import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# Включаем логирование
logging.basicConfig(level=logging.INFO)


# Создаем класс состояний пользователя
class UserState(StatesGroup):
    age = State()  # Состояние для возраста
    growth = State()  # Состояние для роста
    weight = State()  # Состояние для веса


# Инициализируем бот и диспетчер
bot = Bot(token="")
# Добавляем хранилище состояний в диспетчер
dp = Dispatcher(storage=MemoryStorage())


# Хэндлер на команду /start
@dp.message(Command("start"))
async def start(message: types.Message):
    # Создаем клавиатуру с кнопками "Рассчитать" и "Информация"
    kb = ReplyKeyboardBuilder()
    kb.button(text="Рассчитать")
    kb.button(text="Информация")
    kb.adjust(2)
    keyboard = kb.as_markup(resize_keyboard=True)

    await message.answer(
        "Привет! Я бот помогающий твоему здоровью.", reply_markup=keyboard)


# Хэндлер для начала расчета калорий
@dp.message(F.text == "Рассчитать")
async def set_age(message: types.Message, state: FSMContext):
    await message.answer("Введите свой возраст:")
    await state.set_state(UserState.age)


# Хэндлер для получения роста
@dp.message(UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите число.")
        return
    # Сохраняем возраст
    await state.update_data(age=int(message.text))
    # Запрашиваем рост
    await message.answer("Введите свой рост в сантиметрах:")
    await state.set_state(UserState.growth)


# Хэндлер для получения веса
@dp.message(UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите число.")
        return
    # Сохраняем рост
    await state.update_data(growth=int(message.text))
    # Запрашиваем вес
    await message.answer("Введите свой вес в килограммах:")
    await state.set_state(UserState.weight)


# Хэндлер для расчета калорий
@dp.message(UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите число.")
        return
    # Сохраняем вес
    await state.update_data(weight=int(message.text))

    # Получаем все сохраненные данные
    data = await state.get_data()

    # Расчет калорий по формуле Миффлина-Сан Жеора для мужчин
    calories = (10 * data['weight']) + (6.25 * data['growth']) - (5 * data['age']) + 5

    # Отправляем результат
    await message.answer(f"Ваша суточная норма калорий: {calories:.0f} ккал")

    # Завершаем состояние
    await state.clear()


# Хэндлер на все остальные сообщения
@dp.message()
async def all_messages(message: types.Message):
    await message.answer("Введите команду /start, чтобы начать общение.")


# Главная функция
async def main():
    # Запускаем бота
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
