import matplotlib.pyplot as plt
import os
import asyncio
from datetime import datetime

def get_day_of_week(date_str):
    # Перевод английских сокращений в русские
    days = {
        'Mon': 'пн',
        'Tue': 'вт',
        'Wed': 'ср',
        'Thu': 'чт',
        'Fri': 'пт',
        'Sat': 'сб',
        'Sun': 'вс'
    }
    date_obj = datetime.strptime(date_str, '%d.%m.%y')
    return days[date_obj.strftime('%a')]


async def plot_message_count_graph(dates, counts, user_name, chat_name):
    # Преобразование дат в строки с новым форматом
    dates = [date.strftime('%d.%m.%y') for date in dates]
    weekdays = [get_day_of_week(date) for date in dates]

    # Создание директории для графиков
    directory = "graphs"
    if not os.path.exists(directory):
        os.makedirs(directory)
    # Создание графика
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(dates, counts, color='#42AAFF')
    # Добавление текста к каждому столбцу
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval, str(int(yval)), ha='center', va='bottom')

    plt.title(f"Количество сообщений пользователя {user_name} в чате {chat_name} за последние 30 дней")

        # Настройка основной оси X (даты)
    ax.set_xticks(range(len(dates)))
    ax.set_xticklabels(dates, rotation=45)
        # Добавление второй оси X для дней недели внизу
    ax2 = ax.twiny()  # Создаем вторичную ось
    ax2.xaxis.set_ticks_position('bottom')  # Ставим ось снизу
    ax2.xaxis.set_label_position('bottom')  # Позиционируем метку оси снизу
    ax2.spines['bottom'].set_position(('outward', 40))  # Смещаем ось ниже
    ax2.set_xticks(range(len(weekdays)))
    ax2.set_xticklabels(weekdays)
    ax2.set_xlim(ax.get_xlim())  # Устанавливаем те же пределы, что и у основной оси

        # Сделать линии оси ax2 невидимыми
    ax2.spines['bottom'].set_visible(False)
    # Удаление линий вторичной оси X
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    ax2.spines['bottom'].set_visible(False)  # Также убираем нижнюю линию вторичной оси X

    # Удаление меток с левой стороны графика (ось Y)
    ax.set_yticklabels([])

        # Удаление лишних осей и рамок оси ax
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('#dddddd')
    ax.tick_params(left=False)

    plt.tight_layout()
        # Сохранение графика
    file_path = os.path.join(directory, f"message_count_{user_name}.png")
    plt.savefig(file_path)
    plt.close()

    return file_path

async def plot_message_count_chat(dates, counts, chat_name):
        # Преобразование дат в строки с новым форматом
        dates = [date.strftime('%d.%m.%y') for date in dates]
        weekdays = [get_day_of_week(date) for date in dates]

        # Создание директории для графиков
        directory = "graphs"
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Создание графика
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(dates, counts, color='#FFA500')  # Здесь изменен цвет на оранжевый

        # Добавление текста к каждому столбцу
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, yval, str(int(yval)), ha='center', va='bottom')

        plt.title(f"Количество сообщений в чате {chat_name} за последние 30 дней")

        # Настройка основной оси X (даты)
        ax.set_xticks(range(len(dates)))
        ax.set_xticklabels(dates, rotation=45)

        # Добавление второй оси X для дней недели
        ax2 = ax.twiny()
        ax2.xaxis.set_ticks_position('bottom')
        ax2.xaxis.set_label_position('bottom')
        ax2.spines['bottom'].set_position(('outward', 40))
        ax2.set_xticks(range(len(weekdays)))
        ax2.set_xticklabels(weekdays)
        ax2.set_xlim(ax.get_xlim())

        # Рассчитываем среднее количество сообщений
        average_count = sum(counts) / len(counts) if counts else 0
        # Добавление горизонтальной пунктирной линии для среднего количества сообщений
        plt.axhline(y=average_count, color='gray', linestyle='--', linewidth=1)

        # Удаление лишних осей и рамок
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_color('#dddddd')
        ax.tick_params(left=False)
        ax2.spines['bottom'].set_visible(False)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['left'].set_visible(False)

        # Удаление меток оси Y
        ax.set_yticklabels([])

        plt.tight_layout()
        # Сохранение графика
        file_path = os.path.join(directory, f"message_count_{chat_name}.png")
        plt.savefig(file_path)
        plt.close()
        return file_path


async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    # And the run events dispatching
    dbclient = DatabaseClient.DatabaseClient()
    await dbclient.create_pool()
    dates, counts = await dbclient.get_message_count_by_chat(-1001990350502)
    print(dates, counts)
    await plot_message_count_chat(dates, counts, chat_name="cat chance")

if __name__ == "__main__":
    import DatabaseClient
    asyncio.run(main())



