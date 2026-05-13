class NegativeValueException(Exception):
    '''Нельзя установить отрицательный баланс кошелька'''
    pass


class NotComparisonException(Exception):
    """Нельзя складывать/вычитать разные типы валют"""
    pass
