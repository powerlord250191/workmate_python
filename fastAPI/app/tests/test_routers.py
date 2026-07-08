import pytest


class TestRouters:

    @pytest.mark.asyncio
    async def test_get_last_trading_dates(self, client, populated_db):
        response = await client.get("/last_trading_dates?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["trading_date"] == "2024-01-16"
        assert data[1]["trading_date"] == "2024-01-15"

        incorrect_response = await client.get("/last_trading_dates")
        assert incorrect_response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_dynamics(self, client, populated_db):
        response = await client.get(
            "/dynamics?start_date=2024-01-15&end_date=2024-01-16&oil_id=A100"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(r["oil_id"] == "A100" for r in data)

        response = await client.get(
            "/dynamics?start_date=2024-01-15&end_date=2024-01-16"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

        incorrect_response = await client.get(
            "/dynamics?start_date=2024-01-15"
        )
        assert incorrect_response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_trading_results(self, client, populated_db):
        response = await client.get("/trading_results")
        data = response.json()
        assert len(data) == 1

        response = await client.get("/trading_results?oil_id=A100")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["oil_id"] == "A100"

        response = await client.get("/trading_results?delivery_type_id=F")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert all(res["delivery_type_id"] == "F" for res in data)

        response = await client.get("/trading_results?delivery_basis_id=NVY")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert all(res["delivery_basis_id"] == "NVY" for res in data)

    @pytest.mark.asyncio
    async def test_health_check(self, client):
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_not_found(self, client):
        response = await client.get("/not-exists")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_root_routers(self, client):
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Spimex Trading API"