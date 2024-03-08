import os
import asyncio
import asyncpg
from settings import DATABASE_URL

async def add_tag_and_images(pool, tag_path):
    async with pool.acquire() as connection:
        # Добавляем информацию о теге
        tag_name = os.path.basename(tag_path)
        tag = await connection.fetchrow('INSERT INTO tags (name) VALUES ($1) RETURNING id', tag_name)

        # Проходим по всем изображениям в теге и добавляем информацию о них
        for image_name in os.listdir(tag_path):
            image_path = os.path.join(tag_path, image_name)
            if os.path.isfile(image_path):
                await connection.execute('INSERT INTO images (name, tag_id) VALUES ($1, $2)', image_name, tag['id'])

async def main():

    pool = await asyncpg.create_pool(DATABASE_URL)

    root_folder = 'media/'  # Путь к вашей директории
    for folder_name in os.listdir(root_folder):
        folder_path = os.path.join(root_folder, folder_name)
        if os.path.isdir(folder_path):
            await add_tag_and_images(pool, folder_path)

if __name__ == '__main__':
    asyncio.run(main())
