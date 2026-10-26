# Тесты DrillMole

Запуск из корня репозитория:

```
python -m unittest discover -s tests -t . -v
```

- `test_drill_mole.py` — модульные тесты (AAA), TC-01…TC-22
- `test_drill_mole_scenarios.py` — сценарные тесты (GWT), TC-23…TC-26
- `driver.py` — машинист, через которого идут сценарные тесты
- `test_review_regressions.py` — дополнения по ревью, TC-27…TC-32

Версия ТЗ и тестов: 1.0, заморожены 26.10.2026. Всего 32 теста.

Тесты ожидают `drill_mole.py` в корне репозитория. Пока реализации нет, запуск падает с ImportError.
