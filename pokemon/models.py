# coding: utf-8
from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    TIMESTAMP,
    Text,
    text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Pokemon(Base):
    __tablename__ = "pokemon"

    name = Column(String(100), primary_key=True)
    abilities = Column(Text)
    against_bug = Column(Float)
    against_dark = Column(Float)
    against_dragon = Column(Float)
    against_electric = Column(Float)
    against_fairy = Column(Float)
    against_fight = Column(Float)
    against_fire = Column(Float)
    against_flying = Column(Float)
    against_ghost = Column(Float)
    against_grass = Column(Float)
    against_ground = Column(Float)
    against_ice = Column(Float)
    against_normal = Column(Float)
    against_poison = Column(Float)
    against_psychic = Column(Float)
    against_rock = Column(Float)
    against_steel = Column(Float)
    against_water = Column(Float)
    attack = Column(Integer)
    base_egg_steps = Column(Integer)
    base_happiness = Column(Integer)
    base_total = Column(Integer)
    capture_rate = Column(Integer)
    classfication = Column(Text)
    defense = Column(Integer)
    experience_growth = Column(Integer)
    height_m = Column(Float)
    hp = Column(Integer)
    japanese_name = Column(String(100))
    percentage_male = Column(Float)
    pokedex_number = Column(Integer)
    sp_attack = Column(Integer)
    sp_defense = Column(Integer)
    speed = Column(Integer)
    type1 = Column(String(50))
    type2 = Column(String(50))
    weight_kg = Column(Float)
    generation = Column(Integer)
    is_legendary = Column(Integer)


class Battle(Base):
    __tablename__ = "battle"

    battle_id = Column(
        String(36), primary_key=True, server_default=text("(uuid())")
    )
    pokemon_a = Column(ForeignKey("pokemon.name"), index=True)
    pokemon_b = Column(ForeignKey("pokemon.name"), index=True)
    status = Column(String(50))
    winner_name = Column(String(100))
    won_by_margin = Column(Float)
    created_at = Column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at = Column(
        TIMESTAMP,
        server_default=text(
            "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
        ),
    )

    pokemon = relationship(
        "Pokemon", primaryjoin="Battle.pokemon_a == Pokemon.name"
    )
    pokemon1 = relationship(
        "Pokemon", primaryjoin="Battle.pokemon_b == Pokemon.name"
    )
