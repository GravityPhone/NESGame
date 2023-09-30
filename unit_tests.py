
import unittest
from app import Barbarian, go_on_adventure, calculate_and_simulate_adventures

class TestBarbarianGame(unittest.TestCase):

    def setUp(self):
        self.barbarian = Barbarian()

    def test_initial_values(self):
        self.assertEqual(self.barbarian.gold, 0)
        self.assertEqual(self.barbarian.experience, 0)
        self.assertEqual(self.barbarian.level, 1)
        self.assertEqual(self.barbarian.auto_adventure, False)

    def test_go_on_adventure(self):
        initial_gold = self.barbarian.gold
        initial_experience = self.barbarian.experience
        go_on_adventure(self.barbarian)
        self.assertTrue(self.barbarian.gold > initial_gold)
        self.assertTrue(self.barbarian.experience > initial_experience)

    def test_calculate_and_simulate_adventures(self):
        initial_gold = self.barbarian.gold
        initial_experience = self.barbarian.experience
        calculate_and_simulate_adventures(self.barbarian)
        self.assertTrue(self.barbarian.gold > initial_gold)
        self.assertTrue(self.barbarian.experience > initial_experience)

    def test_level_up(self):
        self.barbarian.experience = 1000
        self.barbarian.check_for_level_up()
        self.assertEqual(self.barbarian.level, 2)

    def test_auto_adventure_toggle(self):
        self.barbarian.toggle_auto_adventure()
        self.assertTrue(self.barbarian.auto_adventure)

if __name__ == "__main__":
    unittest.main()
