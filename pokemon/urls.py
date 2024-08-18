from django.urls import path
from pokemon.views import PokemonAPIView, BattleAPIView


urlpatterns = [
    path(
        "list",
        PokemonAPIView.as_view(),
        name="pokemon-list",
    ),
    path(
        "battle",
        BattleAPIView.as_view(),
        name="perform-battle",
    ),
    path(
        "battle/<str:battle_id>",
        BattleAPIView.as_view(),
        name="battle-status",
    ),
]
