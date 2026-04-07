#!/usr/bin/env python3
"""
Resource generator for namedays.csv sample data.

Run this to generate sample nameday reference data.
"""

import csv
from pathlib import Path

# Sample Hungarian and English namedays data
NAMEDAY_DATA = [
    # January
    ("Teodóra", "01-01", None),
    ("Makária", "01-02", None),
    ("Genovéva", "01-03", None),
    ("Izolda", "01-04", None),
    ("Simon", "01-05", None),
    ("Boldizsár", "01-06", None),
    ("Attila", "01-07", None),
    ("Gyula", "01-08", None),
    ("Marcella", "01-09", None),
    ("Melánia", "01-10", None),
    # February
    ("Ignác", "02-01", None),
    ("Imra", "02-02", None),
    ("Balázs", "02-03", None),
    ("Róza", "02-04", None),
    ("Ágota", "02-05", None),
    ("Dorottya", "02-06", None),
    ("Tilda", "02-07", None),
    ("Aranka", "02-08", None),
    ("Bernadett", "02-09", None),
    ("Elvira", "02-10", None),
    # March
    ("Albin", "03-01", None),
    ("János", "03-02", None),
    ("Kornélia", "03-03", None),
    ("Ádám", "03-04", None),
    ("Adrienn", "03-05", None),
    ("Lenke", "03-06", None),
    ("Tamás", "03-07", None),
    ("Nóra", "03-08", None),
    ("Franciska", "03-09", None),
    (" Eszter", "03-10", None),
    # ... (more months would follow)
    # April
    ("Irén", "04-01", None),
    ("Appolónia", "04-02", None),
    ("Buda", "04-03", None),
    ("Ambrus", "04-04", None),
    ("Vince", "04-05", None),
    ("Vilmos", "04-06", None),
    ("Herman", "04-07", None),
    ("Dénes", "04-08", None),
    ("Героди", "04-09", None),
    ("Gida", "04-10", None),
]


def generate_namedays_csv():
    """Generate sample namedays.csv file."""
    csv_path = Path(__file__).parent / "resources" / "namedays.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(["name", "main_nameday", "other_nameday"])
            writer.writerows(NAMEDAY_DATA)
        
        print(f"✓ Created {csv_path} with {len(NAMEDAY_DATA)} entries")
        return True
    except Exception as e:
        print(f"✗ Failed to create {csv_path}: {e}")
        return False


if __name__ == "__main__":
    generate_namedays_csv()
