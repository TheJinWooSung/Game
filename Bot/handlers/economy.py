from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from ..db import connect_db
from ..keyboards import confirm_kb


router = Router()


@router.callback_query(F.data == "shop")
async def shop_cb(query: CallbackQuery):
    text = (
        "🛒 <b>Shop</b>\n\n"
        "1️⃣ <b>Cool Title</b>\n"
        "💰 Price: 50 coins\n"
        "🏷️ Unlock a special title\n\n"
        "👉 Use <code>/buy title</code> to purchase"
    )
    await query.message.answer(text)


@router.message(commands=["buy"])
async def buy_cmd(message: Message):
    db = await connect_db()

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply("❌ Usage: <code>/buy title</code>")
        return

    item = parts[1].strip().lower()

    if item != "title":
        await message.reply("❓ Unknown item")
        return

    player = await db.players.find_one({"user_id": message.from_user.id})
    if not player or player.get("balance", 0) < 50:
        await message.reply("💸 Not enough coins")
        return

    await db.players.update_one(
        {"user_id": message.from_user.id},
        {
            "$inc": {"balance": -50},
            "$addToSet": {"achievements": "Title: Cool Player"},
        },
    )

    await message.reply("✅ Purchased: 🏷️ <b>Cool Player</b>")