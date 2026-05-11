import pandas as pd
import zipfile
from pathlib import Path

path = Path("C:/R_SMTR/dados/gtfs/2026/gtfs_rio-de-janeiro_pub.zip")
with zipfile.ZipFile(path, 'r') as z:
    routes = pd.read_csv(z.open('routes.txt'), dtype=str)
    print(routes.head(10))
    print("\nUnique agency_ids:")
    if 'agency_id' in routes.columns:
        print(routes['agency_id'].unique())
    print("\nUnique route_types:")
    print(routes['route_type'].unique())
