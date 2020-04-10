import os

from project.settings import TEMPLATES, BASE_DIR

# добавляем в DIRS директории с кастомными шаблонами (в примере, новые шаблоны находятся в директории custom)
# TEMPLATES['DIRS'] = [os.path.join(BASE_DIR, 'custom/templates')]

# определяем путь к статическим файлам (css, js, картинки и т.л.)
# (в примере, статические файлы находятся в директории custom)
# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, "custom/static"),
# ]

# переопредеяем шаблоны для основных интерфейсов
# TEMPLATES_DICT = {
#     "base": 'base.html',        # базовый шаблон, на основе которого строятся остальные шаблоны
#     "index": '',                # шаблон главной страницы
#     "workers_done_report": '',  # шаблон отчета "Прошедшие"
#     "direction_list": '',       # шаблон для списка направлений на осмотры
# }