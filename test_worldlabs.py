import json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import worldlabs, worldlabs_admin as admin

def world():
    return {'id':'12345678-1234-1234-1234-123456789abc','model':'marble-1.1','world_prompt':{'text_prompt':'PRIVATE PROMPT'},
        'assets':{'splats':{'spz_urls':{'100k':'https://cdn.marble.worldlabs.ai/test.spz?signature=PRIVATE'},
        'semantics_metadata':{'metric_scale_factor':1.5,'ground_plane_offset':.2}},'mesh':{}}}

class WorldLabsBoundary(unittest.TestCase):
    def test_private_api_metadata_never_published(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); dest=root/'assets/worldlabs'
            def download(url,path): path.write_bytes(b'fixture-not-a-real-world')
            with patch.object(admin,'download',side_effect=download):
                admin.publish(world(),dest,'Published world')
            data=worldlabs.active(root)
            self.assertEqual(data['status'],'ready')
            self.assertEqual(data['semantics']['metric_scale_factor'],1.5)
            self.assertNotIn('PRIVATE',json.dumps(data))
            self.assertNotIn('signature',(dest/'active.json').read_text())
            self.assertNotIn('world_prompt',(dest/'active.json').read_text())

    def test_bad_manifest_and_external_assets_fail_closed(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); dest=root/'assets/worldlabs';dest.mkdir(parents=True)
            self.assertEqual(worldlabs.active(root)['status'],'awaiting_world')
            for value in ('../../server.py','https://evil.example/file.spz','/etc/shadow'):
                admin.write_json(dest/'active.json',{'format':'hotel-marble/1','splat':value})
                self.assertEqual(worldlabs.active(root)['status'],'unavailable')
        for url in ('http://cdn.marble.worldlabs.ai/a','https://127.0.0.1/a','https://cdn.marble.worldlabs.ai.evil.test/a',
                    'https://cdn.marble.worldlabs.ai:22/a','https://user:pass@cdn.marble.worldlabs.ai/a'):
            with self.assertRaises(ValueError): admin.asset_url(url)
        self.assertEqual(admin.asset_url('https://cdn.marble.worldlabs.ai/a.spz'),'https://cdn.marble.worldlabs.ai/a.spz')

    def test_missing_or_nonfinite_scale_rejected(self):
        for value in (None,float('inf'),float('nan'),0,-1,True):
            raw=world();raw['assets']['splats']['semantics_metadata']['metric_scale_factor']=value
            with self.assertRaises(ValueError): admin.semantics(raw)

    def test_uncertain_generation_is_not_retried(self):
        with tempfile.TemporaryDirectory() as t:
            with patch.object(admin,'api_call',side_effect=OSError('connection interrupted')) as call:
                with self.assertRaises(OSError): admin.generate('A hotel','marble-1.1','test-key',t)
                with self.assertRaises(ValueError): admin.generate('A hotel','marble-1.1','test-key',t)
                self.assertEqual(call.call_count,1)

    def test_resume_polls_and_fetches_without_generation(self):
        raw=world()
        with tempfile.TemporaryDirectory() as t:
            with patch.object(admin,'api_call',side_effect=[{'done':True,'response':raw},raw]) as call:
                admin.wait_for_world('operation_123','test-key',t,timeout=1)
                self.assertTrue((Path(t)/'world.json').exists())
                self.assertEqual([a.args[0] for a in call.call_args_list],
                    ['operations/operation_123','worlds/'+raw['id']])

    def test_failed_download_leaves_previous_manifest(self):
        with tempfile.TemporaryDirectory() as t:
            dest=Path(t);previous={'old':'world'};admin.write_json(dest/'active.json',previous)
            with patch.object(admin,'download',side_effect=ValueError('bad asset')):
                with self.assertRaises(ValueError): admin.publish(world(),dest,'new')
            self.assertEqual(json.loads((dest/'active.json').read_text()),previous)

