TOKEN = "5452719544:AAFLpPzKYYUMPxwsMJPrWi4jOGezkiNQlBs"
if TOKEN is None:
    TOKEN = input("Enter your bot TOKEN: ")
USER = 'postgres'
if USER is None:
    USER = input("Enter your database username: ")
PASSWORD = 3454325
if PASSWORD is None:
    PASSWORD = input("Enter your postgres password: ")

HOST = 'localhost'
if HOST is None:
    HOST = input("Enter your database address: ")
DATABASE = 'SocioConnection'
if DATABASE is None:
    DATABASE = input("Enter your database database name: ")

DATABASE_URL = f'postgres://{USER}:{PASSWORD}@{HOST}/{DATABASE}?'
MEDIA_STORAGE = 'media/'
db_credentials = {
    'user': USER,
    'password': PASSWORD,
    'database': DATABASE,
    'host': HOST,  # Например, 'localhost' или IP-адрес
    # 'port': 5432,  # Необязательно, если используется стандартный порт
}
VOICE_SRORAGE = 'voice/'
GRAPH_STORAGE = 'graph/'
