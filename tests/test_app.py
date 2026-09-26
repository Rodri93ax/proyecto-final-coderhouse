import unittest

from app import app
from prometheus_client.parser import text_string_to_metric_families


class AppTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_home(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["version"], "1.0.0")

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "ok"})

    def test_not_found(self):
        response = self.client.get("/ruta-inexistente")
        self.assertEqual(response.status_code, 404)

    def test_metrics_count_requests(self):
        def read_count():
            response = self.client.get("/metrics")
            self.assertEqual(response.status_code, 200)
            for family in text_string_to_metric_families(
                response.get_data(as_text=True)
            ):
                for sample in family.samples:
                    if (
                        sample.name == "app_requests_total"
                        and sample.labels == {
                            "endpoint": "health", "status": "200"
                        }
                    ):
                        return sample.value
            return 0

        before = read_count()
        self.client.get("/health")
        self.assertEqual(read_count(), before + 1)


if __name__ == "__main__":
    unittest.main()
