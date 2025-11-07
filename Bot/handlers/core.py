from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from ..keyboards import main_menu_kb
from ..db import players_collection, connect_db
from ..utils import ensure_player

router = Router()

@router.message(commands=["start", "help"])
async def start_handler(message: Message):
    db = await connect_db()
    await ensure_player(db, message.from_user)
    text = (
        "Welcome! This bot offers multiple mini-games:
"
        "- Trivia (single-player)
- Tic-Tac-Toe (1v1)

"
        "Use the buttons below to begin. Good luck!"
    )
    await message.answer(text, reply_markup=main_menu_kb())

@router.callback_query(F.data == "leaderboard")
async def leaderboard_cb(query: CallbackQuery):
    db = await connect_db()
    col = db.players
    docs = await col.find().sort([("stats.wins", -1)]).limit(10).to_list(length=10)
    if not docs:
        await query.message.edit_text("Leaderboard is empty.")
        return
    lines = []
    for i, d in enumerate(docs, start=1):
        name = d.get("username") or d.get("display_name") or str(d["user_id"])
        lines.append(f"{i}. {name} — Wins: {d['stats'].get('wins',0)} — Coins: {d.get('balance',0)}")
    await query.message.edit_text("
".join(lines))
