import csv
import io
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).parent / "data"
RAW = ROOT / "raw"
UCI_ZIP = RAW / "uci_adult.zip"
OPENML_ARFF = RAW / "openml_adult.arff"
OUT = ROOT / "adult.csv"
UCI_URL = "https://archive.ics.uci.edu/static/public/2/adult.zip"
HEADER = ["age", "workclass", "education", "education_num", "marital_status", "occupation", "race", "sex", "hours_per_week", "income"]
KEEP = [0, 1, 3, 4, 5, 6, 8, 9, 12, 14]


# Turns raw census lines into training rows: keeps 10 columns, drops rows with missing values, fixes the test file's trailing dot
def clean(lines):
    for r in csv.reader(lines, skipinitialspace=True):
        if len(r) == 15 and r[0].isdigit() and "?" not in r:
            r[14] = r[14].rstrip(".")
            yield [r[i] for i in KEEP]


# UCI source: adult.data and adult.test together make the full 48,842 record dataset
def from_uci():
    if not UCI_ZIP.exists():
        RAW.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(UCI_URL, UCI_ZIP)
    with zipfile.ZipFile(UCI_ZIP) as z:
        return [row for name in ("adult.data", "adult.test") for row in clean(io.TextIOWrapper(z.open(name)))]


# OpenML source: the same 48,842 records in ARFF format, used to cross check the UCI build
def from_openml():
    lines = OPENML_ARFF.read_text().splitlines()
    start = next(i for i, line in enumerate(lines) if line.strip().lower() == "@data")
    return list(clean(lines[start + 1:]))


if __name__ == "__main__":
    rows = from_uci()
    with open(OUT, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)
        writer.writerows(rows)
    print(f"Wrote {len(rows):,} rows to {OUT}")
    if OPENML_ARFF.exists():
        same = sorted(from_openml()) == sorted(rows)
        print("OpenML cross check:", "identical records" if same else "MISMATCH, check the raw files")
