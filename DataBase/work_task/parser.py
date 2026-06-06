import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from typing import Optional

BASE_URL = "https://spimex.com"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}


def get_bulletins(soup) -> list[dict[str, Optional[str]]]:
    """Парсит ссылки на бюллетени со страницы итогов торгов"""

    # Ищем ссылки с классом "accordion-inner_item-title link pdf"
    # Используем CSS selector
    links_pdf = soup.select('.accordeon-inner__item-title.link.pdf')
    links_xls = soup.select('.accordeon-inner__item-title.link.xls')

    bulletins = []

    for link in links_pdf:
        href = link.get('href')
        if not href:
            continue
        # Преобразуем относительный путь в абсолютный
        full_url = urljoin(BASE_URL, href)

        filename = href.split('/')[-1].split('?')[0]

        bulletins.append({
            'url': full_url,
            'filename': filename
        })

    for link in links_xls:
        href = link.get('href')
        if not href:
            continue
        # Преобразуем относительный путь в абсолютный
        full_url = urljoin(BASE_URL, href)

        # Извлекаем имя файла
        filename = href.split('/')[-1].split('?')[0]

        bulletins.append({
            'url': full_url,
            'filename': filename
        })

    return bulletins


def download_bulletin(bulletin: dict, save_dir: str = "bulletins") -> str:
    """Скачивает PDF/xls-файл бюллетеня"""

    os.makedirs(save_dir, exist_ok=True)

    filename = bulletin['filename']

    filepath = os.path.join(save_dir, filename)

    if os.path.exists(filepath):
        return filepath

    filepath = os.path.join(save_dir, filename)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    response = requests.get(bulletin['url'], headers=headers)
    response.raise_for_status()

    with open(filepath, 'wb') as f:
        f.write(response.content)

    return filepath


def start_parsing_bilutens():
    import time

    prefix = "/markets/oil_products/trades/results/"
    start_url = f"{BASE_URL}/{prefix}"

    response = requests.get(start_url, headers=HEADERS)
    response.raise_for_status()
    worker = BeautifulSoup(response.text, 'html.parser')

    pagination_items = worker.select('.bx-pagination-container li a')
    max_page = 59

    for item in pagination_items:
        text = item.get_text(strip=True)
        if text.isdigit():
            page_num = int(text)

    # Собираем бюллетени со всех страниц
    all_bulletins = []

    for page_num in range(1, max_page + 1):
        if page_num == 1:
            current_url = start_url
        else:
            current_url = f"{start_url}?page=page-{page_num}"

        response = requests.get(current_url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        bulletins = get_bulletins(soup)

        all_bulletins.extend(bulletins)

        for bulletin in bulletins:
            try:
                path = download_bulletin(bulletin)
            except Exception as e:
                print(f"Ошибка при скачивании {path}: {e}")

        time.sleep(2)  # Задержка между страницами

    print(f"\nВсего собрано бюллетеней: {len(all_bulletins)}")
