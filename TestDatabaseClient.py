import aiogram.types
import asyncpg
from settings import TEST_DATABASE_URL as DATABASE_URL
import random
from datetime import datetime
from aiogram.types.user_profile_photos import UserProfilePhotos


class DatabaseClient:
    def __init__(self):
        self.connection_string = DATABASE_URL
        print(f"connected to {DATABASE_URL} database")
        self.conn = None
        self.pool = None

    async def create_pool(self):
        self.pool = await asyncpg.create_pool(self.connection_string)

    async def connect(self):
        if not self.conn:
            self.conn = await asyncpg.connect(self.connection_string)

    async def get_random_image(self, chat_id: int):
        # await self.connect()
        async with self.pool.acquire() as conn:
            # Получение случайного изображения
            image_record = await conn.fetchrow(
                '''
                SELECT name, i.id, image_telegram_id FROM images i
                JOIN image_tags t ON t.image_id = i.id
                LEFT JOIN public.chats_private_tags cpt on t.tag_id = cpt.tag_id
                where cpt.chat_id is NULL or cpt.chat_id = $1
                 ORDER BY RANDOM() LIMIT 1
                ''', chat_id)
            if image_record:
                return image_record['name'], image_record['id'], image_record['image_telegram_id']
            else:
                return None

    async def find_random_image_by_tag(self, tag: str, chat_id: int):
        async with self.pool.acquire() as conn:
            image_record = await conn.fetchrow(
                '''
                SELECT i.id as image_id, i.name as image_path, t.name as tag_name, 
                i.caption, i.image_telegram_id, t.spoiler
                FROM images i
                JOIN image_tags it ON i.id = it.image_id
                JOIN tags t ON t.id = it.tag_id
                LEFT JOIN public.chats_private_tags cpt on t.id = cpt.tag_id
                WHERE t.name = $1 and (cpt.chat_id is NULL or cpt.chat_id = $2)
                ORDER BY RANDOM() LIMIT 1
                ''', tag, chat_id)

            if image_record:
                return {
                    'image_id': image_record['image_id'],
                    'image_path': image_record['image_path'],
                    'tag_name': image_record['tag_name'],
                    'caption': image_record['caption'],
                    'image_telegram_id': image_record['image_telegram_id'],
                    'spoiler': image_record['spoiler']
                }
            else:
                return None


    async def get_tags_of_image(self, image_name):
        async with self.pool.acquire() as conn:
            tags = await conn.fetch(
                'SELECT t.name, t.spoiler FROM tags t '
                'JOIN image_tags it ON t.id = it.tag_id '
                'JOIN images i ON it.image_id = i.id '
                'WHERE i.name = $1', image_name)
            if tags:
                tags_list = []
                spoiler = False
                for tag in tags:
                    tags_list.append('#' + tag['name'])
                    if tag['spoiler']:
                        spoiler = True

                return ', '.join(tags_list), len(tags), spoiler
            else:
                return None, 0, False


    async def get_chats_by_user(self, message: aiogram.types.Message) -> list:
        async with self.pool.acquire() as conn:
            query = """
                   SELECT DISTINCT m.chat_id, ch.name 
                   FROM messages m
                   JOIN chats ch ON m.chat_id = ch.chat_id
                   WHERE from_user_id = $1 AND ch.type != 'private' AND ch.anon_posting = TRUE
               """
            rows = await conn.fetch(query, message.from_user.id)
            return rows

    async def add_chat_record(self, message: aiogram.types.Message):
        # await self.connect()
        async with self.pool.acquire() as conn:
            chat_id = message.chat.id
            type = message.chat.type
            name = message.chat.title if type == 'group' or type == 'supergroup' else message.from_user.username
            photo = None
            update_date = datetime.now().date()  # Текущая дата
            # Вставка новой записи в таблицу chats
            await conn.execute(
                'INSERT INTO chats (chat_id, type, name, photo, update_date)'
                'VALUES ($1, $2, $3, $4, $5) ON CONFLICT (chat_id) DO NOTHING',
                chat_id, type, name, photo, update_date
            )

    async def add_person_record(self, message: aiogram.types.Message) -> None:
        async with self.pool.acquire() as conn:
        # await self.connect()
            person_id = message.from_user.id
            name = message.from_user.first_name
            lastname = message.from_user.last_name
            username = message.from_user.username
            update_date = message.date
            await conn.execute(
                '''
                INSERT INTO persons (person_id, name, lastname, username,  update_date)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (person_id) DO NOTHING
                ''',
                person_id, name, lastname, username,  update_date
            )

    # edited
    async def add_message_record(self, message: aiogram.types.Message) -> None:        
        async with self.pool.acquire() as conn:
            message_id: int = message.message_id
            chat_id: int = message.chat.id
            from_user_id: int = message.from_user.id
            reply_to_message: int = message.reply_to_message.message_id if message.reply_to_message else None
            text: str = message.text
            date = message.date
            content_type: str = message.content_type
            is_forwarded: bool = True if message.forward_origin else False
            file_id: str = message.sticker.file_id if content_type == 'sticker' else None
            if message.caption:
                text = message.caption

            await conn.execute(
                '''
                INSERT INTO message (message_id, chat_id, from_user_id, reply_to_message, text, date, content_type, file_id, is_forwarded)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)               
                ''',
                message_id, chat_id, from_user_id, reply_to_message, text,  date, content_type, file_id, is_forwarded
            )

    async def update_image_telegram_id(self, image_id, telegram_image_id):
        async with self.pool.acquire() as conn:
            await conn.execute(
                'UPDATE images SET image_telegram_id = $1 WHERE id = $2',
                telegram_image_id, image_id
            )

    async def get_chat_settings(self, message: aiogram.types.Message):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                '''
                SELECT auto_voice, anon_posting FROM chats ch
                WHERE ch.chat_id = $1
                ''',
                message.chat.id
            )
            if row:
                auto_voice, anon_posting = row['auto_voice'], row['anon_posting']
                return auto_voice, anon_posting
            else:
                return None, None  # Или другие значения по умолчанию, если это уместно

    async def toggle_auto_voice(self, chat_id: int):
        async with self.pool.acquire() as conn:
            # Получаем текущее состояние
            current_state = await conn.fetchval('SELECT auto_voice FROM chats WHERE chat_id = $1', chat_id)
            # Меняем состояние на противоположное
            new_state = not current_state
            await conn.execute('UPDATE chats SET auto_voice = $1 WHERE chat_id = $2', new_state, chat_id)
            return new_state

    async def toggle_anon_posting(self, chat_id: int):
        async with self.pool.acquire() as conn:
            # Получаем текущее состояние
            current_state = await conn.fetchval('SELECT anon_posting FROM chats WHERE chat_id = $1', chat_id)
            # Меняем состояние на противоположное
            new_state = not current_state
            await conn.execute('UPDATE chats SET anon_posting = $1 WHERE chat_id = $2', new_state, chat_id)
            return new_state

    async def update_persons_chats_from_messages(self):
        async with self.pool.acquire() as conn:
            # Получение данных из messages
            messages = await conn.fetch(
                'SELECT from_user_id, chat_id FROM messages'
            )

            # Обновление данных в persons_chats
            for message in messages:
                from_user_id = message['from_user_id']
                chat_id = message['chat_id']

                # Проверяем, не совпадают ли person_id и chat_id
                if from_user_id == chat_id:
                    continue  # Пропускаем эту итерацию цикла

                # Проверка существует ли запись
                exists = await conn.fetchval(
                    'SELECT EXISTS(SELECT 1 FROM persons_chats WHERE person_id = $1 AND chat_id = $2)',
                    from_user_id, chat_id
                )

                if exists:
                    # Обновление существующей записи
                    await conn.execute(
                        'UPDATE persons_chats SET anon_posting = false WHERE person_id = $1 AND chat_id = $2',
                        from_user_id, chat_id
                    )
                else:
                    # Добавление новой записи
                    await conn.execute(
                        'INSERT INTO persons_chats (person_id, chat_id, anon_posting) VALUES ($1, $2, false)',
                        from_user_id, chat_id
                    )

    async def toggle_anon_user_posting(self, user_id: int, chat_id: int):
        async with self.pool.acquire() as conn:
            # Проверяем, существует ли запись
            exists = await conn.fetchval(
                'SELECT EXISTS(SELECT 1 FROM persons_chats WHERE person_id = $1 AND chat_id = $2)',
                user_id, chat_id)
            if exists:
                # Если запись существует, переключаем anon_posting
                await conn.execute(
                    '''
                    UPDATE persons_chats
                    SET anon_posting = NOT anon_posting
                    WHERE person_id = $1 AND chat_id = $2
                    ''',
                    user_id, chat_id)
            else:
                # Если записи нет, добавляем новую с anon_posting = true
                await conn.execute(
                    '''
                    INSERT INTO persons_chats (person_id, chat_id, anon_posting)
                    VALUES ($1, $2, true)
                    ''',
                    user_id, chat_id)

    async def get_anon_posting_chats_for_user(self, user_id: int):
        async with self.pool.acquire() as conn:
            # Получение списка чатов и их состояний anon_posting для пользователя
            chats = await conn.fetch(
                '''
                SELECT c.chat_id, c.name, pc.anon_posting
                FROM persons_chats pc
                JOIN chats c ON pc.chat_id = c.chat_id
                WHERE pc.person_id = $1 AND c.anon_posting = true
                ''',
                user_id
            )
            return chats

    async def add_person_chat_if_not_exists(self, person_id: int, chat_id: int, anon_posting: bool = False):
        async with self.pool.acquire() as conn:
            # Проверяем, существует ли уже такая запись
            exists = await conn.fetchval(
                'SELECT EXISTS(SELECT 1 FROM persons_chats WHERE person_id = $1 AND chat_id = $2)',
                person_id, chat_id
            )

            if not exists:
                # Если записи нет, добавляем новую
                await conn.execute(
                    'INSERT INTO persons_chats (person_id, chat_id, anon_posting) VALUES ($1, $2, $3)',
                    person_id, chat_id, anon_posting
                )

    async def remove_person_chat(self, person_id: int, chat_id: int):
        async with self.pool.acquire() as conn:
            # Удаление записи о чате пользователя
            await conn.execute(
                'DELETE FROM persons_chats WHERE person_id = $1 AND chat_id = $2',
                person_id, chat_id
            )

    async def update_chat_name(self, chat_id: int, new_name: str):
        async with self.pool.acquire() as conn:
            # Обновление названия чата
            await conn.execute(
                'UPDATE chats SET name = $1 WHERE chat_id = $2',
                new_name, chat_id
            )

    async def save_image_with_tags(self, image_path, unique_id, tags):
        async with self.pool.acquire() as conn:
            # Добавление информации о картинке
            image_id = await conn.fetchval('SELECT id FROM images WHERE file_unique_id = $1', unique_id)
            if not image_id:
                image_id = await conn.fetchval(
                    'INSERT INTO images (name, image_type, image_telegram_id, file_unique_id) VALUES ($1, $2, $3, $4) RETURNING id',
                    None, 'jpg', image_path, unique_id)
            for tag in tags:
                # Проверка, существует ли уже такой тег
                tag_id = await conn.fetchval('SELECT id FROM tags WHERE name = $1', tag)
                if not tag_id:
                    # Если тега нет, добавляем его
                    tag_id = await conn.fetchval(
                        'INSERT INTO tags (name, spoiler) VALUES ($1, $2) RETURNING id',
                        tag, False)
                # Связываем картинку с тегом
                await conn.execute(
                    'INSERT INTO image_tags (image_id, tag_id) VALUES ($1, $2)',
                    image_id, tag_id)


    async def count_images_by_tag(self, tag: str) -> int:
        async with self.pool.acquire() as conn:
            result = await conn.fetchval('''
                select count(*) FROM images i
                join image_tags it ON it.image_id = i.id
                join public.tags t on t.id = it.tag_id  
                WHERE t.name = $1
                ''', tag)
        return result


    async def get_private_tags(self, chat_id: int) -> list:
        async with self.pool.acquire() as conn:
            # Выполнение запроса к базе данных для получения приватных тегов для чата
            tags_records = await conn.fetch(
                '''
                SELECT t.name
                FROM tags t
                JOIN chats_private_tags cpt ON t.id = cpt.tag_id
                WHERE cpt.chat_id = $1
                ''', chat_id)

            # Преобразование результатов в список названий тегов
            tags = [record['name'] for record in tags_records]
            return tags

    async def get_images_by_tag(self, tag: str):
        async with self.pool.acquire() as conn:
            records = await conn.fetch(
                '''
                select i.id, i.name, i.image_telegram_id, cpt.chat_id
                from images i
                join public.image_tags it on i.id = it.image_id
                join public.tags t on it.tag_id = t.id
                left join public.chats_private_tags cpt on t.id = cpt.tag_id
                where t.name = $1
                ''', tag
            )
            if not records:
                return None, None
            result = [[record['id'], record['name'], record['image_telegram_id']] for record in records]
            private_chat = records[0]['chat_id']
            return result, private_chat

    async def get_group_chat_ids(self):
        async with self.pool.acquire() as conn:
            chat_records = await conn.fetch(
                '''
                SELECT chat_id
                FROM chats
                WHERE type != 'private'
                '''
            )
            # Преобразование результатов запроса в список номеров чатов
            chat_ids = [record['chat_id'] for record in chat_records]
            return chat_ids

    async def get_message_count_by_user(self, user_id: int, chat_id: int):
        async with self.pool.acquire() as conn:
            records = await conn.fetch(
                '''
                SELECT DATE(update_date) as date, COUNT(*) as message_count
                FROM messages
                WHERE from_user_id = $1 and chat_id = $2
                AND update_date >= NOW() - INTERVAL '30 days'
                GROUP BY DATE(update_date)
                ORDER BY DATE(update_date)
                ''', user_id, chat_id
            )
            # Преобразование данных+
            dates = [record['date'] for record in records]
            counts = [record['message_count'] for record in records]
            return dates, counts

    async def get_message_count_by_chat(self, chat_id: int):
        async with self.pool.acquire() as conn:
            records = await conn.fetch(
                '''
                SELECT DATE(update_date) as date, COUNT(*) as message_count
                FROM messages
                WHERE  chat_id = $1
                AND update_date >= NOW() - INTERVAL '30 days'
                GROUP BY DATE(update_date)
                ORDER BY DATE(update_date)
                ''', chat_id
            )
            # Преобразование данных+
            dates = [record['date'] for record in records]
            counts = [record['message_count'] for record in records]
            return dates, counts

    async def execute_script(self, path: str):
        async with self.pool.acquire() as conn:
            with open(path, 'r', encoding='utf-8') as file:
                sql_script = file.read()
                try:
                    await conn.execute(sql_script)
                    print(f"SQL {path} script has been executed successfully.")
                except Exception as e:
                    print(f"An error occurred: {e}")

async def close(self):
    if self.conn:
        await self.conn.close()
    if self.pool:
        await self.pool.close()

# Пример использования
