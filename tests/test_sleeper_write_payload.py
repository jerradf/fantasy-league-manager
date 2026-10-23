import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from api_client import SleeperClient


class TestSleeperWritePayload(unittest.TestCase):
    def test_waiver_payload_shape_mocked(self):
        client = SleeperClient()
        with patch.object(SleeperClient, "_post", return_value={"ok": True}) as mock_post:
            result = client.post_waiver_add("league123", "8", "playerA", "playerB", "FAKE_COOKIE_FOR_TEST_ONLY")
        self.assertEqual(result, {"ok": True})
        endpoint, payload, cookie = mock_post.call_args.args
        self.assertEqual(endpoint, "league/league123/transactions")
        self.assertEqual(payload["type"], "waiver")
        self.assertEqual(payload["adds"], {"playerA": "8"})
        self.assertEqual(payload["drops"], {"playerB": "8"})
        self.assertEqual(cookie, "FAKE_COOKIE_FOR_TEST_ONLY")

    def test_read_only_roster_lookup_mocked(self):
        client = SleeperClient()
        with patch.object(SleeperClient, "_get", return_value=[{"roster_id": 8, "players": []}]):
            roster = client.get_roster("league123", "8")
        self.assertEqual(roster["roster_id"], 8)


if __name__ == "__main__":
    unittest.main()
