"""Regression checks for ATELIER's automated, non-publishing editorial triage."""
import datetime as dt
import pathlib
import sys
import unittest

sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"scripts"))
import editorial_agent as e

def story(title, date="2026-10-30T12:00:00+00:00"):
 return {"title":title,"published_at":date,"source":"ARTnews","url":"https://example.org/test"}

class EditorialTests(unittest.TestCase):
 def test_major_institution(self):
  self.assertEqual(e.classify("Centre Pompidou, MoMA, And M+ Announce New Cultural Alliance","DÜNYA"),"KURUMLAR")
 def test_artist_not_crime_category(self):
  self.assertEqual(e.classify("Photographer Pipo Nguyen-duy Found Dead, According to Police","DÜNYA"),"SANATÇILAR")
 def test_duplicate_alliance(self):
  a=story("Centre Pompidou, MoMA, And M+ Announce New Cultural Alliance")
  b=story("MoMA, Centre Pompidou, and M+ Form an Unprecedented Alliance")
  self.assertTrue(e.near_duplicate(a,b))
 def test_distinct_events_do_not_merge(self):
  a=story("MoMA Announces Photography Exhibition")
  b=story("MoMA Announces New Photography Director")
  self.assertFalse(e.near_duplicate(a,b))
 def test_date_boundary(self):
  a=story("Centre Pompidou MoMA Cultural Alliance")
  b=story("MoMA and Centre Pompidou Cultural Alliance", "2026-10-23T12:00:00+00:00")
  self.assertFalse(e.near_duplicate(a,b))
 def test_ranking_prefers_institutional_news(self):
  now=dt.datetime.fromisoformat("2026-10-30T14:00:00+00:00")
  a=story("MoMA and Pompidou announce new alliance")
  b=story("Ten must-see art guides in October")
  self.assertGreater(e.rank(a,now)[0],e.rank(b,now)[0])

if __name__=="__main__":unittest.main()
