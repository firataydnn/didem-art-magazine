#!/usr/bin/env python3
"""Push research leads to Didem Supabase private editorial schema via PostgREST RPC.
Requires server-only GitHub Actions secret DIDEM_SUPABASE_SERVICE_ROLE_KEY.
Never publishes, approves or modifies stories."""
import json,os,pathlib,sys,urllib.request,urllib.error
ROOT=pathlib.Path(__file__).resolve().parents[1]
PROJECT="atjbktwtcveaibwuixfa"
URL=f"https://{PROJECT}.supabase.co/rest/v1/rpc/ingest_didem_radar"
# The project API endpoint requires PostgREST to expose the public RPC.
# A workflow push to this script runs an end-to-end sync test.
def sync():
    key=os.environ.get("DIDEM_SUPABASE_SERVICE_ROLE_KEY","").strip()
    if not key:
        print("No Supabase service key configured; skipping private sync.")
        return 0
    payload=json.loads((ROOT/"editorial/radar/triage.json").read_text(encoding="utf-8")).get("items",[])
    total=0
    for start in range(0,len(payload),200):
        batch=payload[start:start+200]
        req=urllib.request.Request(URL,data=json.dumps(batch).encode("utf-8"),
            headers={"apikey":key,"Authorization":"Bearer "+key,"Content-Type":"application/json",
                     "Accept":"application/json"},method="POST")
        try:
            with urllib.request.urlopen(req,timeout=40) as response:
                result=json.load(response)
            total+=result.get("processed",0)
        except urllib.error.HTTPError as exc:
            print("Supabase sync failed: HTTP",exc.code,file=sys.stderr)
            try:
                details=json.loads(exc.read(4096).decode("utf-8","replace"))
                print("PostgREST error:",details.get("code","unknown"),str(details.get("message",""))[:400],file=sys.stderr)
            except (ValueError,UnicodeError):
                print("Response was not JSON",file=sys.stderr)
            return 1
    print("Supabase research leads synced:",total,"(all unapproved)")
    return 0
if __name__=="__main__":sys.exit(sync())
