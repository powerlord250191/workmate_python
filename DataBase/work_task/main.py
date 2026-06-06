import os
from time import time
from scripts import engine
from parser import start_parsing_bilutens
from initial_db import initial_db
from reader import reading_bulletin_by_text_xls,reading_bulletin_by_text_pdf
from scripts import insert_data_to_database

if __name__ == '__main__':
    print("Начало выполнения программы")
    begin = time()

    initial_db(engine)  # если запускаем первый раз, раскомментировать эту строчку

    start_parsing_bilutens()    # если биллютени ещё не спарсены, вызываем эту функцию

    folder_path = "bulletins"

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if filename.endswith(".pdf"):
            data_dict = reading_bulletin_by_text_pdf(file_path)
        elif filename.endswith(".xls"):
            data_dict = reading_bulletin_by_text_xls(file_path)
        else:
            continue

        insert_data_to_database(data=data_dict)

    end = time()
    print(f"Конец работы программы время работы - {round(end - begin, 2)}")