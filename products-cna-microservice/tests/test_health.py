"""Health and readiness, plus the request id every response carries."""


class TestHealth:
    async def test_health_reports_the_database(self, api):
        response = await api.get("/health")

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert body["service"] == "product-service"
        assert body["dependencies"] == {"postgresql": "up"}

    async def test_ready_says_the_service_can_serve(self, api):
        response = await api.get("/ready")

        assert response.status_code == 200
        assert response.json() == {"ready": True}

    async def test_every_response_carries_a_request_id(self, api):
        response = await api.get("/ready")
        assert response.headers["x-request-id"]

    async def test_an_incoming_request_id_is_kept(self, api):
        response = await api.get("/ready", headers={"X-Request-Id": "trace-me-123"})
        assert response.headers["x-request-id"] == "trace-me-123"
