name: Собрать reestr.json из выгрузки

# Запускается сам, когда вы загружаете новый xlsx в репозиторий
on:
  push:
    paths:
      - '**.xlsx'
      - '**.xls'
  workflow_dispatch: {}

permissions:
  contents: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - run: pip install pandas openpyxl

      - run: python build_reestr.py

      - name: Сохранить результат
        run: |
          git config user.name "reestr-bot"
          git config user.email "bot@users.noreply.github.com"
          git add reestr.json
          git diff --staged --quiet || git commit -m "Обновление реестра"
          git push
