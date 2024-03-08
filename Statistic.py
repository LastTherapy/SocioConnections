import matplotlib.pyplot as plt
import os
from datetime import datetime

async def plot_message_count_graph(dates, counts, user_name, chat_name):
    # Преобразование дат в строки с убраным годом
    dates = [date.strftime('%d.%m.%y') for date in dates]

    # Создание директории для графиков
    directory = "graphs"
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Создание графика
    plt.figure(figsize=(10, 6))
    bars = plt.bar(dates, counts, color='#42AAFF')

    # Добавление текста к каждому столбцу
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval, int(yval), ha='center', va='bottom')

    plt.title(f"Количество сообщений пользователя {user_name} в чате {chat_name} за последние 30 дней")

    # Удаление цифр (меток) с левой стороны графика (ось Y)
    plt.gca().set_yticklabels([])

    # Удаление рамки и осей
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['left'].set_visible(False)
    plt.gca().spines['bottom'].set_color('#dddddd')
    plt.gca().tick_params(left=False)  # Убираем деления на оси Y

    plt.xticks(rotation=45)
    plt.tight_layout()

    # Сохранение графика
    file_path = os.path.join(directory, f"message_count_{user_name}.png")
    plt.savefig(file_path)
    plt.close()

    return file_path

# async def plot_message_count_graph(dates, counts, user_name, chat_name):
#     # Создание директории для графиков, если она еще не существует
#     directory = "graphs"
#     if not os.path.exists(directory):
#         os.makedirs(directory)
#
#     # Создание графика
#     plt.figure(figsize=(10, 6))
#     plt.plot(dates, counts, marker='o')
#     for i, count in enumerate(counts):
#         plt.text(dates[i], counts[i], str(count), ha='center', va='bottom')
#
#     plt.title(f"Количество сообщений пользователя {user_name} в чате {chat_name} за последние 30 дней")
#     plt.xlabel("Дата")
#     plt.ylabel("Количество сообщений")
#     plt.xticks(rotation=45)
#     plt.tight_layout()
#
#     # Сохранение графика в файл
#     file_path = os.path.join(directory, f"message_count_{user_name}.png")
#     plt.savefig(file_path)
#     plt.close()  # Закрытие объекта plt, чтобы освободить память
#
#     return file_path
