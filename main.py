
import logging
import os
import aiohttp
from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN")
USDT_ADDRESS = os.getenv("USDT_ADDRESS")
PDF_PATH = "pdf/guide.pdf"
CHECK_API_URL = f"https://apilist.tronscanapi.com/api/transaction?sort=-timestamp&count=true&limit=20&start=0&address={USDT_ADDRESS}"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)

@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    await message.reply(f"""
Привет! 👋
Гайд стоит 2 USDT (TRC-20)

💳 Адрес для перевода:
`{USDT_ADDRESS}`

⚠️ Перевод строго в сети TRC-20

После оплаты нажми /getguide
    """, parse_mode="Markdown")

@dp.message_handler(commands=["getguide"])
async def check_payment_and_send(message: types.Message):
    user_id = message.from_user.id
    async with aiohttp.ClientSession() as session:
        async with session.get(CHECK_API_URL) as resp:
            if resp.status != 200:
                await message.reply("Ошибка при проверке транзакций. Попробуйте позже.")
                return
            data = await resp.json()
            transactions = data.get("data", [])
            for tx in transactions:
                if tx.get("toAddress") == USDT_ADDRESS and float(tx.get("amount", 0)) >= 2:
                    await message.reply_document(types.InputFile(PDF_PATH))
                    return
            await message.reply("Оплата не найдена. Попробуйте через 1–2 минуты.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
