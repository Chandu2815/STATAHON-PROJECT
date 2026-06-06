from pathlib import Path
import zipfile

folder = Path("/root/Economic_Census/Economic census_1990/Data")

for z in sorted(folder.glob("*.zip")):
    print(z.name)
