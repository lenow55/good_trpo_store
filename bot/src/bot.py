import asyncio
from typing import final
from typing_extensions import Any
import httpx
import os
import json

from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types.message import Message
from aiogram.filters import Command

# Telegram Bot setup
API_TOKEN = os.getenv("API_TOKEN", "YOUR_TELEGRAM_BOT_API_TOKEN")
API_URL = os.getenv("API_URL", "http://localhost:8000")

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()


@final
class Form(StatesGroup):
    add = State()
    get_by_id = State()


async def fetch_prices(product: str | None = None, seller: str | None = None):
    """Получение списка цен из REST API."""
    params = {}
    if product:
        params["product"] = product
    if seller:
        params["seller"] = seller

    async with httpx.AsyncClient() as session:
        response = await session.get(f"{API_URL}/prices/", params=params)
        if response.status_code != 200:
            return None
        return response.json()


async def fetch_price_by_id(price_id: int):
    """Получение конкретной записи о цене из REST API."""
    async with httpx.AsyncClient() as session:
        response = await session.get(f"{API_URL}/prices/{price_id}")
        if response.status_code != 200:
            return None
        return response.json()


async def add_price(record: dict[str, Any]):
    """Добавление новой записи о цене в REST API."""
    async with httpx.AsyncClient() as session:
        response = await session.post(f"{API_URL}/prices/", json=record)
        if response.status_code != 200:
            if response.status_code == 422:
                raise ValueError(json.dumps(response.json(), indent=2))
            raise Exception
        return response.json()


@router.message(Command("start"))
async def start_command(message: Message):
    """Обработка команды /start."""
    _ = await message.answer(
        "Привет! Я бот для работы с REST API сервера цен.\n"
        "Вы можете использовать следующие команды:\n"
        "/list - получить список цен\n"
        "/add - добавить новую запись о цене\n"
        "/get - получить запись по ID"
    )


@router.message(Command("list"))
async def list_prices(message: Message):
    """Обработка команды /list."""
    prices = await fetch_prices()
    if not prices:
        _ = await message.answer("Нет записей о ценах.")
        return

    response = "\n\n".join(
        f"ID: {price['id']}\nПродукт: {price['product']}\nПродавец: {price['seller']}\nЦена: {price['price']}\nДата: {price['date']}"
        for price in prices
    )
    _ = await message.answer(response)


@router.message(Command("get"))
async def get_price(message: Message):
    """Обработка команды /get."""
    _ = await message.answer("Введите ID записи о цене:")

    @router.message()
    async def handle_price_id(message: Message):
        try:
            if not isinstance(message.text, str):
                raise ValueError
            price_id = int(message.text)
        except ValueError:
            _ = await message.answer("ID должен быть числом. Попробуйте снова.")
            return

        price = await fetch_price_by_id(price_id)
        if not price:
            _ = await message.answer(f"Запись с ID {price_id} не найдена.")
            return

        response = (
            f"ID: {price['id']}\nПродукт: {price['product']}\nПродавец: {price['seller']}\n"
            f"Ссылка: {price['link']}\nЦена: {price['price']}\nДата: {price['date']}"
        )
        _ = await message.answer(response)


@router.message(Command("add"))
async def add_price_command(message: Message, state: FSMContext):
    """Обработка команды /add."""
    _ = await message.answer(
        "Введите данные в формате:\nпродукт\nпродавец\nссылка\nцена\nдата (YYYY-MM-DD)"
    )
    await state.set_state(Form.add)


@router.message(Form.add)
async def handle_price_data(message: Message, state: FSMContext):
    try:
        if not isinstance(message.text, str):
            raise ValueError
        product, seller, link, price, date = message.text.split("\n")
        record = {
            "product": product,
            "seller": seller,
            "link": link,
            "price": float(price),
            "date": date,
        }
    except ValueError as e:
        _ = await message.answer("Неверный формат данных. Попробуйте снова.")
        print(e)
        await state.clear()
        return

    try:
        result = await add_price(record)
        _ = await message.answer(f"Запись добавлена с ID: {result['id']}")

    except ValueError as e:
        _ = await message.answer("Не удалось добавить запись.")
        _ = await message.answer(str(e))
    except Exception:
        _ = await message.answer("Не удалось добавить запись.")
        return
    finally:
        await state.clear()


# Main entry point
if __name__ == "__main__":
    _ = dp.include_router(router)
    asyncio.run(dp.start_polling(bot, skip_updates=True))
