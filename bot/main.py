import asyncio
import logging
import sys
from os import getenv

import view
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()

TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start(message: Message) -> None:
    await message.answer(
        "Вітаю, я ваш персональний фінансовий помічнк! Якщо ви ще не зареєстровані використайте коману /register, щоб зареєструватися. В іншому випадку вітаємо вас знову з нами"
    )


@dp.message(Command("register"))
async def command_register(message: Message) -> None:
    response = view.registrer_user(
        telegram_id=message.from_user.id, name=message.from_user.username
    )
    if response.status_code == 201:
        await message.answer(
            f"Вітаю @{message.from_user.username}, ви успішно зареєструвалися!"
        )
    elif response.status_code == 409:
        await message.answer("Вибачте, ви вже зареєстрований користувач")
    else:
        await message.answer("Сталася помилка")


@dp.message()
async def echo_handler(message: Message) -> None:
    response = view.make_prompt(user_id=message.from_user.id, prompt=message.text)
    if response.status_code == 401:
        await message.answer(
            "Схоже ви ще не зареєстровані. Щоб зареєструватися використайте команду /register"
        )
    elif response.status_code == 200:
        await message.answer(response.json()["answer"])
    else:
        await message.answer("Сталася помилка")


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
