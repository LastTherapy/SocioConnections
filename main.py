# -*- coding: utf8 -*-
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


from settings import TOKEN, MEDIA_STORAGE, VOICE_SRORAGE
from aiogram import F
from aiogram.types import FSInputFile, ContentType, ReactionTypeEmoji, CallbackQuery
import DatabaseClient
# import VoiceRecognition


# Инициализация бота и диспетчера
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
dbclient = DatabaseClient.DatabaseClient()
image_file_ids = {}
image_file_unique_ids = {}
images_in_categgory = {}

@dp.message_reaction()
async def message_reaction_handler(message_reaction: types.MessageReactionUpdated) -> None:
    pass
    # file_id = "AgACAgIAAxkDAAIWZmXPl2Cv8xnoyjms9Q3Y9dYJaZInAAKo2DEbZU6BSgXvpRJhSNAfAQADAgADcwADNAQ"
    #            AgACAgIAAxkDAAIWZmXPl2Cv8xnoyjms9Q3Y9dYJaZInAAKo2DEbZU6BSgXvpRJhSNAfAQADAgADcwADNAQ
    # await bot.send_photo(message_reaction.chat.id, file_id)

# @dp.message(F.chat.type == "private")
# async def private_handler(message: Message):
#     print("lichka")
@dp.message(Command("all", ignore_case=True))
async def notify_all(message: types.Message) -> None:
    if message.reply_to_message is None:
        print("all must be reply")
        return
    if message.from_user.id != 291699185:
        print("you are not admin to all")
        return
    chats = await dbclient.get_group_chat_ids()
    for chat in chats:
        try:
            await bot.copy_message(chat_id=chat, message_id=message.reply_to_message.message_id,
                                   from_chat_id=message.reply_to_message.chat.id)
            print(f"message sended to {chat}")
        except Exception as e:
            pass

@dp.message(Command("start", ignore_case=True))
async def start_message(message: types.Message) -> None:
    await message.answer("You can post anonymously just with typing here any message")


@dp.message(Command("help", ignore_case=True))
async def delete_message(message: types.Message) -> None:
    await message.answer("Nobody can help you in your life")


@dp.message(Command("d", "del", ignore_case=True), lambda m: m.reply_to_message is not None)
async def delete_message(message: types.Message) -> None:
    if message.reply_to_message.from_user.is_bot:
        try:
            await bot.delete_message(message_id=message.reply_to_message.message_id, chat_id=message.chat.id)
        except Exception:
            print("Error! Bad message to delete")





@dp.message(F.left_chat_member)
async def remove_anon_chat(message: Message):
    await dbclient.remove_person_chat(person_id=message.left_chat_member.id, chat_id=message.chat.id)

#
@dp.message(F.new_chat_title)
async def chat_name_update(message: Message):
    await dbclient.update_chat_name(message.chat.id, message.new_chat_title)

@dp.message(F.text.startswith('/rand'))
async def random_image(message: types.Message) -> None:
    image_name, image_id, image_telegram_id = await dbclient.get_random_image(message.chat.id)
    image = FSInputFile(f"{MEDIA_STORAGE}/{image_name}")
    tags, num_tags, spoiler = await dbclient.get_tags_of_image(image_name)
    if image_telegram_id is None:
        message = await bot.send_photo(message.chat.id, image, caption=tags, has_spoiler=spoiler)
        message_ps = message.photo
        if message_ps:
            new_telegram_id = message_ps[0].file_id
            await dbclient.update_image_telegram_id(image_id, new_telegram_id)
            print("added new note for image id in database")
    else:
        await bot.send_photo(message.chat.id, image_telegram_id, caption=tags, has_spoiler=spoiler)


@dp.message(Command("settings", ignore_case=True))
async def settings_chats(message: Message) -> None:
    if message.chat.type == 'private':
        return
    auto_voice, anon_posting = await dbclient.get_chat_settings(message)
    voice_marker = '✅ Да' if auto_voice else '❌ Нет'
    anon_marker = '✅ Да' if anon_posting else '❌ Нет'
    private_tags = await dbclient.get_private_tags(message.chat.id)
    pt = "нет приватных тегов"
    if private_tags:
        pt = ''.join(f"#{tag} " for tag in private_tags)

    description = f"""
    Настройки чата:
    Автоматически распознавать голосовые: {voice_marker}
    Отправка анонимных сообщений в чат: {anon_marker}
    Приватные категории этого чата: {pt}
    """
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="🎭 Anonymous",
        callback_data="anon_button")
    )
    builder.add(types.InlineKeyboardButton(
        text="🎤 Voice",
        callback_data="voice_button")
    )
    builder.add(types.InlineKeyboardButton(
        text="Close ❌",
        callback_data="settings_x")
    )
    await message.answer(text=description, reply_markup=builder.as_markup())

