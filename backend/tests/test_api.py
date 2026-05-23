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
        self.assertGreaterEqual(len(payload["rpaJobs"]), 1)

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

    def test_rpa_job_submission_runs_backend_worker(self):
        response = self.client.post(
            "/api/rpa/jobs",
            json={"accountId": "OPS-001", "action": "refresh_holdings", "operator": "Demo User"},
        )

        self.assertEqual(response.status_code, 201)
        payload = response.get_json()["data"]
        self.assertEqual(payload["accountId"], "OPS-001")
        self.assertEqual(payload["status"], "Queued")
        self.assertGreater(len(payload["steps"]), 0)

    def test_rpa_job_blocks_paused_account(self):
        response = self.client.post(
            "/api/rpa/jobs",
            json={"accountId": "OPS-003", "action": "refresh_holdings"},
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["data"]["status"], "Blocked")


if __name__ == "__main__":
    unittest.main()
