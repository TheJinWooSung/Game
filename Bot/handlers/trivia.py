from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from ..utils import gen_id
from ..db import games_collection, players_collection, connect_db
import random
import os
import json

router = Router()

BASE_DIR = os.path.dirname(__file__)
QPATH = os.path.join(BASE_DIR, '..', 'static', 'sample_questions.json')
with open(QPATH, 'r', encoding='utf8') as f:
    SAMPLE_QS = json.load(f)

@router.callback_query(F.data == "play_trivia")
async def trivia_start(query: CallbackQuery):
    db = await connect_db()
    await players_collection().database.players.update_one({"user_id": query.from_user.id}, {"$inc": {"stats.games_played": 1}}, upsert=True)
    q = random.choice(SAMPLE_QS)
    game_id = gen_id('trivia')
    game_doc = {
        "game_id": game_id,
        "type": "trivia",
        "players": [query.from_user.id],
        "state": {"question": q['question'], "choices": q['choices'], "answer": q['answer']},
    }
    await games_collection().insert_one(game_doc)
    ikb = InlineKeyboardMarkup()
    for idx, choice in enumerate(q['choices']):
        ikb.add(InlineKeyboardButton(choice, callback_data=f"trivia_ans:{game_id}:{idx}"))
    await query.message.answer(f"🎯 Trivia: {q['question']}", reply_markup=ikb)

@router.callback_query(F.data.startswith("trivia_ans:"))
async def trivia_answer(query: CallbackQuery):
    parts = query.data.split(":")
    game_id = parts[1]
    idx = int(parts[2])
    g = await games_collection().find_one({"game_id": game_id})
    if not g:
        await query.answer("Game expired.")
        return
    correct = g['state']['answer']
    if idx == correct:
        await query.message.answer("✅ Correct! You win 10 coins.")
        await players_collection().update_one({"user_id": query.from_user.id}, {"$inc": {"balance": 10, "stats.wins": 1}}, upsert=True)
    else:
        await query.message.answer("❌ Wrong. Better luck next time.")
        await players_collection().update_one({"user_id": query.from_user.id}, {"$inc": {"stats.losses": 1}}, upsert=True)
    await games_collection().delete_one({"game_id": game_id})
