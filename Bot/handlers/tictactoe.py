from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from ..utils import gen_id
from ..db import games_collection, players_collection, connect_db

router = Router()

WIN_LINES = [
    (0,1,2),(3,4,5),(6,7,8),
    (0,3,6),(1,4,7),(2,5,8),
    (0,4,8),(2,4,6)
]

def render_board(board):
    mapping = {0: "▫️", 1: "❌", 2: "⭕"}
    rows = []
    for r in range(3):
        rows.append(''.join(mapping[board[3*r + c]] for c in range(3)))
    return "
".join(rows)

def check_winner(board):
    for a,b,c in WIN_LINES:
        if board[a] != 0 and board[a] == board[b] == board[c]:
            return board[a]
    if all(x != 0 for x in board):
        return 0  # draw
    return None

@router.callback_query(F.data == "play_tictactoe")
async def ttt_offer(query: CallbackQuery):
    await query.message.answer("🔔 Tic-Tac-Toe: Join queue with /join_ttt or challenge with /ttt <user_id>")

@router.message(commands=["join_ttt"])
async def join_queue(message):
    db = await connect_db()
    col = db.games
    waiting = await col.find_one({"type": "ttt_waiting"})
    if not waiting or not waiting.get('user'):
        await col.update_one({"type": "ttt_waiting"}, {"$set": {"type": "ttt_waiting", "user": message.from_user.id}}, upsert=True)
        await message.answer("You joined the queue. Waiting for another player...")
        return
    other = waiting['user']
    if other == message.from_user.id:
        await message.answer("You're already waiting.")
        return
    board = [0]*9
    game_id = gen_id('ttt')
    game_doc = {"game_id": game_id, "type": "tictactoe", "players": [other, message.from_user.id], "state": {"board": board, "turn": other}}
    await col.insert_one(game_doc)
    await col.delete_one({"type": "ttt_waiting"})
    await message.answer(f"Game started! ID: {game_id}
{render_board(board)}
It's {other}'s turn.")

@router.callback_query(F.data.startswith("ttt_move:"))
async def ttt_move(query: CallbackQuery):
    parts = query.data.split(":")
    game_id = parts[1]
    pos = int(parts[2])
    g = await games_collection().find_one({"game_id": game_id})
    if not g:
        await query.answer("Game not found")
        return
    board = g['state']['board']
    turn = g['state']['turn']
    if query.from_user.id != turn:
        await query.answer("Not your turn", show_alert=True)
        return
    if board[pos] != 0:
        await query.answer("Cell taken", show_alert=True)
        return
    mark = 1 if g['players'][0] == turn else 2
    board[pos] = mark
    winner = check_winner(board)
    if winner is None:
        # continue
        next_turn = g['players'][0] if turn == g['players'][1] else g['players'][1]
        await games_collection().update_one({"game_id": game_id}, {"$set": {"state.board": board, "state.turn": next_turn}})
        await query.message.edit_text(f"{render_board(board)}
Next: {next_turn}")
        return
    # game finished
    if winner == 0:
        # draw
        await query.message.edit_text(f"{render_board(board)}
It's a draw!")
        await games_collection().delete_one({"game_id": game_id})
        return
    # a player won
    winner_user = g['players'][0] if winner == 1 else g['players'][1]
    await query.message.edit_text(f"{render_board(board)}
Player {winner_user} wins! 🎉")
    # update stats
    await players_collection().update_one({"user_id": winner_user}, {"$inc": {"stats.wins": 1, "balance": 20}}, upsert=True)
    loser_user = g['players'][1] if winner == 1 else g['players'][0]
    await players_collection().update_one({"user_id": loser_user}, {"$inc": {"stats.losses": 1}}, upsert=True)
    await games_collection().delete_one({"game_id": game_id})