import  Statistic  #переместить

@dp.message(Command("mystats", ignore_case=True))
async def show_personal_pot(message: Message) -> None:
    dates, counts = await dbclient.get_message_count_by_user(user_id=message.from_user.id, chat_id=message.chat.id)
    path = await Statistic.plot_message_count_graph(dates, counts,
                                                    user_name=message.from_user.first_name, chat_name=message.chat.title)
    print("personal stats called")
    # Рассчитываем среднее количество сообщений
    average_count = sum(counts) / len(counts) if counts else 0

    # Сгруппируем количество сообщений по дням недели
    day_counts = defaultdict(list)
    for date, count in zip(dates, counts):
        day = date.strftime('%A')
        day_counts[day].append(count)

    # Рассчитываем среднее количество сообщений для каждого дня недели
    day_averages = {day: sum(day_counts[day]) / len(day_counts[day]) for day in day_counts}

    # Находим день с максимальным и минимальным средним количеством сообщений
    max_day = max(day_averages, key=day_averages.get)
    min_day = min(day_averages, key=day_averages.get)

    stats_message = (f"Среднее количество сообщений в день: {average_count:.2f}\n"
                     f"Больше всего сообщений в среднем: {max_day} ({day_averages[max_day]:.2f})\n"
                     f"Меньше всего сообщений в среднем: {min_day} ({day_averages[min_day]:.2f})")

    await bot.send_photo(chat_id=message.chat.id, photo=FSInputFile(path), caption=stats_message)

@dp.message(Command("stats", ignore_case=True))
async def show_personal_pot(message: Message) -> None:
    dates, counts = await dbclient.get_message_count_by_chat(chat_id=message.chat.id)
    path = await Statistic.plot_message_count_chat(dates, counts, chat_name=message.chat.title)
    print("stats called")
    await bot.send_photo(chat_id=message.chat.id, photo=FSInputFile(path))

