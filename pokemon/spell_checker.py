import difflib
import logging
from typing import List
from django.conf import settings

from pokemon.models import Pokemon
from battle_simulator.utils import custom_exceptions as ce

# Get an instance of logger
logger = logging.getLogger("pokemon")

# Create DB Session
session = settings.DB_SESSION


class PokemonSpellChecker:
    def __init__(self):
        self.valid_pokemon_names = [
            each.lower() for each in fetch_pokemon_names()
        ]

    def normalize_name(self, name):
        """Normalize the Pokémon name by converting it to lowercase."""
        return name.lower().strip()

    def check_spelling(self, input_name):
        """Check for spelling mistakes in the Pokémon name."""
        normalized_input = self.normalize_name(input_name)
        close_matches = difflib.get_close_matches(
            normalized_input, self.valid_pokemon_names, n=1, cutoff=0.8
        )

        if not close_matches:
            raise ce.InvalidPokemon(
                f"Pokémon name '{input_name}' is not recognized."
            )

        closest_name = close_matches[0]
        if normalized_input == closest_name:
            return closest_name
        else:
            # Check if the input name is a close match within the threshold
            if (
                difflib.SequenceMatcher(
                    None, normalized_input, closest_name
                ).ratio()
                >= 0.8
            ):
                return closest_name
            else:
                raise ce.InvalidPokemon(
                    f"Pokémon name '{input_name}' is not recognized."
                )


def fetch_pokemon_names() -> List:
    try:
        # Start building the query for Pokémon data
        query = session.query(Pokemon.name).all()

        # Commit session and process results
        session.commit()

        # Convert result to list of dicts
        pokemons = [each.name for each in query] if query else None

    except Exception as e:
        logger.error(f"FETCH POKEMON NAMES: {e}")
        pokemons = None

    return pokemons


spell_checker = PokemonSpellChecker()
