import asyncio
import logging
import sys
from os import getenv
from collections import defaultdict
from datetime import datetime
import aiogram.types
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.types import PhotoSize
from aiogram.utils.markdown import hbold
from aiogram.utils.keyboard import InlineKeyboardBuilder


from settings import TEST_TOKEN, MEDIA_STORAGE, VOICE_SRORAGE, TEST_TOKEN
from aiogram import F
from aiogram.types import FSInputFile, ContentType, ReactionTypeEmoji, CallbackQuery
import TestDatabaseClient
bot = Bot(TEST_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
dbclient = TestDatabaseClient.DatabaseClient()
image_file_ids = {}
image_file_unique_ids = {}
images_in_categgory = {}


async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    # And the run events dispatching
    await dbclient.create_pool()
    await dbclient.execute_script("message.sql")
    # await dbclient.update_persons_chats_from_messages()
    await dp.start_polling(bot)


@dp.message()
async def all_handler(message: types.Message) -> None:
    print('trying to add record in postgres database', message.text)
    if message.text is not None:
        if "соционяш" in message.text.lower() in message.text.lower():
            print("socionyasha mentioned")
            await bot.set_message_reaction(chat_id=message.chat.id, message_id=message.message_id,
                                       reaction=[ReactionTypeEmoji(emoji="❤")])
    
    # await dbclient.add_chat_record(message)
    # await dbclient.add_person_record(message)
    await dbclient.add_message_record(message)
    # await dbclient.add_person_chat_if_not_exists(message.from_user.id, chat_id=message.chat.id, anon_posting=True)
    if message.chat.type == 'private':
        print("starting anon post")
        await anon_posting(message)


if __name__ == "__main__":
    print('Starting test bot...')
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    asyncio.run(main())
