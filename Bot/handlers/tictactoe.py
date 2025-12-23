from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton

from ..utils import gen_id
from ..db import connect_db, games_collection, players_collection


router = Router()


WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
]


def render_board(board):
    m = {0: "▫️", 1: "❌", 2: "⭕"}
    rows = []
    for r in range(3):
        rows.append("".join(m[board[3 * r + c]] for c in range(3)))
    return "\n".join(rows)


def board_kb(game_id, board):
    kb = []
    for r in range(3):
        row = []
        for c in range(3):
            i = 3 * r + c
            text = "▫️" if board[i] == 0 else ("❌" if board[i] == 1 else "⭕")
            row.append(
                InlineKeyboardButton(
                    text=text,
                    callback_data=f"ttt_move:{game_id}:{i}",
                )
            )
        kb.append(row)
    return InlineKeyboardMarkup(inline_keyboard=kb)


def check_winner(board):
    for a, b, c in WIN_LINES:
        if board[a] != 0 and board[a] == board[b] == board[c]:
            return board[a]
    if all(x != 0 for x in board):
        return 0
    return None


@router.callback_query(F.data == "play_tictactoe")
async def ttt_offer(query: CallbackQuery):
    await query.message.answer(
        "❌⭕ <b>Tic-Tac-Toe</b>\n\n"
        "🧩 Join queue: <code>/join_ttt</code>\n"
        "⚔️ First two players will be matched automatically"
    )


@router.message(commands=["join_ttt"])
async def join_queue(message: Message):
    db = await connect_db()
    col = db.games

    waiting = await col.find_one({"type": "ttt_waiting"})
    if not waiting or not waiting.get("user"):
        await col.update_one(
            {"type": "ttt_waiting"},
            {"$set": {"type": "ttt_waiting", "user": message.from_user.id}},
            upsert=True,
        )
        await message.answer("⏳ You joined the queue. Waiting for opponent…")
        return

    other = waiting["user"]
    if other == message.from_user.id:
        await message.answer("⚠️ You are already in the queue")
        return

    board = [0] * 9
    game_id = gen_id("ttt")

    await col.insert_one(
        {
            "game_id": game_id,
            "type": "tictactoe",
            "players": [other, message.from_user.id],
            "state": {"board": board, "turn": other},
        }
    )

    await col.delete_one({"type": "ttt_waiting"})

    await message.answer(
        f"🎮 <b>Game Started!</b>\n\n"
        f"{render_board(board)}\n\n"
        f"👉 Turn: <code>{other}</code>",
        reply_markup=board_kb(game_id, board),
    )


@router.callback_query(F.data.startswith("ttt_move:"))
async def ttt_move(query: CallbackQuery):
    _, game_id, pos = query.data.split(":")
    pos = int(pos)

    game = await games_collection().find_one({"game_id": game_id})
    if not game:
        await query.answer("❌ Game not found", show_alert=True)
        return

    board = game["state"]["board"]
    turn = game["state"]["turn"]

    if query.from_user.id != turn:
        await query.answer("⛔ Not your turn", show_alert=True)
        return

    if board[pos] != 0:
        await query.answer("⚠️ Cell already used", show_alert=True)
        return

    mark = 1 if game["players"][0] == turn else 2
    board[pos] = mark

    result = check_winner(board)

    if result is None:
        next_turn = (
            game["players"][1]
            if turn == game["players"][0]
            else game["players"][0]
        )

        await games_collection().update_one(
            {"game_id": game_id},
            {"$set": {"state.board": board, "state.turn": next_turn}},
        )

        await query.message.edit_text(
            f"{render_board(board)}\n\n👉 Turn: <code>{next_turn}</code>",
            reply_markup=board_kb(game_id, board),
        )
        return

    await games_collection().delete_one({"game_id": game_id})

    if result == 0:
        await query.message.edit_text(
            f"{render_board(board)}\n\n🤝 <b>It's a draw!</b>"
        )
        return

    winner = game["players"][0] if result == 1 else game["players"][1]
    loser = game["players"][1] if result == 1 else game["players"][0]

    await players_collection().update_one(
        {"user_id": winner},
        {"$inc": {"stats.wins": 1, "balance": 20}},
        upsert=True,
    )

    await players_collection().update_one(
        {"user_id": loser},
        {"$inc": {"stats.losses": 1}},
        upsert=True,
    )

    await query.message.edit_text(
        f"{render_board(board)}\n\n🏆 <b>Winner:</b> <code>{winner}</code> 🎉"
    )