"""Модульные тесты DrillMole (паттерн AAA). ID тест-кейсов — из TEST_CASES.md."""

import unittest

from drill_mole import (
    CrazyVehicleError,
    DrillMole,
    DrillMoleCannotSwim,
    DrillMoleDrillWorn,
    DrillMoleError,
    DrillMoleNoFuel,
    DrillMoleNotOnSurface,
)


def make_mole(**kwargs):
    params = {"name": "Копатель", "drill_diameter_m": 1.2, "max_speed_kmh": 20, "fuel": 100}
    params.update(kwargs)
    return DrillMole(**params)


def state(mole):
    return (mole.position_km, mole.fuel, mole.drill_wear, mole.is_underground)


class TestConstructor(unittest.TestCase):
    def test_tc01_invalid_values_raise(self):
        """TC-01: пустое имя, неположительные диаметр и скорость."""
        for bad in ({"name": ""}, {"name": "   "}, {"drill_diameter_m": 0}, {"drill_diameter_m": -1}, {"max_speed_kmh": 0}):
            with self.subTest(bad=bad):
                # Act / Assert
                with self.assertRaises(ValueError):
                    make_mole(**bad)

    def test_tc02_fuel_bounds_and_default(self):
        """TC-02: fuel в диапазоне 0…100, по умолчанию 100."""
        for bad in (-1, 101):
            with self.subTest(fuel=bad):
                with self.assertRaises(ValueError):
                    make_mole(fuel=bad)
        # Arrange / Act
        empty = make_mole(fuel=0)
        full = make_mole(fuel=100)
        default = DrillMole("Копатель", 1.2, 20)
        # Assert
        self.assertEqual(empty.fuel, 0)
        self.assertEqual(full.fuel, 100)
        self.assertEqual(default.fuel, 100.0)

    def test_tc03_invalid_types_raise(self):
        """TC-03: неверные типы параметров конструктора."""
        for bad in ({"name": 5}, {"drill_diameter_m": "1"}, {"max_speed_kmh": None}, {"fuel": True}):
            with self.subTest(bad=bad):
                with self.assertRaises(TypeError):
                    make_mole(**bad)


class TestMove(unittest.TestCase):
    def test_tc04_move_surface(self):
        """TC-04: движение по поверхности."""
        # Arrange
        mole = make_mole()
        # Act
        hours = mole.move(10, "surface")
        # Assert
        self.assertAlmostEqual(hours, 0.5)
        self.assertEqual(state(mole), (10, 90, 0, False))

    def test_tc05_move_soil(self):
        """TC-05: движение в грунте."""
        # Arrange
        mole = make_mole()
        # Act
        hours = mole.move(10, "soil")
        # Assert
        self.assertAlmostEqual(hours, 1.0)
        self.assertEqual(state(mole), (10, 80, 10, True))

    def test_tc06_move_rock(self):
        """TC-06: движение в скале."""
        # Arrange
        mole = make_mole()
        # Act
        hours = mole.move(4, "rock")
        # Assert
        self.assertAlmostEqual(hours, 0.8)
        self.assertEqual(state(mole), (4, 88, 20, True))

    def test_tc07_water_raises(self):
        """TC-07: в воду нельзя."""
        # Arrange
        mole = make_mole()
        before = state(mole)
        # Act / Assert
        with self.assertRaises(DrillMoleCannotSwim):
            mole.move(1, "water")
        self.assertEqual(state(mole), before)

    def test_tc08_not_enough_fuel(self):
        """TC-08: не хватает топлива."""
        # Arrange
        mole = make_mole(fuel=10)
        before = state(mole)
        # Act / Assert
        with self.assertRaises(DrillMoleNoFuel):
            mole.move(4, "rock")
        self.assertEqual(state(mole), before)

    def test_tc09_exact_fuel(self):
        """TC-09: топлива ровно хватает."""
        # Arrange
        mole = make_mole(fuel=12)
        # Act
        mole.move(4, "rock")
        # Assert
        self.assertEqual(mole.fuel, 0)
        self.assertEqual(mole.drill_wear, 20)

    def test_tc10_worn_drill(self):
        """TC-10: износ ровно 100 допустим, дальше копать нельзя, по поверхности можно."""
        # Arrange
        mole = make_mole()
        mole.move(10, "rock")
        mole.move(10, "rock")
        self.assertEqual(mole.drill_wear, 100)
        before = state(mole)
        # Act / Assert
        with self.assertRaises(DrillMoleDrillWorn):
            mole.move(1, "soil")
        self.assertEqual(state(mole), before)
        mole.move(1, "surface")
        self.assertEqual(state(mole), (21, 39, 100, False))

    def test_tc11_invalid_arguments(self):
        """TC-11: неверные distance_km и terrain."""
        cases = [((0, "soil"), ValueError), ((-1, "soil"), ValueError), ((1, "lava"), ValueError),
                 (("1", "soil"), TypeError), ((1, 5), TypeError)]
        for args, error in cases:
            with self.subTest(args=args):
                # Arrange
                mole = make_mole()
                before = state(mole)
                # Act / Assert
                with self.assertRaises(error):
                    mole.move(*args)
                self.assertEqual(state(mole), before)

    def test_tc12_check_order(self):
        """TC-12: порядок проверок: параметры → вода → бур → топливо."""
        # Arrange
        empty = make_mole(fuel=0)
        worn = make_mole(fuel=60)
        worn.move(10, "rock")
        worn.move(10, "rock")
        # Act / Assert
        with self.assertRaises(DrillMoleCannotSwim):
            empty.move(1, "water")
        with self.assertRaises(ValueError):
            empty.move(0, "water")
        with self.assertRaises(DrillMoleDrillWorn):
            worn.move(1, "soil")

    def test_tc13_fractional_values_rounded(self):
        """TC-13: дробные значения округляются, 0.3 − 3×0.1 = 0."""
        # Arrange
        mole = make_mole(fuel=0.3)
        # Act
        for _ in range(3):
            mole.move(0.1, "surface")
        # Assert
        self.assertEqual(mole.fuel, 0.0)
        self.assertEqual(mole.position_km, 0.3)


