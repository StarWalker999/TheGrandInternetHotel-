import copy
import unittest
import hotel_sim as sim
from world import clear

class SimulationTests(unittest.TestCase):
    def test_every_job_completes_with_collisions_and_replay(self):
        for task in sim.TASKS:
            with self.subTest(task=task):
                run=sim.create(task)
                for _ in range(400):
                    sim.apply(run,'step')
                    self.assertTrue(clear(run['worker']['x'],run['worker']['z'],run['worker']['floor']))
                    if run['status']!='running':break
                self.assertEqual(run['status'],'completed')
                self.assertEqual(run['rejected'],0)
                self.assertEqual(len(run['frames']),run['actions']+1)
                self.assertEqual(run['frames'][-1]['worker'],run['worker'])
                actions=[f['action'] for f in run['frames']]
                self.assertEqual([a for a in actions if a in sim.WORK_ACTIONS],[s['action'] for s in run['task']['steps']])
                self.assertEqual(run['phase'],len(run['task']['steps']))
                if task=='room':self.assertIn('lift',actions)
                repeat=sim.create(task)
                for _ in range(run['actions']):sim.apply(repeat,'step')
                self.assertEqual(run['frames'],repeat['frames'])

    def test_invalid_interactions_are_recorded_not_awarded(self):
        run=sim.create('room')
        for action,extra in [('deliver',{}),('pickup',{}),('lift',{'floor':1}),('target',{'x':-8,'z':-3})]:
            sim.apply(run,action,extra)
            self.assertFalse(run['frames'][-1]['accepted'])
        self.assertEqual(run['rejected'],4)
        self.assertEqual(run['worker']['floor'],0)
        self.assertFalse(run['carrying'])
        self.assertEqual(run['status'],'running')

    def test_manual_actions_and_sequence_conflicts(self):
        run=sim.create('parcel');sim.apply(run,'target',{'x':-8,'z':0})
        while run['path']:sim.apply(run,'advance')
        sim.apply(run,'pickup');self.assertTrue(run['carrying'])
        before=copy.deepcopy(run)
        with self.assertRaises(ValueError):sim.apply(run,'move',{'dx':float('nan')})
        self.assertEqual(run,before)
        with self.assertRaises(ValueError):sim.apply(run,'step',{'seq':0})
        self.assertEqual(run,before)
        sim.apply(run,'target',{'x':-10,'z':-8})
        while run['path']:sim.apply(run,'advance')
        sim.apply(run,'deliver');self.assertEqual(run['status'],'completed')
        with self.assertRaises(ValueError):sim.apply(run,'step')

    def test_step_limit_and_copy_isolation(self):
        run=sim.create('tea');run['actions']=999;sim.apply(run,'move',{})
        self.assertEqual(run['status'],'limit')
        observation=sim.observe(run);observation['worker']['x']=999
        self.assertNotEqual(run['worker']['x'],999)

    def test_inventory_count_and_repair_order(self):
        run=sim.create('inventory');run['worker'].update(x=8,z=-5)
        sim.apply(run,'count',{'count':7});self.assertFalse(run['frames'][-1]['accepted'])
        sim.apply(run,'inspect');sim.apply(run,'count',{'count':6})
        self.assertFalse(run['frames'][-1]['accepted']);self.assertEqual(run['phase'],1)
        sim.apply(run,'count',{'count':7});self.assertEqual(run['objects']['inventory'],'count verified')
        run=sim.create('maintenance');run['worker'].update(x=8,z=-5)
        sim.apply(run,'test');self.assertFalse(run['frames'][-1]['accepted'])
        while run['status']=='running':sim.apply(run,'step')
        self.assertEqual(run['objects']['equipment'],'working')
        self.assertEqual(len(sim.TASKS),10)
