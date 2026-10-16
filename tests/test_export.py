import pathlib,sqlite3,tempfile,json,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"scripts"))
from export_approved_stories import export,ROOT
class ExportTests(unittest.TestCase):
 def test_unapproved_not_exported(self):
  with tempfile.TemporaryDirectory() as d:
   db=pathlib.Path(d)/"test.db";out=pathlib.Path(d)/"out.json"
   c=sqlite3.connect(db);c.executescript((ROOT/"database/schema.sql").read_text())
   c.execute("INSERT INTO stories(id,title,body,status,slug) VALUES(?,?,?,?,?)",("x","Draft","test "*150,"draft","draft"))
   c.execute("INSERT INTO assets(id,story_id,source_url,credit,license,rights_status) VALUES(?,?,?,?,?,?)",("a","x","https://example.org/img.jpg","Artist","CC0","verified"))
   c.commit();c.close();export(db,out)
   self.assertEqual(json.loads(out.read_text())["count"],0)
if __name__=="__main__":unittest.main()
