from dataclasses import dataclass


@dataclass(frozen=True)
class Currency:
    currency: str
    symbol: str


rub = Currency(currency='Рубль', symbol="rub")
usd = Currency(currency='Доллар США', symbol="usd")
eur = Currency(currency='Евро', symbol="eur")
