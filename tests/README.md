# Тесты DrillMole

Запуск из корня репозитория:

```
python -m unittest discover -s tests -t . -v
```

- `test_drill_mole.py` — модульные тесты (AAA), TC-01…TC-22
- `test_drill_mole_scenarios.py` — сценарные тесты (GWT), TC-23…TC-26
- `driver.py` — машинист, через которого идут сценарные тесты
- `test_review_regressions.py` — дополнения по ревью, TC-27…TC-32
- `test_acceptance_regressions.py` — регрессионные тесты приёмки, TC-33…TC-36

ТЗ заморожено 26.10.2026; после приёмки уточняется версия 1.1. Всего 36 тестов.

Тесты ожидают `drill_mole.py` в корне репозитория. Пока реализации нет, запуск падает с ImportError.
