from dataclasses import dataclass, field
from .currency import Currency, rub
from .exceptions import NegativeValueException, NotComparisonException


@dataclass(frozen=True)
class Money:
    value: float
    currency: Currency

    def __post_init__(self):
        if self.value < 0:
            raise NegativeValueException(
                f"Нельзя создать кошелёк с отрицательным балансом: {self.value}"
            )

    def __add__(self, other: "Money"):
        if self.currency != other.currency:
            raise NotComparisonException(
                f"нельзя складывать валюты {self.currency} "
                f"и {other.currency} между собой"
            )
        return Money(self.value + other.value, self.currency)

    def __sub__(self, other: "Money"):
        if self.currency != other.currency:
            raise NotComparisonException(
                f"нельзя вычитать валюту {self.currency} "
                f"из валюты {other.currency} "
            )
        if self.value - other.value < 0:
            raise NegativeValueException(
                f"Недостаточно средств для вычитания, "
                f"баланс после операции не может быть отрицательным"
            )
        return Money(self.value - other.value, self.currency)


@dataclass
class Wallet:
    _money: dict[Currency, Money] = field(default_factory=dict, init=False, repr=False)

    @classmethod
    def from_moneys(cls, *args: Money) -> "Wallet":
        wallet = cls()
        for money in args:
            wallet._money[money.currency] = money
        return wallet

    # Поддерживаем старый интерфейс для обратной совместимости
    def __init__(self, *args: Money):
        self._money = {}
        for money in args:
            self._money[money.currency] = money

    def __getitem__(self, item: Currency) -> Money:
        if item in self._money:
            return self._money[item]
        return Money(0, item)

    def __setitem__(self, key: Currency, money: Money) -> None:
        if money.value < 0:
            raise NegativeValueException("нельзя установить отрицательный баланс")
        if money.value == 0:
            if key in self._money:
                del self._money[key]
        else:
            self._money[key] = money

    def __delitem__(self, key: Currency) -> None:
        self._money.pop(key, None)

    def __len__(self) -> int:
        return len(self._money)

    def __contains__(self, item: Currency) -> bool:
        return item in self._money

    @property
    def currencies(self) -> set:
        return set(self._money.keys())

    def add(self, money: Money) -> "Wallet":
        # print(f"DEBUG add: before = {self[money.currency].value}")
        current = self[money.currency]
        new_value = current.value + money.value
        self[money.currency] = Money(new_value, money.currency)
        #         print(f"DEBUG add: after = {self[money.currency].value}")
        return self

    def sub(self, money: Money) -> "Wallet":
        #         print(f"DEBUG sub: before = {self[money.currency].value}")
        current = self[money.currency]
        if current.value < money.value:
            raise NegativeValueException(
                f"Невозможно провести операцию списания, недостаточно средств"
            )
        new_value = current.value - money.value
        if new_value == 0:
            del self[money.currency]
        else:
            self[money.currency] = Money(new_value, money.currency)
        #         print(f"DEBUG sub: after = {self[money.currency].value}")
        return self

    def __repr__(self):
        currencies = ", ".join(f"{c.symbol}: {m.value}" for c, m in self._money.items())
        return f"Wallet{currencies}"
