import asyncio
import os
from time import time
from logging import getLogger, basicConfig, INFO, FileHandler
from scripts import sync_engine
from parser import start_parsing_bulletins
from initial_db import initial_db
from reader import process_files_parallel
from scripts import insert_data_to_database


basicConfig(
    level=INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding="utf-8",
    handlers=[FileHandler(filename="main_logs.log")]
)

logger = getLogger(__name__)

if __name__ == '__main__':
    begin = time()
    logger.info(f"Начало выполнения программы - {round(begin, 6)}")
    # print(f"Начало выполнения программы - {round(begin, 6)}")
    initial_db(sync_engine)  # если запускаем первый раз, раскомментировать эту строчку

    asyncio.run(start_parsing_bulletins())   # если биллютени ещё не спарсены, вызываем эту функцию

    folder_path = "bulletins"
    if os.path.exists(folder_path) and os.listdir(folder_path):
        file_paths = [os.path.join(folder_path, filename) for filename in os.listdir(folder_path)]

        ready_to_insert_data = process_files_parallel(file_paths)
        asyncio.run(insert_data_to_database(ready_to_insert_data))

    end = time()
    logger.info(f"Конец работы программы время работы - {round(end - begin / 60, 6)}")
#     print(f"Конец работы программы время работы - {round(end - begin, 6)}")