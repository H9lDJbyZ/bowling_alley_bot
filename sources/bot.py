import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.enums.dice_emoji import DiceEmoji
# from aiogram import F
from aiohttp import web
import json
from os import getenv


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = getenv('BA_BOT_TOKEN')
UPDATE_MODE = int(getenv('UPDATE_MODE'))
PORT = int(getenv('PORT'))


bot = Bot(BOT_TOKEN)
dp = Dispatcher()

score_file = 'score.json'


@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    await message.answer('Hello!')


@dp.message(Command('score'))
async def get_score(message: types.Message):
    text = ''
    scores = load_score()
    chat_id = str(message.chat.id)
    if chat_id in scores:
        scores = scores[chat_id]
        for score in scores:
            s = scores[score]
            if s['score_value'] > 0:
                text += f'{s['fullname']} ({s['username']}): {s['score_value']}, strikes: {s['strikes']}\n'
    if text == '':
        text = 'Таблица лидеров пуста'
    await message.answer(text)


@dp.message()
async def get_dice(message: types.Message):
# 1 - промах, 2 - одна кегля, 3 - три ..., 6 - страйк, видимо две кегли сбить невозможно
    if message.dice is not None:
        if message.dice.emoji == DiceEmoji.BOWLING:
            current_dice_value = message.dice.value
            if current_dice_value > 1:
                if current_dice_value == 2:
                    current_dice_value = 1
                from_id = str(message.from_user.id)
                chat_id = str(message.chat.id)
                scores = load_score()
                if chat_id not in scores:
                    scores_in_chat = dict()
                else:
                    scores_in_chat = scores[chat_id]
                if from_id not in scores_in_chat:
                    scores_in_chat[from_id] = dict()
                    scores_in_chat[from_id]['score_value'] = current_dice_value
                    scores_in_chat[from_id]['strikes'] = 0
                else:
                    scores_in_chat[from_id]['score_value'] += current_dice_value
                if current_dice_value == 6:
                    scores_in_chat[from_id]['strikes'] += 1
                scores_in_chat[from_id]['username'] = message.from_user.username
                scores_in_chat[from_id]['fullname'] = message.from_user.full_name
                scores[chat_id]=scores_in_chat
                save_score(scores)
            # await message.answer(f'значение: {message.dice.value}')


def load_score() -> dict:
    result = dict()
    try:
        with open(score_file) as f:
            result = json.load(f)
    except Exception as e:
        print(e)
    return result



def save_score(score: dict):
    try:
        with open(score_file, 'w') as f:
            json.dump(score, f)
    except Exception as e:
        print(e)


routes = web.RouteTableDef()


@routes.get("/")
async def index(request):
    """Используется для health check"""
    return web.Response(text="OK")


@routes.post(f"/{BOT_TOKEN}")
async def handle_webhook_request(request):
    """Обрабатывает webhook из telegram"""

    # Достаем токен
    url = str(request.url)
    index = url.rfind("/")
    token = url[index + 1 :]

    # Проверяем токен
    if token == BOT_TOKEN:
        request_data = await request.json()
        update = types.Update(**request_data)
        await dp._process_update(bot=bot, update=update)

        return web.Response(text="OK")
    else:
        return web.Response(status=403)


if __name__ == "__main__" and UPDATE_MODE == 1:
    logger.info('webhook mode')
    logger.info("Сервер заработал ...")

    app = web.Application()
    app.add_routes(routes)
    web.run_app(app, host="0.0.0.0", port=PORT)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__" and UPDATE_MODE == 0:
    logger.info('polling mode')
    asyncio.run(main())