class TestCanOvercome(unittest.TestCase):
    def test_tc14_river_only_underground(self):
        """TC-14: река проходима только под землёй."""
        # Arrange
        on_surface = make_mole()
        underground = make_mole()
        underground.move(1, "soil")
        came_back = make_mole()
        came_back.move(1, "soil")
        came_back.move(1, "surface")
        # Act / Assert
        self.assertIs(on_surface.can_overcome("river"), False)
        self.assertIs(underground.can_overcome("river"), True)
        self.assertIs(came_back.can_overcome("river"), False)

    def test_tc15_wall_requires_underground_and_usable_drill(self):
        """TC-15: стена проходима только под землёй при износе < 100."""
        mole = make_mole()
        self.assertIs(mole.can_overcome("wall"), False)
        mole.move(1, "soil")
        before = state(mole)
        self.assertIs(mole.can_overcome("wall"), True)
        self.assertEqual(state(mole), before)
        mole.move(1, "surface")
        self.assertIs(mole.can_overcome("wall"), False)
        worn = make_mole()
        worn.move(10, "rock")
        worn.move(10, "rock")
        self.assertIs(worn.can_overcome("wall"), False)

    def test_tc16_boulder_needs_big_drill(self):
        """TC-16: валун — при диаметре бура ≥ 1 м."""
        # Arrange
        big = make_mole(drill_diameter_m=1.0)
        small = make_mole(drill_diameter_m=0.99)
        # Act / Assert
        self.assertIs(big.can_overcome("boulder"), True)
        self.assertIs(small.can_overcome("boulder"), False)

    def test_tc17_invalid_obstacle(self):
        """TC-17: неизвестное препятствие и неверный тип."""
        # Arrange
        mole = make_mole()
        # Act / Assert
        with self.assertRaises(ValueError):
            mole.can_overcome("tree")
        with self.assertRaises(TypeError):
            mole.can_overcome(1)


class TestOtherMethods(unittest.TestCase):
    def test_tc18_calculate_fuel(self):
        """TC-18: расчёт топлива не меняет состояние и не зависит от запаса."""
        for fuel in (100, 0):
            with self.subTest(fuel=fuel):
                # Arrange
                mole = make_mole(fuel=fuel)
                before = state(mole)
                # Act
                results = [mole.calculate_fuel(5, t) for t in ("surface", "soil", "rock")]
                # Assert
                self.assertEqual(results, [5.0, 10.0, 15.0])
                with self.assertRaises(DrillMoleCannotSwim):
                    mole.calculate_fuel(1, "water")
                self.assertEqual(state(mole), before)

    def test_tc19_refuel(self):
        """TC-19: заправка, предел 100, неположительное количество."""
        # Arrange
        mole = make_mole(fuel=20)
        # Act
        result = mole.refuel(50)
        # Assert
        self.assertIsNone(result)
        self.assertEqual(mole.fuel, 70)
        # Arrange / Act
        mole = make_mole(fuel=50)
        mole.refuel(1000)
        # Assert
        self.assertEqual(mole.fuel, 100)
        for amount in (0, -1):
            with self.subTest(amount=amount):
                with self.assertRaises(ValueError):
                    mole.refuel(amount)

    def test_tc20_replace_drill_only_on_surface(self):
        """TC-20: бур меняется только на поверхности."""
        # Arrange
        mole = make_mole()
        mole.move(10, "rock")
        # Act / Assert
        with self.assertRaises(DrillMoleNotOnSurface):
            mole.replace_drill()
        self.assertEqual(mole.drill_wear, 50)
        # Arrange
        mole.move(1, "surface")
        # Act
        mole.replace_drill()
        # Assert
        self.assertEqual(mole.drill_wear, 0)
        self.assertEqual(mole.fuel, 69)

    def test_tc21_get_status(self):
        """TC-21: снимок состояния."""
        # Arrange
        mole = make_mole()
        # Act
        status = mole.get_status()
        # Assert
        self.assertEqual(status, {"name": "Копатель", "fuel": 100.0, "drill_wear": 0.0,
                                  "position_km": 0.0, "is_underground": False})

    def test_tc22_exception_hierarchy(self):
        """TC-22: иерархия доменных исключений."""
        for error in (DrillMoleCannotSwim, DrillMoleDrillWorn, DrillMoleNoFuel, DrillMoleNotOnSurface):
            with self.subTest(error=error.__name__):
                self.assertTrue(issubclass(error, DrillMoleError))
        self.assertTrue(issubclass(DrillMoleError, CrazyVehicleError))


if __name__ == "__main__":
    unittest.main()
