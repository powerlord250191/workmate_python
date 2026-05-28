from datetime import datetime
from pprint import pprint

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import SpimexTradingResult
from initial_db import DATABASE_URL


engine = create_engine(DATABASE_URL, echo=False)


def create_list_object(dict_objects: dict[str]) -> list[SpimexTradingResult]:
    list_objects = []
    for item in dict_objects:
        list_objects.append(
            SpimexTradingResult(
                exchange_product_id=item["exchange_product_id"],
                exchange_product_name=item["exchange_product_name"],
                oil_id=item["exchange_product_id"][:4],
                delivery_basis_id=item["exchange_product_id"][4:7],
                delivery_basis_name=item["delivery_basis_name"],
                delivery_type_id=item["exchange_product_id"][-1],
                volume=item["volume"],
                total=item["total"],
                count=item["count"],
                date=item["date"],
                created_on=datetime.now(),
                updated_on=datetime.now(),
            )
        )

    return list_objects


def insert_data_to_database(data: dict[str]):
    data_objects = create_list_object(data)

    with Session(engine) as session:
        session.add_all(data_objects)
        session.commit()
