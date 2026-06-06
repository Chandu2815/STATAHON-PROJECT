import zipfile

zip_path = "/root/Economic_Census/Economic census_1990/Data/ec3st02.zip"

with zipfile.ZipFile(zip_path) as z:
    txt_name = z.namelist()[0]

    with z.open(txt_name) as f:

        for i, raw_line in enumerate(f):

            line = raw_line.decode("utf-8", errors="ignore").rstrip("\n")

            record = {
                "sector": line[0:1].strip(),
                "state_ut": line[1:3].strip(),
                "district": line[3:5].strip(),
                "activity_code": line[36:40].strip(),
                "major_activity_code": line[40:42].strip(),
                "file_code": line[98:100].strip()
            }

            print(record)

            if i == 4:
                break
