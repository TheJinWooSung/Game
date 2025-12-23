from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from ..keyboards import main_menu_kb
from ..db import connect_db
from ..utils import ensure_player


router = Router()


@router.message(commands=["start", "help"])
async def start_handler(message: Message):
    db = await connect_db()
    await ensure_player(db, message.from_user)

    text = (
        "👋 <b>Welcome!</b>\n\n"
        "🎮 This bot offers multiple mini-games:\n"
        "• 🧠 Trivia (single-player)\n"
        "• ❌⭕ Tic-Tac-Toe (1v1)\n\n"
        "👇 Use the buttons below to begin.\n"
        "🍀 Good luck!"
    )

    await message.answer(text, reply_markup=main_menu_kb())


@router.callback_query(F.data == "leaderboard")
async def leaderboard_cb(query: CallbackQuery):
    db = await connect_db()
    col = db.players

    docs = (
        await col.find()
        .sort([("stats.wins", -1)])
        .limit(10)
        .to_list(length=10)
    )

    if not docs:
        await query.message.edit_text("📊 Leaderboard is empty.")
        return

    lines = ["🏆 <b>Top Players</b>\n"]

    for i, d in enumerate(docs, start=1):
        name = d.get("username") or d.get("display_name") or str(d["user_id"])
        wins = d.get("stats", {}).get("wins", 0)
        coins = d.get("balance", 0)
        lines.append(f"{i}. {name} — 🏅 {wins} wins — 💰 {coins} coins")

    await query.message.edit_text("\n".join(lines))