"""Регрессионные проверки по результатам приёмки реализации."""
import unittest

from drill_mole import DrillMoleDrillWorn, DrillMoleNoFuel
from tests.test_drill_mole import make_mole, state


class TestAcceptanceRegressions(unittest.TestCase):
    def test_tc33_exact_unrounded_initial_fuel(self):
        """TC-33: топливо с семью знаками расходуется без ложной нехватки."""
        mole = make_mole(fuel=0.1234567)
        self.assertEqual(mole.fuel, 0.1234567)
        self.assertAlmostEqual(mole.calculate_fuel(0.1234567, "surface"),
                               0.1234567, places=10)
        mole.move(0.1234567, "surface")
        self.assertEqual(mole.fuel, 0.0)

    def test_tc34_float_noise_and_real_shortage(self):
        """TC-34: допустим шум float, но не заметная нехватка топлива."""
        mole = make_mole(fuel=0.3)
        mole.move(0.1, "rock")
        self.assertEqual(mole.fuel, 0.0)
        mole = make_mole(fuel=0.3)
        before = state(mole)
        with self.assertRaises(DrillMoleNoFuel):
            mole.move(0.100001, "rock")
        self.assertEqual(state(mole), before)

    def test_tc35_empty_tank_rejects_even_short_move(self):
        """TC-35: допуск не позволяет двигаться с пустым баком."""
        mole = make_mole(fuel=0)
        before = state(mole)
        with self.assertRaises(DrillMoleNoFuel):
            mole.move(0.0000000005, "surface")
        self.assertEqual(state(mole), before)

    def test_tc36_worn_drill_rejects_even_short_dig(self):
        """TC-36: при износе 100 копание запрещено на любой дистанции."""
        mole = make_mole()
        mole.move(10, "rock")
        mole.move(10, "rock")
        before = state(mole)
        with self.assertRaises(DrillMoleDrillWorn):
            mole.move(0.0000001, "soil")
        self.assertEqual(state(mole), before)