@dp.callback_query(F.data.in_({"voice_button", "anon_button", "settings_x"}))
async def change_voice_settings(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    if callback.data == "settings_x":
        await bot.delete_message(chat_id=chat_id, message_id=callback.message.message_id)
        await callback.answer()
        return
    if callback.data == "voice_button":
        comment = "голосовых"
        await dbclient.toggle_auto_voice(chat_id=chat_id)
    if callback.data == "anon_button":
        comment = "анонимных сообщений"
        await dbclient.toggle_anon_posting(chat_id=chat_id)

    private_tags = await dbclient.get_private_tags(callback.message.chat.id)
    pt = "нет приватных тегов"
    if private_tags:
        pt = ''.join(f"#{tag} " for tag in private_tags)

    auto_voice, anon_posting = await dbclient.get_chat_settings(callback.message)
    voice_marker = '✅ Да' if auto_voice else '❌ Нет'
    anon_marker = '✅ Да' if anon_posting else '❌ Нет'
    description = f"""
    Настройки чата:
    (Недоступно) Автоматически распознавать голосовые: {voice_marker}
    Отправка анонимных сообщений в чат: {anon_marker}
    Приватные категории этого чата: {pt}
    """
    # Обновление исходного сообщения
    await callback.message.edit_text(text=description, reply_markup=callback.message.reply_markup)
    await callback.answer(f"Настройки {comment} сообщений обновлены.")

# @dp.callback_query(F.data == "voice_button")
# async def change_voice_settings(callback: CallbackQuery):
#     await callback.answer("Done")


@dp.message(Command("v", "voice", ignore_case=True))
async def command_start_handler(message: Message) -> None:
    await message.answer('Распознавание голоса пока отключено')
#     help_text = """
#     Use /v or /voice in your message reply to do speech recognition. 
# You can specify the model type with another word, for example, - "/v base". 
# The available models are (parameters): tiny (39M), base (74M), small (244M), medium (769M), and large (1550M). 
# Be aware that the large model is slower than Slow. 
# By default, I will use the small one.
# You can also turn on or off automatic voice recognition in the chat settings by typing /settings.
# Using Whisper pretrained model by OpenAI.
#     """
#     if message.reply_to_message is None:
#         image = FSInputFile("whisper.png")
#         await bot.send_photo(chat_id=message.chat.id, photo=image, caption=help_text)
#         # await message.answer(help_text)
#         return

#     message_text = message.text.lower().split()
#     if len(message_text) > 1:
#         arg = message_text[1]
#         if arg == 'help':
#             image = FSInputFile("whisper.png")
#             await bot.send_photo(chat_id=message.chat.id, photo=image, caption=help_text)
#             # await message.answer(help_text)
#             return
#         else:
#             await voice_recognition(message.reply_to_message, arg)
#             return
#     else:
#         await voice_recognition(message.reply_to_message)
#         return


@dp.message(F.content_type.in_({'voice'}))
async def auto_voice_recognition(message: Message):
    pass
    # auto_voice, anon_posting = await dbclient.get_chat_settings(message)
    # if not auto_voice:
    #     print("Auto audio off for this chat")
    #     return
    # else:
    #     await voice_recognition(message)

async def voice_recognition(message: Message, model: str = 'small'):
    voice_id = message.voice.file_id
    file = await bot.get_file(voice_id)
    file_path = file.file_path
    destination_file = f'{VOICE_SRORAGE}{message.message_id}.ogg'
    await bot.download_file(file_path, destination_file)
    print("voice downloaded")
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    recognized: Message = await message.reply("Starting voice recognition...")
    try:
        result = VoiceRecognition.recognition(destination_file, model)
    except Exception:
        result = "Sorry, no more GPU memory available for neuro SocioNyash. Error(("
    if len(result) == 0:
        result = "Sorry, no text in voice recognition."
    if len(result) < 4096:
        await bot.edit_message_text(result, chat_id=message.chat.id, message_id=recognized.message_id)
    else:
        await bot.delete_message(message_id=recognized.message_id, chat_id=recognized.chat.id)
        splited = VoiceRecognition.split_string(result)
        for chunk in splited:
            print(chunk)
            await message.reply(chunk)


#saving media to database with hashtags
@dp.message(F.text.startswith('/'))
async def image_save_category(message: types.Message) -> None:
    if not message.reply_to_message:
        await show_images_in_category(message)
        return

    if message.reply_to_message.photo is None:
        return
    tags = message.text.lower().lstrip('/').split()
    if len(tags) > 1:
        end = 'tags'
    else:
        end = 'tag'
    formated_tags = ' '.join(f"#{tag}" for tag in tags if tag)
    file_id = message.reply_to_message.photo[-1].file_id
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Yes",
        callback_data=f"imagesave_yes"))
    builder.add(types.InlineKeyboardButton(
        text="No",
        callback_data="imagesave_no"))
    image_file_ids[message.message_id] = message.reply_to_message.photo[-1].file_id #is it uniq? check
    image_file_unique_ids[message.message_id] = message.reply_to_message.photo[-1].file_unique_id
    image_count = await dbclient.count_images_by_tag(tags[0])
    category_description = f"There {'is' if image_count == 1 else 'are'} {image_count} image{'s' if image_count != 1 else ''} for this category" if image_count > 0 else \
        "There are no images for this category. A new category will be created."
    await message.reply(
        text=f"Do you want to save the image with {formated_tags} {end}?\n{category_description}",
        reply_markup=builder.as_markup()
    )


async def show_images_in_category(message: types.Message, index: int = 0):
    args = message.text.lower().lstrip('/').split()
    tag = args[0]

    if len(args) > 1:
        try:
            index = int(args[1])
        except ValueError:
            pass
    tag_count: int = await dbclient.count_images_by_tag(tag)
    if index >= tag_count:
        index = 0
    all_images,  private_chats = await dbclient.get_images_by_tag(tag)
    print(private_chats)
    current_image = all_images[index]
    private_settings: str = "public"
    if private_chats:
        if message.chat.id != private_chats: #может потом на спиоск заменить и тогда переделать
            await bot.send_message(chat_id=message.chat.id, text="Молодой человек, эта категория не для вас показывается.")
            return
        else:
            private_settings = "private"

    message_text = f"""Категория: {tag}\nВладелец категории: {"Соционяшечка"}\nКоличество изображений: {tag_count}\nТип доступа: {private_settings}
       """
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="<",
        callback_data=f"category_{index-1}"))
    builder.add(types.InlineKeyboardButton(
        text=">",
        callback_data=f"category_{index+1}"))
    builder.add(types.InlineKeyboardButton(
        text="❌",
        callback_data="category_x"))

    if current_image[2] is not None:
        new_message = await bot.send_photo(message.chat.id, photo=current_image[2], caption=message_text,
                             reply_markup=builder.as_markup())
    elif current_image[1] is not None:
        new_message = await bot.send_photo(message.chat.id, photo=FSInputFile(f"{MEDIA_STORAGE}/{current_image[1]}"),
                             caption=message_text, reply_markup=builder.as_markup())
    else:
        return
    images_in_categgory[new_message.message_id] = all_images

