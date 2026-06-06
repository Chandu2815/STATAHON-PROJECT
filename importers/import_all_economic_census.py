from pathlib import Path
import zipfile
import csv
from sqlalchemy import create_engine

DATA_FOLDER = Path(
    "/root/Economic_Census/Economic census_1990/Data"
)

TEMP_CSV = "/tmp/economic_census_batch.csv"

engine = create_engine(
    "postgresql+psycopg2://statahon_user:Statahon%40123@localhost:5432/statahon_db"
)

total_rows = 0

for zip_file in sorted(DATA_FOLDER.glob("*.zip")):

    print(f"\nProcessing {zip_file.name}")

    with zipfile.ZipFile(zip_file) as z:

        txt_file = z.namelist()[0]

        with z.open(txt_file) as f, \
             open(TEMP_CSV, "w", newline="", encoding="utf-8") as out:

            writer = csv.writer(out)

            count = 0

            for raw_line in f:

                line = raw_line.decode(
                    "utf-8",
                    errors="ignore"
                ).rstrip("\n")

                writer.writerow([
                    line[0:1].strip(),
                    line[1:3].strip(),
                    line[3:5].strip(),
                    line[5:9].strip(),
                    line[9:13].strip(),
                    line[13:17].strip(),
                    line[17:20].strip(),
                    line[20:23].strip(),
                    line[23:27].strip(),
                    line[27:28].strip(),
                    line[28:32].strip(),
                    line[32:36].strip(),
                    line[36:40].strip(),
                    line[40:42].strip(),
                    line[42:43].strip(),
                    line[43:44].strip(),
                    line[44:45].strip(),
                    line[45:46].strip(),
                    line[46:47].strip(),
                    line[47:52].strip(),
                    line[52:57].strip(),
                    line[57:63].strip(),
                    line[63:68].strip(),
                    line[68:73].strip(),
                    line[73:79].strip(),
                    line[79:80].strip(),
                    line[80:81].strip(),
                    line[81:83].strip(),
                    line[83:84].strip(),
                    line[84:86].strip(),
                    line[86:87].strip(),
                    line[87:90].strip(),
                    line[90:94].strip(),
                    line[94:98].strip(),
                    line[98:100].strip()
                ])

                count += 1

            print(f"Prepared {count} rows")

        raw_conn = engine.raw_connection()

        try:

            cur = raw_conn.cursor()

            with open(TEMP_CSV, "r", encoding="utf-8") as csv_file:

                cur.copy_expert(
                    """
                    COPY economic_census_1990_enterprise
                    FROM STDIN
                    WITH CSV
                    """,
                    csv_file
                )

            raw_conn.commit()

        finally:
            raw_conn.close()

        total_rows += count

        print(
            f"Imported {count} rows"
        )

print(f"\nTotal Imported: {total_rows}")
