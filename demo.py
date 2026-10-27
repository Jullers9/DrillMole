"""Краткая демонстрация крота-бура. Запуск: python demo.py"""
from drill_mole import DrillMole, DrillMoleCannotSwim

mole = DrillMole("Копатель", drill_diameter_m=1.2, max_speed_kmh=20)
print("Начало:", mole.get_status())
print("2 км по поверхности, часов:", mole.move(2, "surface"))
print("Река с поверхности:", mole.can_overcome("river"))
print("4 км в грунте, часов:", mole.move(4, "soil"))
print("Под землёй:", mole.get_status())
print("Река и стена под землёй:", mole.can_overcome("river"), mole.can_overcome("wall"))
before = mole.get_status()
try:
    mole.move(1, "water")
except DrillMoleCannotSwim:
    print("В воду нельзя: DrillMoleCannotSwim")
print("Состояние после ошибки не изменилось:", mole.get_status() == before)
print("Выезд на поверхность, часов:", mole.move(1, "surface"))
mole.replace_drill()
print("Бур заменён:", mole.get_status())
