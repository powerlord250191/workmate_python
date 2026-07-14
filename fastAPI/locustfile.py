from locust import HttpUser, task, between
from random import choice, randint


class TradingAPIUser(HttpUser):
    # Пауза между задачами (имитация реального пользователя)
    wait_time = between(0.5, 2.0)

    @task(3)  # вес 3 — выполняется чаще
    def get_last_trading_dates(self):
        limit = randint(5, 30)
        self.client.get(f"/last_trading_dates?limit={limit}", name="/last_trading_dates")

    @task(2)
    def get_dynamics(self):
        dates = (
            ("2024-05-18", "2024-06-11"),
            ("2023-01-10", "2023-03-01"),
            ("2025-08-05", "2025-09-01"),
            ("2024-08-05", "2024-09-01"),
            ("2023-08-05", "2023-09-01"),
            ("2024-10-05", "2024-11-01"),
            ("2023-01-02", "2023-06-01"),
            ("2024-11-05", "2024-12-01"),
            ("2023-03-15", "2023-04-06"),
        )
        start_date = choice(dates)[0]
        end_date = choice(dates)[1]
        oil_ids = ["A100", "A692", None]
        oil_id = choice(oil_ids)
        params = f"start_date={start_date}&end_date={end_date}"
        if oil_id:
            params += f"&oil_id={oil_id}"
        self.client.get(f"/dynamics?{params}", name="/dynamics")

    @task(1)
    def get_trading_results(self):
        oil_id = choice(["A100", "A692", None])
        params = f"oil_id={oil_id}" if oil_id else ""
        self.client.get(f"/trading_results?{params}", name="/trading_results")

    @task(1)
    def health_check(self):
        self.client.get("/health", name="/health")