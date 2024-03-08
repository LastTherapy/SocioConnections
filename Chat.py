import DatabaseClient


class ChatCache:
    def __init__(self, dbclient: DatabaseClient):
        self.cache = {}  # Используется для хранения данных чатов
        self.db_client = dbclient  # Клиент базы данных

    async def load_from_database(self):
        pass

    async def is_chat_present(self, chat_id):
        # Проверяем кэш
        if chat_id in self.cache:
            return True

        # Проверяем базу данных, если чата нет в кэше
        chat_exists = await self.db_client.check_chat_exists(chat_id)

        # Обновляем кэш, если чат существует
        if chat_exists:
            self.cache[chat_id] = True

        return chat_exists