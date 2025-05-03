import pandas as pd
import json
import os
from os import listdir
import psycopg2
import sys

date = sys.argv[1]

with open("../util/creds.txt", "r") as credsfile:
    username = credsfile.readline().strip()
    password = credsfile.readline().strip()

base_path = "../../data/processed"
folders = os.listdir(base_path)


conn = psycopg2.connect(
    host='localhost',
    database='moj',
    user=username,
    password=password
)
cursor = conn.cursor()

query = """
DELETE FROM temp_hashtags;
COPY temp_hashtags 
FROM 'C:/Users/archi/capstone/data/processed/flows/summer/csvs/temp_hashtags.csv'
WITH (FORMAT CSV);

INSERT INTO hashtags (i, tagName, tagId)
SELECT * FROM temp_hashtags AS new_data (i, tagName, tagId)
ON CONFLICT (i, tagName) DO NOTHING;

SELECT COUNT(*) from hashtags;
"""

for party_folder in folders:
    if party_folder == "csv":
        continue
    tags_df = pd.DataFrame(columns=['videoId', 'tagName', 'tagId'])
    file_path = f"{base_path}/{party_folder}/{party_folder}-{date}.json"

    if os.path.exists(file_path): 
        with open(file_path) as datafile:
            df = pd.read_json(datafile, orient="records")
            for index, row in df.iterrows():
                try:
                    tags_list = row.captionTagsList
                    for i in range(0,len(tags_list)):
                        new_row = pd.Series({'videoId': row.i, 'tagName': tags_list[i]['tagName'], 'tagId': tags_list[i]['tagId']})  
                        tags_df = pd.concat([tags_df, new_row.to_frame().T], ignore_index=True)
                except:
                    print(f"No tags for {row.i} in row {index}")

            
        tags_df.to_csv("../../data/processed/csvs/temp_hashtags.csv", header=None, index=None)

        cursor.execute(query)
        conn.commit()

        print(f"Finished {party_folder}-{date}")
    

# Fetch the results
results = cursor.fetchall()

# Process the results
for row in results:
    print(row)

# Close the cursor and database connection
cursor.close()
conn.close()