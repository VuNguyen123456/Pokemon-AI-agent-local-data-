from pydantic import BaseModel
from typing import List, Optional, Dict

class TeamPokemon(BaseModel):
    species: str
    gender: Optional[str] = None
    item: Optional[str] = None
    ability: Optional[str] = None
    evs: Optional[Dict[str, int]] = None
    ivs: Optional[Dict[str, int]] = None
    nature: Optional[str] = None
    moves: Optional[List[str]] = []


class TeamSearchResult(BaseModel):
    file: str
    team_name: str
    author: str
    team: List[TeamPokemon]
    pokemonShowdownExport: Optional[str] = None

class AllTeamSearchResult(BaseModel):
    teams: List[TeamSearchResult]