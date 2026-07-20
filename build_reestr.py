# build_reestr.py
# Берёт самый свежий xlsx из репозитория и делает reestr.json.
# Файл может лежать прямо в корне. Запускается автоматически (GitHub Actions).
import os, re, json, glob
from datetime import date
import pandas as pd

def date_key(name):
    m = re.search(r"(\d{2})[_\-.](\d{2})[_\-.](\d{4})", os.path.basename(name))
    return (int(m.group(3)), int(m.group(2)), int(m.group(1))) if m else (0, 0, 0)

def newest_xlsx():
    files = glob.glob("*.xlsx") + glob.glob("*.xls")
    files += glob.glob("**/*.xlsx", recursive=True) + glob.glob("**/*.xls", recursive=True)
    files = sorted(set(files))
    if not files:
        raise SystemExit("Не найден ни один xlsx-файл. Загрузите выгрузку реестра в репозиторий.")
    return max(files, key=date_key)

def updated_str(name):
    m = re.search(r"(\d{2})[_\-.](\d{2})[_\-.](\d{4})", os.path.basename(name))
    return f"{m.group(1)}/{m.group(2)}/{m.group(3)}" if m else date.today().strftime("%d/%m/%Y")

def region(addr):
    return addr.split(",")[0].strip()[:40] if addr else ""

def col(df, names):
    for n in names:
        if n in df.columns:
            return df[n]
    return pd.Series([""] * len(df))

def main():
    src = newest_xlsx()
    df = pd.read_excel(src, dtype=str).fillna("")

    reg     = col(df, ["Реестровый номер"])
    dt      = col(df, ["Дата включения в реестр уведомлений ТЭД", "Дата включения"])
    inn_ul  = col(df, ["ИНН ЮЛ"])
    name_ul = col(df, ["Полное наименование юридического лица"])
    addr    = col(df, ["Юридический адрес"])
    inn_ip  = col(df, ["ИНН ИП"])
    fam     = col(df, ["Фамилия ИП"])
    imy     = col(df, ["Имя ИП"])
    otch    = col(df, ["Отчество ИП (при наличии)", "Отчество ИП"])

    rows = []
    for i in range(len(df)):
        ul = re.sub(r"\D", "", str(inn_ul.iloc[i]))
        if ul:
            inn, name, kind, a = ul, str(name_ul.iloc[i]).strip(), "ЮЛ", str(addr.iloc[i])
        else:
            inn = re.sub(r"\D", "", str(inn_ip.iloc[i]))
            name = " ".join(x for x in [str(fam.iloc[i]).strip(), str(imy.iloc[i]).strip(), str(otch.iloc[i]).strip()] if x)
            kind, a = "ИП", ""
        if not (inn or name):
            continue
        rows.append([str(reg.iloc[i]).strip(), str(dt.iloc[i])[:10], inn, name, kind, region(a)])

    out = {"updated": updated_str(src), "count": len(rows), "rows": rows}
    with open("reestr.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    print(f"OK: {len(rows)} записей из {os.path.basename(src)} -> reestr.json (актуально на {out['updated']})")

if __name__ == "__main__":
    main()
