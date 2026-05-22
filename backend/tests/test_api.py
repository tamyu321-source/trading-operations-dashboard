import unittest

from backend.app import create_app


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()

    def test_dashboard_payload_contains_core_sections(self):
        response = self.client.get("/api/dashboard")

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()["data"]
        self.assertGreater(payload["summary"]["totalEquity"], 0)
        self.assertEqual(len(payload["accounts"]), 4)
        self.assertEqual(len(payload["holdings"]), 6)
        self.assertEqual(len(payload["strategies"]), 2)
        self.assertEqual(len(payload["logs"]), 4)
        self.assertEqual(len(payload["servers"]), 3)

    def test_account_filter_uses_public_demo_status(self):
        response = self.client.get("/api/accounts?status=Active")

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()["data"]
        self.assertEqual(len(payload), 2)
        self.assertTrue(all(item["status"] == "Active" for item in payload))

    def test_strategy_profile_update_changes_demo_config(self):
        response = self.client.post(
            "/api/strategies/strategy-a",
            json={"maxSingleNameExposure": 20, "rebalanceWindow": "10:00-12:00"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()["data"]
        self.assertEqual(payload["maxSingleNameExposure"], 20)
        self.assertEqual(payload["rebalanceWindow"], "10:00-12:00")


if __name__ == "__main__":
    unittest.main()
