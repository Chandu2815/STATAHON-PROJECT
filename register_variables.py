import pandas as pd
from pathlib import Path 
csv_dir= Path("/root/HCES_Data_2023-24_Csv/HCES_Data_2023-24_Csv")
for csv_file in sorted(csv_dir.glob("*.csv")):
	cols = pd.read_csv(csv_file,nrows=0).columns.tolist()
	
	print ("\n" + "=" * 60)
	print(csv_file.name)
	print("=" * 60)
	for col in cols:
		print(col)
