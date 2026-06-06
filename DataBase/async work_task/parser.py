import asyncio
from time import time
from logging import getLogger, basicConfig, INFO, FileHandler
import aiohttp
import aiofiles
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from typing import Optional

BASE_URL = "https://spimex.com"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}


basicConfig(
    level=INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[FileHandler(filename='logs_parser.log')]
)

logger = getLogger(__name__)


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


async def download_bulletin(session: aiohttp.ClientSession, bulletin: dict,  save_dir: str = "bulletins") -> str:
    """Скачивает PDF/xls-файл бюллетеня"""

    os.makedirs(save_dir, exist_ok=True)

    filename = bulletin['filename']

    filepath = os.path.join(save_dir, filename)

    if os.path.exists(filepath):
        return filepath

    async with session.get(bulletin['url'], headers=HEADERS) as response:
        response.raise_for_status()
        content = await response.read()

        async with aiofiles.open(filepath, 'wb') as file:
            await file.write(content)

    return filepath


async def start_parsing_bulletins():

    prefix = "/markets/oil_products/trades/results/"
    start_url = f"{BASE_URL}/{prefix}"

    async with aiohttp.ClientSession() as session:
        async with session.get(start_url, headers=HEADERS) as response:
            response.raise_for_status()
            html = await response.text()
            worker = BeautifulSoup(html, "html.parser")

        # pagination_items = worker.select('.bx-pagination-container li a')
        max_page = 59

        # Собираем бюллетени со всех страниц
        all_bulletins = []

        for page_num in range(1, max_page + 1):
            if page_num == 1:
                current_url = start_url
            else:
                current_url = f"{start_url}?page=page-{page_num}"

            async with session.get(current_url, headers=HEADERS) as response:
                response.raise_for_status()
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                bulletins = get_bulletins(soup)

                all_bulletins.extend(bulletins)

                for bulletin in bulletins:
                    try:
                        path = await download_bulletin(session, bulletin)
                    except Exception as e:
                        logger.info(f"Ошибка при скачивании {path}: {e}")

            await asyncio.sleep(3)  # Задержка между страницами

    logger.info(f"\nВсего собрано бюллетеней: {len(all_bulletins)}")


# if __name__ == "__main__":
#     logger.info("Начинаем парсить билютени")
#     start = time()
#     asyncio.run(start_parsing_bulletins())
#     end = time()
#     logger.info(f"Закончили парсинг, общее время {round(end-start, 2)}")