@dp.callback_query(F.data.startswith("category_"))
async def category_callback(call: CallbackQuery):

    if call.data == "category_x":
        if call.message.message_id in images_in_categgory:
            del images_in_categgory[call.message.message_id]
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await call.answer('Closed')
        return

    _, index_str = call.data.split("_")
    try:
        index = int(index_str)  # Преобразуем строку в число
    except ValueError:
        await call.answer("Произошла ошибка в обработке запроса.")
        return

    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="<",
        callback_data=f"category_{index-1}"))
    builder.add(types.InlineKeyboardButton(
        text=">",
        callback_data=f"category_{index+1}"))
    builder.add(types.InlineKeyboardButton(
        text="❌",
        callback_data="category_x"))
    current_image = images_in_categgory[call.message.message_id][index]
    category_len = len(images_in_categgory[call.message.message_id])
    index = index if index > 0 else category_len + index
    caption = f"Current image: {index}/{category_len}"
    print(current_image)
    if current_image[2] is not None:
        await bot.edit_message_media(media=types.input_media_photo.InputMediaPhoto(media=current_image[2], caption=caption),
                                     chat_id=call.message.chat.id, message_id=call.message.message_id,
                                     reply_markup=builder.as_markup())
        await call.answer('Ok')
    elif current_image[1] is not None:
        await bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                     media=types.input_media_photo.InputMediaPhoto(media=FSInputFile(f"{MEDIA_STORAGE}/{current_image[1]}"), caption=caption),
                                     reply_markup=builder.as_markup())
        await call.answer('Ok')


@dp.callback_query(F.data.startswith("imagesave_"))
async def save_image_in_category(callback: types.CallbackQuery) -> None:
    if callback.data == 'imagesave_no':
        await callback.answer()
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    else:
        message_id = callback.message.reply_to_message.message_id
        if message_id in image_file_ids and message_id in image_file_unique_ids:
            file_id = image_file_ids[message_id]
            file_unique_id = image_file_unique_ids[message_id]
            tags = callback.message.reply_to_message.text.lower().lstrip('/').split()
            try:
                await dbclient.save_image_with_tags(image_path=file_id, unique_id=file_unique_id, tags=tags)
                await callback.answer("Image saved")
                await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
            except Exception as e:
                await callback.answer(f"Error saving image: {str(e)}")
                del image_file_ids[message_id]
                del image_file_unique_ids[message_id]
        else:
            print('Error while save image in category')
            await callback.answer("Image information not found.")





@dp.message(F.text.startswith('!'))
async def image_handler(message: types.Message) -> None:
    message_text = message.text.lower().split()
    tag = message_text[0][1:]  # Получаем тег, удаляя первый символ '#'
    args = message_text[1] if len(message_text) > 1 else None
    print(tag + ' called')
    if tag == 'rand' or tag == 'random':
        await random_image(message)
        return
    image_data = await dbclient.find_random_image_by_tag(tag, chat_id=message.chat.id)
    if not image_data:
        return  # Обработка случая, если изображение не найдено

    image_id,  image_name, tag_name, caption, image_telegram_id, spoiler = image_data.values()

    tags, num_tags, _ = await dbclient.get_tags_of_image(image_name)
    if num_tags <= 1:
        tags = None

    if args and args.startswith('-sp'):
        spoiler = True

    if tags is not None:
        if caption is not None:
            caption = tags + caption
        else:
            caption = tags

    if image_telegram_id:
        await bot.send_photo(chat_id=message.chat.id, photo=image_telegram_id, caption=caption, has_spoiler=spoiler)
    elif image_name:
        image = FSInputFile(f"{MEDIA_STORAGE}/{image_name}")
        new_message = await bot.send_photo(message.chat.id, photo=image, caption=caption, has_spoiler=spoiler)
        if new_message.photo:
            new_telegram_id = new_message.photo[0].file_id
            await dbclient.update_image_telegram_id(image_id, new_telegram_id)
            print("added new note for image id in database")


