import unittest
from world import HotelWorld,clear,path_to

class WalkingTests(unittest.TestCase):
    def setUp(self):
        self.now=0.;self.world=HotelWorld(lambda:self.now)
        self.world.command('human','enter',{'kind':'human','name':'Human'})
        self.world.command('agent','enter',{'kind':'agent','name':'Agent'})
    def advance(self,steps=100):
        for _ in range(steps):self.now+=.2;self.world.tick()
    def test_both_kinds_share_space_and_enter_lobby(self):
        snap=self.world.snapshot('human')
        self.assertEqual({p['kind'] for p in snap['people']},{'human','agent'})
        self.world.command('human','target',{'landmark':'lobby'})
        self.world.command('agent','target',{'landmark':'front_desk'})
        self.advance()
        self.assertEqual((self.world.get('human')['x'],self.world.get('human')['z']),(0,6))
        self.assertEqual((self.world.get('agent')['x'],self.world.get('agent')['z']),(-8,0))
    def test_resident_routines_and_lobby_spawn(self):
        self.assertEqual((self.world.get('human')['x'],self.world.get('human')['z']),(0,6))
        residents=self.world.residents
        self.assertEqual(len({r['id'] for r in residents}),41)
        self.assertEqual({r['floor'] for r in residents},set(range(12)))
        initial={r['id']:(r['x'],r['z']) for r in residents}
        for _ in range(1800):
            self.now+=.2;self.world.tick()
            self.assertTrue(all(clear(r['x'],r['z'],r['floor']) for r in residents))
        self.assertGreater(sum(initial[r['id']]!=(r['x'],r['z']) for r in residents),30)
        snap=self.world.snapshot('human')
        self.assertTrue(all(r['ambient'] and r['bio'] for r in snap['residents']))
        self.assertTrue(all(not p.get('ambient') for p in snap['people']))

    def test_expanded_lobby_wings_and_column_bases(self):
        self.assertFalse(clear(18.9,0,0))
        self.assertTrue(clear(20,6,0))
        for x in (-20,20):
            self.assertTrue(path_to(0,6,x,6,0))

    def test_collisions_and_no_teleport(self):
        self.assertFalse(clear(22,0,0));self.assertFalse(clear(-8,-3,0))
        self.assertFalse(clear(0,20,1))
        with self.assertRaises(ValueError):path_to(0,20,22,0,0)
        self.now=1
        self.world.command('human','move',{'dx':100000,'dz':0})
        self.assertLessEqual(self.world.get('human')['x'],1.126)
        self.world.command('human','move',{'dx':100000,'dz':0})
        self.assertLessEqual(self.world.get('human')['x'],1.126)
    def test_lift_all_floors_and_return(self):
        self.world.command('agent','floor',{'floor':11});self.advance(100)
        self.assertEqual(self.world.get('agent')['floor'],11)
        self.assertEqual(self.world.get('human')['floor'],0)
        self.world.command('agent','target',{'x':6,'z':-6});self.advance(40)
        self.assertAlmostEqual(self.world.get('agent')['x'],6)
        self.world.command('agent','floor',{'floor':0});self.advance(100)
        self.assertEqual(self.world.get('agent')['floor'],0)
        self.world.command('agent','target',{'landmark':'entrance'});self.advance(100)
        self.assertEqual(self.world.get('agent')['z'],16)
    def test_invalid_commands_and_expiry(self):
        for data in ({'floor':12},{'floor':-1},{'floor':True}):
            with self.assertRaises(ValueError):self.world.command('agent','floor',data)
        with self.assertRaises(ValueError):self.world.command('outsider','move',{'dx':1,'dz':0})
        with self.assertRaises(ValueError):self.world.command('agent','move',{'dx':float('nan'),'dz':0})
        self.world.command('agent','leave',{})
        self.assertEqual(len(self.world.snapshot('human')['people']),1)
        self.now=200;self.world.tick();self.assertFalse(self.world.people)

if __name__=='__main__':unittest.main(verbosity=2)
