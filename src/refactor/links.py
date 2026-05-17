import datetime
from datetime import date

from bs4 import BeautifulSoup

#TODO рекомендуется добавить логирование и документирование


DEFAULT_BASE_URL: str = "https://spimex.com"
PATH_BASE: str = "/upload/reports/oil_xls/oil_xls_"
EXTENSION: str = ".xls"
DATE_FORMAT: str = "%Y%m%d"
LINK_CLASS: str = "accordeon-inner__item-title link xls"


class ParseLinkException(Exception):
    """Исключение для ошибок парсинга ссылки"""
    pass


def is_valid_links(links: list[str]) -> list[str]:
    cleaned_links: list = []
    for link in links:
        href: str = link.get("href").split("?")[0]
        if not href:
            continue
        if not check_href(href):
            continue
        cleaned_links.append(link)
    return cleaned_links


def check_href(href: str) -> bool:
    if PATH_BASE not in href or not href.endswith(EXTENSION):
        return False
    return True


def parse_page_links(html: str, start_date: date, end_date: date):  # url зачем ?
    """
    Парсит ссылки на бюллетени с одной страницы:
    <a class="accordeon-inner__item-title link xls" href="/upload/reports/oil_xls/oil_xls_20240101_test.xls">link1</a>
    """
    results: list = []
    soup: BeautifulSoup = BeautifulSoup(html, "html.parser")
    links: list[str] = is_valid_links(soup.find_all("a", class_=LINK_CLASS))

    for link in links:
        try:
            date: str = link.split("oil_xls_")[1][:8]  # здесь по идее должен быть вот такой срез [0][:8]
            file: date = datetime.datetime.strptime(date, DATE_FORMAT).date()
            if start_date <= file <= end_date:
                u: str = link if link.startswith("http") else f"{DEFAULT_BASE_URL}{link}"
                results.append((u, file))
            else:
                print(f"Ссылка {link} вне диапазона дат")
        except ParseLinkException as e:
            print(f"Не удалось извлечь дату из ссылки {link}: {e}")

    return results
