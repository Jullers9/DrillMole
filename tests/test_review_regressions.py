"""Дополнения по ревью перед заморозкой SPEC 1.0."""
import math
import unittest

from tests.test_drill_mole import make_mole, state


class TestReviewCases(unittest.TestCase):
    def test_tc27_public_attributes_read_only(self):
        """TC-27: запись запрещена для всех публичных атрибутов."""
        mole = make_mole()
        replacements = {
            "name": "Другой", "drill_diameter_m": 2.0,
            "max_speed_kmh": 30.0, "fuel": 50.0, "drill_wear": 20.0,
            "position_km": 5.0, "is_underground": True,
        }
        before = {name: getattr(mole, name) for name in replacements}
        for name, value in replacements.items():
            with self.subTest(attribute=name):
                with self.assertRaises(AttributeError):
                    setattr(mole, name, value)
                self.assertEqual(
                    {key: getattr(mole, key) for key in replacements}, before
                )

    def test_tc28_invalid_calculation_and_refuel_are_atomic(self):
        """TC-28: валидация расчёта и заправки не меняет состояние."""
        mole = make_mole()
        cases = [
            (("1", "soil"), TypeError), ((True, "soil"), TypeError),
            ((None, "soil"), TypeError), ((1, 5), TypeError),
            ((0, "soil"), ValueError), ((-5, "soil"), ValueError),
            ((5, "lava"), ValueError), ((0, 5), ValueError),
        ]
        for args, error in cases:
            with self.subTest(args=args):
                before = state(mole)
                with self.assertRaises(error):
                    mole.calculate_fuel(*args)
                self.assertEqual(state(mole), before)
        for amount in ("10", True, None):
            with self.subTest(amount=amount):
                before = state(mole)
                with self.assertRaises(TypeError):
                    mole.refuel(amount)
                self.assertEqual(state(mole), before)

    def test_tc29_status_is_an_independent_snapshot(self):
        """TC-29: словари независимы от объекта и друг от друга."""
        mole = make_mole()
        first, second = mole.get_status(), mole.get_status()
        self.assertIsNot(first, second)
        first["fuel"] = 0
        self.assertEqual(mole.fuel, 100)
        self.assertEqual(second["fuel"], 100)
        mole.move(1, "soil")
        self.assertEqual(second["fuel"], 100)
        self.assertEqual(second["position_km"], 0)
        self.assertEqual(mole.fuel, 98)

    def test_tc30_service_at_initial_state(self):
        """TC-30: исправный бур можно менять, полный бак — заправлять."""
        mole = make_mole()
        before = state(mole)
        self.assertIsNone(mole.replace_drill())
        self.assertIsNone(mole.replace_drill())
        self.assertIsNone(mole.refuel(20))
        self.assertEqual(state(mole), before)

    def test_tc31_time_is_not_rounded_to_six_places(self):
        """TC-31: время сохраняет результат деления."""
        mole = make_mole(max_speed_kmh=3)
        hours = mole.move(1, "surface")
        self.assertAlmostEqual(hours, 1 / 3, places=7)
        self.assertEqual(mole.position_km, 1)
        self.assertEqual(mole.fuel, 99)

    def test_tc32_non_finite_numbers(self):
        """TC-32: нечисловые по смыслу float отвергаются без изменений."""
        for value in (math.nan, math.inf, -math.inf):
            for parameter in ("drill_diameter_m", "max_speed_kmh", "fuel"):
                with self.subTest(parameter=parameter, value=value):
                    with self.assertRaises(ValueError):
                        make_mole(**{parameter: value})
            mole = make_mole()
            for method, args in (
                (mole.move, (value, "soil")),
                (mole.calculate_fuel, (value, "soil")),
                (mole.refuel, (value,)),
            ):
                with self.subTest(method=method.__name__, value=value):
                    before = state(mole)
                    with self.assertRaises(ValueError):
                        method(*args)
                    self.assertEqual(state(mole), before)
