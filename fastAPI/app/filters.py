from models import SpimexTradingResult


def filtered_trading_results(
        oil_id: str | None = None,
        delivery_type_id: str | None = None,
        delivery_basis_id: str | None = None,
) -> list:

    conditions = []

    if oil_id:
        conditions.append(SpimexTradingResult.oil_id == oil_id)
    if delivery_type_id:
        conditions.append(SpimexTradingResult.delivery_type_id == delivery_type_id)
    if delivery_basis_id:
        conditions.append(SpimexTradingResult.delivery_basis_id == delivery_basis_id)

    return conditions