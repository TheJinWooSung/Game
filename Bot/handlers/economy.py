from aiogram import Router, F
from aiogram.types import CallbackQuery
from ..db import players_collection, connect_db
from ..keyboards import confirm_kb

router = Router()

@router.callback_query(F.data == "shop")
async def shop_cb(query: CallbackQuery):
    text = "Shop:
1) 50 coins — Unlock cool title (use /buy title)"
    await query.message.answer(text)

@router.message(commands=["buy"])
async def buy_cmd(message):
    db = await connect_db()
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply("Usage: /buy <item>")
        return
    item = parts[1].strip().lower()
    if item == "title":
        res = await db.players.find_one({"user_id": message.from_user.id})
        if not res or res.get('balance', 0) < 50:
            await message.reply("Not enough coins.")
            return
        await db.players.update_one({"user_id": message.from_user.id}, {"$inc": {"balance": -50}, "$push": {"achievements": "Title:Cool Player"}})
        await message.reply("Purchased: Title - Cool Player")
    else:
        await message.reply("Unknown item")
