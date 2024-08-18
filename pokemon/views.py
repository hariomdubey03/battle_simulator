import logging
import uuid
from typing import List, Optional, Union

from celery import shared_task
from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.versioning import NamespaceVersioning
from rest_framework.views import APIView
from sqlalchemy import case

from battle_simulator.utils import custom_exceptions as ce
from battle_simulator.utils.custom_validator import CustomValidator
from battle_simulator.utils.data_formatter import (
    result_list_to_dict,
    result_row_to_dict,
)
from pokemon.models import Battle, Pokemon
from pokemon.spell_checker import spell_checker

# Get an instance of logger
logger = logging.getLogger("pokemon")

# Get an instance of Custom Validator
c_validator = CustomValidator({}, allow_unknown=True)

# Create DB Session
session = settings.DB_SESSION


class VersioningConfig(NamespaceVersioning):
    default_version = "v1"
    allowed_versions = ["v1"]
    version_param = "version"


class PokemonAPIView(APIView):
    """
    Handles retrieving and listing Pokemon data with pagination.
    """

    versioning_class = VersioningConfig
    permission_classes = (AllowAny,)

    def get(self, request):
        """
        Method: GET
        Retrieves a paginated list of Pokemon or details of a specific Pokemon by name.
        -------
        Query Parameters:
        name (str): Name of the Pokemon (optional).
        page (int): Page number for pagination (optional).
        limit (int): Limit of items per page (optional).

        Returns:
        json: A list of Pokemon or a single Pokemon if the name is provided.
        """
        try:
            # Handling pagination
            page = int(request.query_params.get("page", 1))
            limit = int(request.query_params.get("limit", 10))
            offset = (page - 1) * limit

            # Filter Pokemon by name if provided
            pokemon_name = request.query_params.get("name")
            pokemon = query_pokemon(
                name=pokemon_name, limit=limit + 1, offset=offset
            )

            has_prev = False if page == 1 else True
            has_next = (
                True if pokemon and len(pokemon) > limit else False
            )

            return Response(
                {
                    "page": page,
                    "has_next": has_next,
                    "has_prev": has_prev,
                    "data": (pokemon[:limit] if pokemon else None),
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(f"POKEMON API VIEW - GET : {e}")
            raise ce.InternalServerError


class BattleAPIView(APIView):
    """
    Handles pokemon related to Pokemon battles.
    """

    versioning_class = VersioningConfig
    permission_classes = (AllowAny,)

    def get(self, request, battle_id):
        """
        Method: GET
        Retrieves the status of a battle by its battle ID.
        -------
        Query Parameters:
        battle_id (UUID): Unique identifier of the battle.

        Returns:
        json: Status of the battle (BATTLE_INPROGRESS, BATTLE_COMPLETED, BATTLE_FAILED).
        """
        try:

            # Fetch the battle record
            battle = get_battle_status(battle_id)

            if not battle:
                raise ce.NotFound({"message": "Battle not found"})

            return Response({"data": battle}, status=status.HTTP_200_OK)

        except ce.ValidationFailed as vf:
            logger.error(f"BATTLE API VIEW - GET : {vf}")
            raise
        except ce.NotFound as nf:
            logger.error(f"BATTLE API VIEW - GET : {nf}")
            raise
        except Exception as e:
            logger.error(f"BATTLE API VIEW - GET : {e}")
            raise ce.InternalServerError

    def post(self, request):
        """
        Method: POST
        Initiates a new battle between two Pokemon.
        -------
        Request Data:
        - pokemon_a (str): Name of Pokemon A.
        - pokemon_b (str): Name of Pokemon B.

        Returns:
        json: UUID battle ID to track the battle status.
        """
        try:
            data = request.data
            pokemon_a = data.get("pokemon_a")
            pokemon_b = data.get("pokemon_b")

            # Validate input Pokemon names
            if not pokemon_a or not pokemon_b:
                raise ce.ValidationFailed(
                    {
                        "message": "Both pokemon_a and pokemon_b are required"
                    }
                )

            pokemon_a = spell_checker.check_spelling(pokemon_a)
            pokemon_b = spell_checker.check_spelling(pokemon_b)

            if not query_pokemon(pokemon_a) or not query_pokemon(
                pokemon_b
            ):
                raise ce.NotFound(
                    {"message": "One or both Pokemon not found"}
                )

            battle_id = uuid.uuid4()
            insert_battle(
                battle_id=battle_id,
                pokemon_a=pokemon_a,
                pokemon_b=pokemon_b,
                status="BATTLE_INPROGRESS",
            )

            # Initiate battle in the background (asynchronous task)
            battle = perform_battle_task.apply_async(
                kwargs={
                    "battle_id": battle_id,
                    "pokemon_a": pokemon_a,
                    "pokemon_b": pokemon_b,
                }
            )

            if not battle:
                return Response(
                    {"message": "Failed to create Battle"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {"battle_id": battle_id},
                status=status.HTTP_202_ACCEPTED,
            )
        except ce.InvalidPokemon as ip:
            logger.error(f"BATTLE API VIEW - POST : {ip}")
            raise
        except ce.ValidationFailed as vf:
            logger.error(f"BATTLE API VIEW - POST : {vf}")
            raise
        except ce.NotFound as nf:
            logger.error(f"BATTLE API VIEW - POST : {nf}")
            raise
        except Exception as e:
            logger.error(f"BATTLE API VIEW - POST : {e}")
            raise ce.InternalServerError


def get_battle_status(battle_id: uuid.UUID) -> Union[dict, None]:
    """
    Retrieves the current status of a battle based on its battle ID.

    Parameters:
    battle_id (UUID): Unique identifier for the battle.

    Returns:
    Union[dict, None]: A dictionary containing the battle status and results, or None if the battle isn't found.
    """
    try:
        battle = fetch_battle_by_id(battle_id)

        if not battle:
            raise ValueError("Battle not found.")

        if battle["status"] == "BATTLE_INPROGRESS":
            return {"status": "BATTLE_INPROGRESS", "result": None}
        elif battle["status"] == "BATTLE_COMPLETED":
            return {
                "status": "BATTLE_COMPLETED",
                "result": {
                    "winnerName": battle["winner_name"],
                    "wonByMargin": battle["won_by_margin"],
                },
            }
        elif battle.status == "BATTLE_FAILED":
            return {"status": "BATTLE_FAILED", "result": None}

    except Exception as e:
        logger.error(f"GET BATTLE STATUS : {e}")
        return None


def insert_battle(
    battle_id: uuid.UUID,
    pokemon_a: str,
    pokemon_b: str,
    status: str,
    winner_name: Optional[str] = None,
    won_by_margin: Optional[float] = None,
) -> Optional[Battle]:
    """
    Insert a new battle into the database.

    Parameters:
    pokemon_a (str): The name of the first Pokemon.
    pokemon_b (str): The name of the second Pokemon.
    status (str): The status of the battle (e.g., BATTLE_INPROGRESS, BATTLE_COMPLETED).
    winner_name (Optional[str]): The name of the winning Pokemon, if any.
    won_by_margin (Optional[float]): The margin by which the Pokemon won, if applicable.

    Returns:
    Optional[Battle]: The created Battle object or None if the creation failed.
    """
    try:
        battle = Battle(
            battle_id=battle_id,
            pokemon_a=pokemon_a,
            pokemon_b=pokemon_b,
            status=status,
            winner_name=winner_name,
            won_by_margin=won_by_margin,
        )
        session.add(battle)
        session.commit()

    except Exception as e:
        logger.error("INSERT BATTLE: {}".format(e))
        session.rollback()
        battle = None

    return battle


def query_pokemon(
    name: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> Union[List[dict], None]:
    """
    Query Pokemon data based on filters like name, type1, and type2.

    Parameters:
    name (Optional[str]): The name of the Pokemon to filter by.
    type1 (Optional[str]): The primary type to filter Pokemon.
    type2 (Optional[str]): The secondary type to filter Pokemon.
    limit (Optional[int]): The maximum number of records to return.
    offset (Optional[int]): The number of records to skip before starting to return results.

    Returns:
    Union[List[dict], None]: A list of Pokemon matching the query or None if no Pokemon are found.
    """
    try:
        query = session.query(
            Pokemon.name,
            Pokemon.type1,
            Pokemon.type2,
            Pokemon.attack,
            Pokemon.hp,
            case(
                [(Pokemon.is_legendary == 1, "Legendary")],
                else_="Normal",
            ).label("Category"),
        ).order_by(Pokemon.is_legendary.desc(), Pokemon.attack.desc())

        if name:
            query = query.filter(Pokemon.name.contains(name))

        if offset is not None and limit is not None:
            query = query.limit(limit).offset(offset)

        pokemon = query.all()

        session.commit()

        pokemon = result_list_to_dict(pokemon) if pokemon else None

    except Exception as e:
        logger.error(f"QUERY POKEMON: {e}")
        pokemon = None

    return pokemon


def fetch_battle_by_id(battle_id: uuid.UUID) -> Optional[dict]:
    """
    Retrieve the details of a battle based on its battle ID.

    This function queries the database to find the battle record with the specified battle ID.

    Returns:
    Optional[dict]: A dictionary containing battle details if a matching record is found; otherwise, None.
    """
    try:
        query = (
            session.query(
                Battle.battle_id,
                Battle.pokemon_a,
                Battle.pokemon_b,
                Battle.status,
                Battle.winner_name,
                Battle.won_by_margin,
            )
            .filter(Battle.battle_id == battle_id)
            .first()
        )

        session.commit()

        battle_details = result_row_to_dict(query) if query else None

    except Exception as e:
        logger.error(f"FETCH BATTLE BY ID: {e}")
        battle_details = None

    return battle_details


def get_pokemon_data(name: str):
    """Fetch Pokemon data from the database."""
    try:
        return (
            session.query(Pokemon)
            .filter(Pokemon.name == name)
            .one_or_none()
        )
    except Exception as e:
        logger.error(f"Error fetching Pokemon data for {name}: {e}")
        return None


def update_battle(
    battle_id: str,
    status: Optional[str] = None,
    winner_name: Optional[str] = None,
    won_by_margin: Optional[float] = None,
) -> Optional[Battle]:
    """
    Update details of a battle in the database.

    Parameters:
    battle_id (str): The unique ID of the battle to update.
    status (Optional[str]): The new status of the battle (e.g., BATTLE_INPROGRESS, BATTLE_COMPLETED).
    winner_name (Optional[str]): The new winner's name, if applicable.
    won_by_margin (Optional[float]): The new margin by which the Pokemon won, if applicable.

    Returns:
    Optional[Battle]: The updated Battle object or None if the update failed.
    """
    try:
        update_data = {}
        if status is not None:
            update_data["status"] = status
        if winner_name is not None:
            update_data["winner_name"] = winner_name
        if won_by_margin is not None:
            update_data["won_by_margin"] = won_by_margin

        # Update the battle record
        updated_record = (
            session.query(Battle)
            .filter(Battle.battle_id == battle_id)
            .update(update_data)
        )

        session.commit()

    except Exception as e:
        logger.error("UPDATE BATTLE ERROR: {}".format(e))
        session.rollback()
        updated_record = 0

    return updated_record


@shared_task(bind=True, queue="perform_battle_queue")
def perform_battle_task(self, **kwargs) -> Optional[Battle]:
    """
    Perform a battle between two Pokemon and update the Battle table.

    Parameters:
    battle_id (uuid): The unique battle perform id.
    pokemon_a (str): The name of the first Pokemon.
    pokemon_b (str): The name of the second Pokemon.

    Returns:
    Optional[Battle]: The updated Battle object or None if the operation failed.
    """

    try:
        battle_id = kwargs.get("battle_id")
        pokemon_a = kwargs.get("pokemon_a")
        pokemon_b = kwargs.get("pokemon_b")

        # Fetch Pokemon data
        poke_a = get_pokemon_data(pokemon_a)
        poke_b = get_pokemon_data(pokemon_b)

        if not poke_a or not poke_b:
            raise ValueError(
                "One or both Pokemon not found in the database."
            )

        # Extract required data
        type1_a, type2_a, attack_a = (
            poke_a.type1,
            poke_a.type2,
            poke_a.attack,
        )
        type1_b, type2_b, attack_b = (
            poke_b.type1,
            poke_b.type2,
            poke_b.attack,
        )

        against_type1_b = getattr(poke_b, f"against_{type1_a}", 1)
        against_type2_b = getattr(poke_b, f"against_{type2_a}", 1)
        damage_a = (attack_a / 200) * 100 - (
            ((against_type1_b / 4) * 100)
            + ((against_type2_b / 4) * 100)
        )

        against_type1_a = getattr(poke_a, f"against_{type1_b}", 1)
        against_type2_a = getattr(poke_a, f"against_{type2_b}", 1)
        damage_b = (attack_b / 200) * 100 - (
            ((against_type1_a / 4) * 100)
            + ((against_type2_a / 4) * 100)
        )

        # Determine the winner
        winner_name = None
        won_by_margin = None
        if damage_a > damage_b:
            winner_name = pokemon_a
            won_by_margin = damage_a - damage_b
        elif damage_b > damage_a:
            winner_name = pokemon_b
            won_by_margin = damage_b - damage_a
        else:
            # If it's a draw
            winner_name = None
            won_by_margin = 0

        # Create or update the Battle record
        update_battle(
            battle_id=battle_id,
            status="BATTLE_COMPLETED" if winner_name else "DRAW",
            winner_name=winner_name,
            won_by_margin=won_by_margin,
        )

    except ValueError as e:
        logger.error("PERFORM BATTLE: {}".format(e))
        update_battle(battle_id=battle_id, status="BATTLE_FAILED")
        return None
    except Exception as e:
        logger.error("PERFORM BATTLE: {}".format(e))
        update_battle(battle_id=battle_id, status="BATTLE_FAILED")
        return None
