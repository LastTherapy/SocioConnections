import DatabaseClient
users = {}

class User:
    def __init__(self, user_id: int, anon_chats: list):
        self.user_id = user_id
        self.is_admin = False
        self.is_moderator = False
        self.anon_chats: list = anon_chats
        self.all_chats: dict = {}


async def create_user(user_id: int, anon_chats):
    user = User(user_id, anon_chats)
    users[user_id] = user
    return user


async def get_user(user_id: int):
    return users[user_id]