from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class Player(BaseModel):
    user_id: int
    username: Optional[str]
    display_name: Optional[str]
    balance: int = 0
    stats: Dict[str, int] = Field(
        default_factory=lambda: {
            "games_played": 0,
            "wins": 0,
            "losses": 0,
            "draws": 0,
        }
    )
    achievements: List[str] = Field(default_factory=list)


class GameState(BaseModel):
    game_id: str
    type: str
    players: List[int]
    state: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[float]