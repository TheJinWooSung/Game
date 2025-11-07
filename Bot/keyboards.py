from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🎲 Play Trivia", callback_data="play_trivia"),
        InlineKeyboardButton("♟️ Tic-Tac-Toe", callback_data="play_tictactoe"),
    )
    kb.add(
        InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard"),
        InlineKeyboardButton("💰 Shop", callback_data="shop"),
    )
    return kb

def confirm_kb(action: str):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton("Yes", callback_data=f"confirm:{action}"),
        InlineKeyboardButton("No", callback_data=f"cancel:{action}"),
    ]])
