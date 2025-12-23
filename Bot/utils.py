import secrets
import time


def gen_id(prefix: str = "g") -> str:
    return f"{prefix}_{int(time.time())}_{secrets.token_hex(6)}"


async def ensure_player(db, user) -> dict:
    col = db.players

    user_doc = await col.find_one({"user_id": user.id})
    if user_doc:
        return user_doc

    doc = {
        "user_id": user.id,
        "username": user.username,
        "display_name": f"{user.first_name or ''} {user.last_name or ''}".strip(),
        "balance": 100,
        "stats": {
            "games_played": 0,
            "wins": 0,
            "losses": 0,
            "draws": 0,
        },
        "achievements": [],
        "created_at": time.time(),
    }

    await col.insert_one(doc)
    return doc