from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Клавиатура для списка должников
def get_debtors_keyboard(debtors):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for debtor in debtors:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"{debtor.name} - {debtor.amount} руб.",
                callback_data=f"select_{debtor.id}"
            )
        ])
    return keyboard

# Клавиатура для действий с должником
def get_actions_keyboard(debtor_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Увеличить долг", callback_data=f"increase_{debtor_id}"),
            InlineKeyboardButton(text="➖ Уменьшить долг", callback_data=f"decrease_{debtor_id}"),
        ],
        [
            InlineKeyboardButton(text="❌ Удалить запись", callback_data=f"delete_{debtor_id}"),
        ]
    ])