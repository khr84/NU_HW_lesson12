# Поиск вакансий на HeadHunter по api.

Поиск производится на сайте, под управлением flask.
Страница поиска: можно указать следующие параметры:
•	Вакансия для поиска
•	Строгий поиск. В случае если вводится несколько слов, то при строгом поиске проверяется наличие всей фразы в вакансии, при нестрогом – каждого из слов
•	Регион поиска.
Важно! Поиск производится по всем вакансиям за последние 10 дней (данный параметр можно поменять в коде: vacancy.period)
Страница результатов: отображает резултаты поиска по критериям, указанным на странице поиска.
Страница истории: дает возможность вывести историю поиска вакансий за последние N дней (не более 10 дней назад). 

Используемые библиотеки:
Flask	2.2.3
SQLAlchemy	2.0.7
requests	2.28.1