@dp.message()
async def all_handler(message: types.Message) -> None:
    if message.text is not None:
        if "соционяш" in message.text.lower() in message.text.lower():
            print("socionyasha mentioned")
            await bot.set_message_reaction(chat_id=message.chat.id, message_id=message.message_id,
                                       reaction=[ReactionTypeEmoji(emoji="❤")])
    await dbclient.add_chat_record(message)
    await dbclient.add_person_record(message)
    await dbclient.add_message_record(message)
    await dbclient.add_person_chat_if_not_exists(message.from_user.id, chat_id=message.chat.id, anon_posting=True)
    if message.chat.type == 'private':
        print("starting anon post")
        await anon_posting(message)


async def anon_posting(message: types.Message) -> None:
    # Получаем список чатов пользователя, где разрешена анонимная отправка сообщений
    personal_chats = await dbclient.get_anon_posting_chats_for_user(message.from_user.id)
    if not personal_chats:
        await message.answer("We couldn't find you in any chat. To enable anonymous posting, you must write a message in a chat where I exist.")
        return
    if len(personal_chats) == 1 and personal_chats[0]['anon_posting']:
        chat_id = personal_chats[0]['chat_id']
        await bot.copy_message(chat_id=chat_id, from_chat_id=message.chat.id, message_id=message.message_id)
    else:
        list_of_chats = ''
        for index, chat in enumerate(personal_chats):
            chat_status = '✅' if chat['anon_posting'] else '❌'
            list_of_chats += f"{index + 1}. {chat['name']} {chat_status}\n"
        # Создание клавиатуры для выбора чата
        keyboard = InlineKeyboardBuilder()
        chat_buttons = [types.InlineKeyboardButton(text=str(index + 1), callback_data=f"anontoggle_{chat['chat_id']}") for index, chat in enumerate(personal_chats)]
        keyboard.row(*chat_buttons)
        keyboard.row(types.InlineKeyboardButton(text="send", callback_data="send_anon"))
        # Отправка сообщения с клавиатурой
        await message.reply("Where to send?\n" + list_of_chats, reply_markup=keyboard.as_markup())


@dp.callback_query(F.data.startswith("anontoggle_"))
async def change_anon_list(callback: types.CallbackQuery):
    user_id = callback.message.reply_to_message.from_user.id
    chat_id = int(callback.data.split("_")[1])
    #togle and save in database
    await dbclient.toggle_anon_user_posting(user_id=user_id, chat_id=chat_id)
    personal_chats_ids = await dbclient.get_anon_posting_chats_for_user(user_id=user_id)
    list_of_chats = ''
    for index, chat in enumerate(personal_chats_ids):
        chat_status = '✅' if chat['anon_posting'] else '❌'
        list_of_chats += f"{index + 1}. {chat['name']} {chat_status}\n"

    # Создание клавиатуры для выбора чата
    keyboard = InlineKeyboardBuilder()
    chat_buttons = [types.InlineKeyboardButton(text=str(index + 1), callback_data=f"anontoggle_{chat['chat_id']}") for
                    index, chat in enumerate(personal_chats_ids)]
    keyboard.row(*chat_buttons)
    keyboard.row(types.InlineKeyboardButton(text="send", callback_data="send_anon"))
    # Отправка сообщения с клавиатурой
    await callback.message.edit_text("Where to send?\n" + list_of_chats, reply_markup=keyboard.as_markup())
    await callback.answer()


@dp.callback_query(F.data == "send_anon")
async def send_to_anon_list(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    # Получаем список чатов пользователя, где разрешена анонимная отправка сообщений
    personal_chats_ids = await dbclient.get_anon_posting_chats_for_user(user_id=user_id)
    # Определяем ID оригинального сообщения и его чат
    original_message_id = callback.message.reply_to_message.message_id
    from_chat_id = callback.message.reply_to_message.chat.id
    for chat in personal_chats_ids:
        if chat['anon_posting']:
            # Отправка копии сообщения в чаты с отметкой "✅"
            await bot.copy_message(chat_id=chat['chat_id'], from_chat_id=from_chat_id, message_id=original_message_id)
    # Удаление оригинального запроса после отправки
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await callback.answer("Message sent anonymously.")

# @dp.callback_query(F.data.in_({"voice_button", "anon_button"}))



async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    # And the run events dispatching
    await dbclient.create_pool()
    # await dbclient.update_persons_chats_from_messages()
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
