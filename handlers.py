from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import Debtor, SessionLocal
from datetime import datetime
from keyboard import get_debtors_keyboard, get_actions_keyboard  # Импортируем клавиатуры

router = Router()

# Состояния для добавления долга
class AddDebt(StatesGroup):
    name = State()
    phone = State()
    amount = State()

# Обработчик команды /start
@router.message(Command("start"))
async def start(message: Message):
    await message.answer("Привет! Я бот для учета долгов. Используй /add для добавления записи.")

# Обработчик команды /add
@router.message(Command("add"))
async def add_debt(message: Message, state: FSMContext):
    await state.set_state(AddDebt.name)
    await message.answer("Введите имя должника:")

# Обработчик состояния AddDebt.name
@router.message(AddDebt.name)
async def enter_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddDebt.phone)
    await message.answer("Введите номер телефона должника:")

# Обработчик состояния AddDebt.phone
@router.message(AddDebt.phone)
async def enter_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(AddDebt.amount)
    await message.answer("Введите сумму долга:")

# Обработчик состояния AddDebt.amount
@router.message(AddDebt.amount)
async def enter_amount(message: Message, state: FSMContext):
    try:
        amount = int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите корректную сумму цифрами.")
        return

    data = await state.get_data()
    name = data["name"]
    phone = data["phone"]

    db = SessionLocal()
    new_debtor = Debtor(name=name, phone=phone, amount=amount, date=datetime.utcnow())
    db.add(new_debtor)
    db.commit()
    db.close()

    await state.clear()
    await message.answer(f"✅ Запись добавлена!\n👤 Имя: {name}\n📞 Телефон: {phone}\n💰 Сумма: {amount}")

# Обработчик команды /list
@router.message(Command("list"))
async def list_debts(message: Message):
    db = SessionLocal()
    debtors = db.query(Debtor).order_by(Debtor.date.desc()).all()
    db.close()

    if not debtors:
        await message.answer("❌ Нет записей о должниках.")
        return

    # Получаем клавиатуру с должниками
    keyboard = get_debtors_keyboard(debtors)
    await message.answer("📜 Список должников:", reply_markup=keyboard)

# Обработчик выбора должника
@router.callback_query(F.data.startswith("select_"))
async def select_debtor(callback: CallbackQuery):
    debtor_id = int(callback.data.split("_")[1])

    # Получаем клавиатуру с действиями для выбранного должника
    keyboard = get_actions_keyboard(debtor_id)
    await callback.message.answer("Выберите действие:", reply_markup=keyboard)
    await callback.answer()

# Обработчик увеличения долга
@router.callback_query(F.data.startswith("increase_"))
async def increase_debt(callback: CallbackQuery, state: FSMContext):
    debtor_id = int(callback.data.split("_")[1])
    await state.update_data(debtor_id=debtor_id)
    await state.set_state("enter_increase_amount")
    await callback.message.answer("Введите сумму, на которую нужно увеличить долг:")
    await callback.answer()

# Обработчик уменьшения долга
@router.callback_query(F.data.startswith("decrease_"))
async def decrease_debt(callback: CallbackQuery, state: FSMContext):
    debtor_id = int(callback.data.split("_")[1])
    await state.update_data(debtor_id=debtor_id)
    await state.set_state("enter_decrease_amount")
    await callback.message.answer("Введите сумму, на которую нужно уменьшить долг:")
    await callback.answer()

# Обработчик удаления записи
@router.callback_query(F.data.startswith("delete_"))
async def delete_debt(callback: CallbackQuery):
    debtor_id = int(callback.data.split("_")[1])

    db = SessionLocal()
    debtor = db.query(Debtor).filter(Debtor.id == debtor_id).first()
    if debtor:
        db.delete(debtor)
        db.commit()
        await callback.message.answer(f"✅ Запись о {debtor.name} удалена.")
    else:
        await callback.message.answer("❌ Запись не найдена.")
    db.close()

    await callback.answer()

# Обработчик ввода суммы для увеличения долга
@router.message(state="enter_increase_amount")
async def enter_increase_amount(message: Message, state: FSMContext):
    try:
        amount = int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите корректную сумму цифрами.")
        return

    data = await state.get_data()
    debtor_id = data["debtor_id"]

    db = SessionLocal()
    debtor = db.query(Debtor).filter(Debtor.id == debtor_id).first()
    if debtor:
        debtor.amount += amount
        db.commit()
        await message.answer(f"✅ Долг {debtor.name} увеличен на {amount} руб. Новый долг: {debtor.amount} руб.")
    else:
        await message.answer("❌ Запись не найдена.")
    db.close()

    await state.clear()

# Обработчик ввода суммы для уменьшения долга
@router.message(state="enter_decrease_amount")
async def enter_decrease_amount(message: Message, state: FSMContext):
    try:
        amount = int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите корректную сумму цифрами.")
        return

    data = await state.get_data()
    debtor_id = data["debtor_id"]

    db = SessionLocal()
    debtor = db.query(Debtor).filter(Debtor.id == debtor_id).first()
    if debtor:
        debtor.amount -= amount
        db.commit()
        await message.answer(f"✅ Долг {debtor.name} уменьшен на {amount} руб. Новый долг: {debtor.amount} руб.")
    else:
        await message.answer("❌ Запись не найдена.")
    db.close()

    await state.clear()