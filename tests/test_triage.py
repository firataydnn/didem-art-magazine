import json
import pathlib
import sys
import unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
from triage_art_news import canonical, tokens, score
import datetime as dt

class TestTriage(unittest.TestCase):
    def test_tracking_parameters(self):
        self.assertEqual(canonical("https://www.example.org/a/?utm_source=x&b=1#frag"),"https://example.org/a?b=1")
    def test_tokens(self):
        self.assertIn("museum",tokens("The Museum opens a new exhibition"))
    def test_scoring(self):
        now=dt.datetime(2026,10,16,tzinfo=dt.timezone.utc)
        self.assertGreater(score({"title":"Museum acquisition","published":"2026-10-16T00:00:00+00:00","source":"x"},now),score({"title":"Something else","published":"2026-09-01T00:00:00+00:00"},now))

if __name__=="__main__": unittest.main()
