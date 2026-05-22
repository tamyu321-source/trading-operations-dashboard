import unittest
from time import sleep

from backend.app import create_app


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()

    def test_dashboard_payload_contains_core_sections(self):
        response = self.client.get("/api/dashboard")

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()["data"]
        self.assertGreater(payload["summary"]["totalEquity"], 0)
        self.assertEqual(len(payload["accounts"]), 3)
        self.assertEqual(len(payload["positions"]), 4)
        self.assertEqual(len(payload["riskEvents"]), 3)
        self.assertEqual(len(payload["executions"]), 4)

    def test_strategy_toggle_updates_state(self):
        response = self.client.post("/api/strategies/manual-review/toggle", json={"enabled": True})

        self.assertEqual(response.status_code, 200)
        self.assertIs(response.get_json()["data"]["enabled"], True)

    def test_rpa_command_submission_records_audited_task(self):
        response = self.client.post(
            "/api/rpa/commands",
            json={"accountId": "SG-ALPHA", "action": "refresh_positions", "operator": "Demo User"},
        )

        self.assertEqual(response.status_code, 201)
        payload = response.get_json()["data"]
        self.assertEqual(payload["accountId"], "SG-ALPHA")
        self.assertEqual(payload["status"], "Queued")
        self.assertGreater(len(payload["steps"]), 0)

        command_id = payload["id"]
        completed = None
        for _ in range(20):
            commands = self.client.get("/api/rpa/commands").get_json()["data"]
            completed = next(item for item in commands if item["id"] == command_id)
            if completed["status"] == "Completed":
                break
            sleep(0.1)

        self.assertEqual(completed["status"], "Completed")
        self.assertEqual(completed["progress"], 100)
        self.assertTrue(completed["artifactUrl"].endswith("_holdings.csv"))
        self.assertGreater(len(completed["logs"]), 2)

    def test_rpa_command_blocks_paused_account_for_active_workflow(self):
        response = self.client.post(
            "/api/rpa/commands",
            json={"accountId": "HK-DELTA", "action": "sync_orders"},
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["data"]["status"], "Blocked")


if __name__ == "__main__":
    unittest.main()
