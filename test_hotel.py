import concurrent.futures, hashlib, http.client, importlib, io, json, os, pathlib, subprocess, sys, tempfile, threading, unittest, zipfile

temp = tempfile.TemporaryDirectory()
os.environ["HOTEL_DATA"] = temp.name
import server

class HotelFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.http = server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        cls.port = cls.http.server_address[1]
        threading.Thread(target=cls.http.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown()
        cls.http.server_close()

    def req(self, path, data=None, owner="a"*64, origin=None):
        c = http.client.HTTPConnection("127.0.0.1", self.port)
        headers = {"Cookie": "hotel_owner="+owner}
        if data is not None: headers["Content-Type"] = "application/json"
        if origin: headers["Origin"] = origin
        c.request("POST" if data is not None else "GET", "/agents/api/"+path, json.dumps(data) if data is not None else None, headers)
        res=c.getresponse(); raw=res.read(); typ=res.getheader("Content-Type"); status=res.status
        c.close()
        return status, json.loads(raw) if typ == "application/json" else raw

    def create(self, **kw):
        status, room=self.req("checkin",dict(name="Validation Guest", budget=8, **kw))
        self.assertEqual(status,201)
        return room

    def act(self, room, action, **kw):
        status,r=self.req("action",dict(id=room["id"],action=action,**kw))
        self.assertEqual(status,200,r)
        return r

    def test_full_stay_export_privacy_and_rollback(self):
        r=self.create()
        self.assertEqual(self.req("action",{"id":r["id"],"action":"verify"})[0],400)
        self.assertEqual(self.req("action",{"id":r["id"],"action":"assess"},owner="b"*64)[0],403)
        r=self.act(r,"assess"); before=r["assessment"]["passed"]
        r=self.act(r,"pause")
        self.assertEqual(self.req("action",{"id":r["id"],"action":"improve"})[0],400)
        r=self.act(r,"resume"); r=self.act(r,"improve");r=self.act(r,"verify")
        self.assertGreater(r["verification"]["after"],r["verification"]["before"])
        self.assertEqual(r["verification"]["after"],12)
        self.assertEqual(r["verification"]["regressions"],0)
        r=self.act(r,"checkout"); cert=r["certificate"]
        self.assertEqual(self.req("certificates/"+cert,owner="b"*64)[0],404)
        self.assertEqual(self.req("export/"+r["id"],owner="b"*64)[0],403)
        status,blob=self.req("export/"+r["id"]);self.assertEqual(status,200)
        with tempfile.TemporaryDirectory() as dest:
            z=zipfile.ZipFile(io.BytesIO(blob));z.extractall(dest)
            p=pathlib.Path(dest)/"hotel_agent"
            result=subprocess.run([sys.executable,str(p/"runtime.py")], input='{"task":"slugify","input":"Crème Brûlée"}',text=True,capture_output=True,check=True)
            self.assertEqual(json.loads(result.stdout),"creme-brulee")
            manifest=json.loads((p/"manifest.json").read_text())
            self.assertEqual(manifest["config_sha256"],server.digest(r["config"]))
            (p/"agent.json").write_text((p/"rollback.json").read_text())
            result=subprocess.run([sys.executable,str(p/"runtime.py")],input='{"task":"slugify","input":"Crème Brûlée"}',text=True,capture_output=True,check=True)
            self.assertNotEqual(json.loads(result.stdout),"creme-brulee")
        r=self.act(r,"settings",public=True,notes="PRIVATE_NOTE")
        other=self.req("state",owner="b"*64)[1]
        self.assertNotIn("PRIVATE_NOTE",json.dumps(other))
        self.assertEqual(self.req("certificates/"+cert,owner="b"*64)[0],200)
        r=self.act(r,"rollback");self.assertIsNone(r["certificate"])
        self.assertEqual(r["config"],server.DEFAULT)

    def test_budget_and_assessment_only(self):
        r=self.create();r=self.act(r,"budget",budget=4);r=self.act(r,"assess")
        self.assertEqual(self.req("action",{"id":r["id"],"action":"improve"})[0],400)
        r=self.act(r,"budget",budget=8);r=self.act(r,"improve")
        r=self.create(mode="assess");r=self.act(r,"assess")
        self.assertEqual(self.req("action",{"id":r["id"],"action":"improve"})[0],400)
        r=self.act(r,"verify");r=self.act(r,"checkout");self.assertEqual(r["config"],server.DEFAULT)

    def test_inputs_origin_duplicate_actions(self):
        self.assertEqual(self.req("checkin",{"name":"x","config":{"unicode":"yes"}})[0],400)
        self.assertEqual(self.req("checkin",[])[0],400)
        self.assertEqual(self.req("checkin",{"name":"x"},origin="https://evil.example")[0],403)
        r=self.create()
        with concurrent.futures.ThreadPoolExecutor(2) as pool:
            results=list(pool.map(lambda _:self.req("action",{"id":r["id"],"action":"assess"})[0],range(2)))
        self.assertEqual(sorted(results),[200,400])

    def test_no_improvement(self):
        r=self.create(config={k:True for k in server.DEFAULT})
        for action in ("assess","improve","verify","checkout"):r=self.act(r,action)
        self.assertEqual(r["verification"]["before"],r["verification"]["after"])
        self.assertEqual(r["version"],1)

if __name__=="__main__": unittest.main(verbosity=2)
