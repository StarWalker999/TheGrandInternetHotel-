"""HTTP boundary regressions; uses an isolated temporary database."""
import http.client
import socket
import time
from unittest.mock import patch
import unittest
import test_hotel
server = test_hotel.server


class SecurityBoundary(unittest.TestCase):
    setUpClass = classmethod(test_hotel.HotelFlow.setUpClass.__func__)
    tearDownClass = classmethod(test_hotel.HotelFlow.tearDownClass.__func__)
    req = test_hotel.HotelFlow.req
    def test_security_headers_and_private_files(self):
        for path in ('/agents/server.py', '/agents/.env', '/agents/data/hotel.sqlite3',
                     '/agents/assets/../../server.py', '/agents/assets/%2e%2e/server.py'):
            c = http.client.HTTPConnection('127.0.0.1', self.port)
            c.request('GET', path)
            r = c.getresponse()
            self.assertEqual(r.status, 404, path)
            r.read(); c.close()
        c = http.client.HTTPConnection('127.0.0.1', self.port)
        c.request('GET', '/agents/api/health')
        r = c.getresponse()
        self.assertNotIn('Python', r.getheader('Server'))
        self.assertIn("object-src 'none'", r.getheader('Content-Security-Policy'))
        self.assertEqual(r.getheader('Referrer-Policy'), 'no-referrer')
        self.assertIn('HttpOnly', r.getheader('Set-Cookie'))
        r.read(); c.close()

    def test_invalid_json_and_cross_site(self):
        for body in ('{"budget":NaN}', '{"budget":Infinity}', '[' * 1500, '{}' * 17000):
            c = http.client.HTTPConnection('127.0.0.1', self.port)
            c.request('POST', '/agents/api/checkin', body, {'Content-Type': 'application/json'})
            r = c.getresponse(); self.assertEqual(r.status, 400); r.read(); c.close()
        c = http.client.HTTPConnection('127.0.0.1', self.port)
        c.request('POST', '/agents/api/checkin', '{}',
                  {'Content-Type': 'application/json', 'Sec-Fetch-Site': 'cross-site'})
        r = c.getresponse(); self.assertEqual(r.status, 403); r.read(); c.close()
        c = http.client.HTTPConnection('127.0.0.1', self.port)
        c.request('GET', '/agents/api/state', headers={'Sec-Fetch-Site': 'cross-site'})
        r = c.getresponse(); self.assertEqual(r.status, 403)
        self.assertIsNone(r.getheader('Set-Cookie')); r.read(); c.close()

    def test_client_download_is_explicit_and_not_executed(self):
        c = http.client.HTTPConnection('127.0.0.1', self.port)
        c.request('GET', '/agents/downloads/hotel_client.py')
        r = c.getresponse()
        self.assertEqual(r.status, 200)
        self.assertIn('attachment', r.getheader('Content-Disposition'))
        self.assertIn(b'def main():', r.read()); c.close()

    def test_slow_body_does_not_block_other_visitors(self):
        s = socket.create_connection(('127.0.0.1', self.port))
        try:
            s.sendall(b'POST /agents/api/checkin HTTP/1.0\r\nContent-Type: application/json\r\nContent-Length: 100\r\n\r\n{')
            time.sleep(.1)
            c = http.client.HTTPConnection('127.0.0.1', self.port, timeout=2)
            c.request('POST', '/agents/api/world/invalid', '{}', {'Content-Type': 'application/json'})
            r = c.getresponse(); self.assertEqual(r.status, 400); r.read(); c.close()
        finally:
            s.sendall(b' ' * 99)
            s.recv(4096)
            s.close()

    def test_storage_limit_stops_writes(self):
        with patch.object(server, 'MAX_DB_BYTES', 0):
            server.db().close()
            self.assertEqual(self.req('checkin', {'name': 'Quota probe'})[0], 503)

    def test_homepage_does_not_replace_existing_api_session(self):
        c = http.client.HTTPConnection('127.0.0.1', self.port)
        # A /agents-scoped cookie is intentionally absent on the root request.
        c.request('GET', '/')
        r = c.getresponse()
        self.assertEqual(r.status, 200)
        self.assertIn(b'The Grand Internet Hotel', r.read())
        self.assertIsNone(r.getheader('Set-Cookie'))
        c.close()
