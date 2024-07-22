import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
import requests
import random

from config import TOKEN, ALPHA_API_KEY

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)

# Пример словарей валют
physical_currencies = {
    "USD": "US Dollar",
    "EUR": "Euro",
    "JPY": "Japanese Yen",
    "GBP": "British Pound",
    "AUD": "Australian Dollar"
}

digital_currencies = {
    "BTC": "Bitcoin",
    "ETH": "Ethereum",
    "LTC": "Litecoin",
    "XRP": "Ripple",
    "ADA": "Cardano"
}

# Определение состояний
class CurrencyExchange(StatesGroup):
    waiting_for_from_currency = State()
    waiting_for_to_currency = State()


# Функция для получения обменного курса
def get_exchange_rate(api_key, from_currency, to_currency):
    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": "CURRENCY_EXCHANGE_RATE",
        "from_currency": from_currency,
        "to_currency": to_currency,
        "apikey": api_key
    }

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if "Realtime Currency Exchange Rate" in data:
            exchange_rate = data["Realtime Currency Exchange Rate"]["5. Exchange Rate"]
            return exchange_rate
        else:
            return None
    else:
        return None


# Обработчик команды /start
@dp.message(Command(commands=["start"]))
async def start(message: Message, state: FSMContext):
    await message.answer(
        "Привет! Я помогу Вам узнать обменный курс в реальном времени для любой пары валют.\n"
        "Подробности Вы узнаете, воспользовавшись командой /help."
        "\n\nВведите исходную валюту - из списка популярных физических валют: USD, EUR, RUB, CNY, TRY, CHF, GBP, JPY, BRL, PLN.\n"
        "или можете воспользоваться списком популярных цифровых валют: BTC, ETH, LTC, XMR, DASH, ZEC, VTC, BTS, FCT, DOGE.\n"
        "либо сделать выбор самостоятельно из множества вариантов валют на сайте: https://www.alphavantage.co/"
    )
    await state.set_state(CurrencyExchange.waiting_for_from_currency)


# Обработчик команды /help
@dp.message(Command(commands=["help"]))
async def help_command(message: Message):
    await message.answer(
        "1. Чтобы узнать аббревиатуры валют, вы можете пройти по следующим ссылкам:\n"
           "Физические валюты: https://www.alphavantage.co/physical_currency_list/\n"
           "Цифровые валюты: https://www.alphavantage.co/digital_currency_list/\n"
        "2. Чтобы узнать обменный курс случайной пары валют, воспользуйтесь командой /random_pair.\n"
    )


# Обработчик ввода исходной валюты
@dp.message(CurrencyExchange.waiting_for_from_currency)
async def process_from_currency(message: Message, state: FSMContext):
    from_currency = message.text.upper()
    await state.update_data(from_currency=from_currency)
    await message.answer("Введите целевую валюту - список популярных физических валют: USD, EUR, RUB, CNY, TRY, CHF, GBP, JPY, BRL, PLN.")
    await state.set_state(CurrencyExchange.waiting_for_to_currency)


# Обработчик ввода целевой валюты
@dp.message(CurrencyExchange.waiting_for_to_currency)
async def process_to_currency(message: Message, state: FSMContext):
    to_currency = message.text.upper()
    data = await state.get_data()
    from_currency = data['from_currency']
    exchange_rate = get_exchange_rate(ALPHA_API_KEY, from_currency, to_currency)

    if exchange_rate:
        await message.answer(f"Обменный курс {from_currency} к {to_currency} составляет {exchange_rate}")
    else:
        await message.answer("Не удалось получить обменный курс. Проверьте правильность введенных данных.")

    await state.clear()

# Обработчик команды /random_pair
@dp.message(Command(commands=['random_pair']))
async def random_pair(message: types.Message, state: FSMContext):
    physical_currency_list = list(physical_currencies.keys())
    digital_currency_list = list(digital_currencies.keys())

    if random.choice([True, False]):
        # Случайная пара физических валют
        from_currency, to_currency = random.sample(physical_currency_list, 2)
        await message.answer(f"Случайная пара физических валют: {from_currency} - {to_currency}")

        exchange_rate = get_exchange_rate(ALPHA_API_KEY, from_currency, to_currency)
        if exchange_rate:
            await message.answer(f"Обменный курс {from_currency} к {to_currency} составляет {exchange_rate}")
        else:
            await message.answer("Не удалось получить обменный курс. Проверьте правильность введенных данных.")
    else:
        # Случайная пара физическая/цифровая валюта
        to_currency = random.choice(physical_currency_list)
        from_currency = random.choice(digital_currency_list)
        await message.answer(f"Случайная пара физическая/цифровая валюта: {from_currency} - {to_currency}")

        exchange_rate = get_exchange_rate(ALPHA_API_KEY, from_currency, to_currency)
        if exchange_rate:
            await message.answer(f"Обменный курс {from_currency} к {to_currency} составляет {exchange_rate}")
        else:
            await message.answer("Не удалось получить обменный курс. Проверьте правильность введенных данных.")

    await state.clear()

# Запуск бота
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
