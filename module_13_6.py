import os
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import asyncio
api = '!!!!!!!!!'
bot = Bot(token=api)
dp = Dispatcher()
router = Router()
dp.include_router(router)
button_calories = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button_formulas = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
inline_kb = InlineKeyboardMarkup(inline_keyboard=[[button_calories], [button_formulas]])
button_1 = KeyboardButton(text='Рассчитать')
button_2 = KeyboardButton(text='Информация')
kb = ReplyKeyboardMarkup(keyboard=[[button_1], [button_2]], resize_keyboard=True)
class UserState(StatesGroup):
    gender = State()
    age = State()
    growth = State()
    weight = State()
def gender_keyboard():
    buttons_sex = [KeyboardButton(text="Мужчина"), KeyboardButton(text="Женщина")]
    return ReplyKeyboardMarkup(keyboard=[buttons_sex], resize_keyboard=True, one_time_keyboard=True)
def is_valid_number(value):
    return value.isdigit() and int(value) > 0
@dp.message(Command("start")) #
async def start_form(message: Message):
    await message.answer("Привет! Я бот, помогающий твоему здоровью. Если хочешь узнать свою суточную норму "
                         "калорий, то нажми 'Рассчитать'.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Рассчитать', callback_data='main_menu')]]))
@router.callback_query(F.data == 'main_menu')
async def main_menu(call: CallbackQuery):
    await call.message.answer("Выберите опцию:", reply_markup=inline_kb)
@router.callback_query(F.data == 'formulas')
async def get_formulas(call: CallbackQuery):
    formula_text = ("Формула Миффлина-Сан Жеора:\n"
                    "Для мужчин: 10 * вес (кг) + 6.25 * рост (см) - 5 * возраст (лет) + 5\n"
                    "Для женщин: 10 * вес (кг) + 6.25 * рост (см) - 5 * возраст (лет) - 161")
    await call.message.answer(formula_text)
@router.callback_query(F.data == 'calories') 
async def set_gender(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Выберите ваш пол:", reply_markup=gender_keyboard())
    await state.set_state(UserState.gender)
@router.message(UserState.gender)
async def set_age(message: types.Message, state: FSMContext):
    gender = message.text.lower()
    if gender not in ["мужчина", "женщина"]:
        await message.answer("Пожалуйста, выберите пол, используя кнопки ниже.")
        return
    await state.update_data(gender=gender)
    await message.answer("Введите свой возраст:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(UserState.age)
@router.message(UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    if is_valid_number(message.text):
        await state.update_data(age=int(message.text))
        await message.answer("Введите свой рост (в см):")
        await state.set_state(UserState.growth)
    else:
        await message.answer("Возраст должен быть положительным числом. Пожалуйста, введите корректное значение.")
@router.message(UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    if is_valid_number(message.text):
        await state.update_data(growth=int(message.text))
        await message.answer("Введите свой вес (в кг):")
        await state.set_state(UserState.weight)  #
    else:
        await message.answer("Рост должен быть положительным числом. Пожалуйста, введите корректное значение.")
@router.message(UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    if is_valid_number(message.text):
        await state.update_data(weight=int(message.text))
        data = await state.get_data()
        gender = data['gender']
        age = data['age']
        growth = data['growth']
        weight = data['weight']
        if gender == "мужчина":
            calories = 10 * weight + 6.25 * growth - 5 * age + 5
        else:
            calories = 10 * weight + 6.25 * growth - 5 * age - 161
        await message.answer(f"Ваша норма калорий: {calories:.2f} ккал в день.")
        await state.clear()
    else:
        await message.answer("Вес должен быть положительным числом. Пожалуйста, введите корректное значение.")
@router.message(~F.text.lower('Рассчитать') and ~F.state(UserState.age) and ~F.state(UserState.growth)
                and ~F.state(UserState.weight))
async def redirect_to_start(message: types.Message):
    await start_form(message)
async def main():
    await dp.start_polling(bot)
if __name__ == '__main__':
    asyncio.run(main())