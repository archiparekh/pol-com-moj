import pandas as pd
import json
import os
from os import listdir
import psycopg2
import sys
import numpy as np

# Grab a sample empty field to fill in NaN audioMeta
empty_field = {
    'audioId': 0,
    'audioName': 'empty',
    'audioText': 'empty',
    'compressedThumbUrl': 'https://cdn.sharechat.com/gm_compressed_16472753.65514_105dde8a_1645077737459.jpeg',
    'durationInMillis': 12564,
    'isFavourite': False,
    'licensed': 0,
    'popularity': 0,
    'resourceUrl': 'https://cdn.sharechat.com/23d11c71_1647274836396.mp3',
    'thumbUrl': 'https://cdn.sharechat.com/gm_compressed_16472753.65514_105dde8a_1645077737459.jpeg'
}

def expand_field(dataset, field, na_field):
    temp = pd.Series(dataset[field].values.tolist())
    
    # print(len(np.where(temp.isna())[0]))
    
    cleaned_temp = np.where(temp.isna(), na_field, temp)
    # print(len(np.where(pd.Series(cleaned_temp).isna())[0]))

    dataset[f'new_{field}'] = cleaned_temp
    fielddf = pd.DataFrame(dataset[f'new_{field}'].values.tolist())
    fielddf.columns = f'{field}.'+ fielddf.columns

    for col in fielddf:
        dataset[col] = fielddf[col]

    fielddf["i"] = dataset["i"]
    fielddf.columns = fielddf.columns.str.replace(".", "_")
    return fielddf


json_base_path = "C:/Users/archi/capstone/data/processed/flows/summer/"
csv_basepath = "C:/Users/archi/capstone/data/processed/flows/tempcsvs"

# # PART 1

# folders = listdir(json_base_path)

# for folder in folders:
#     if folder == "csvs":
#         continue
#     json_files = listdir(f"{json_base_path}/{folder}")
#     for json_file_name in json_files:
#         with open(f"{json_base_path}/{folder}/{json_file_name}") as datafile:
#             df = pd.read_json(datafile, orient="records")
#             try: 
#                 audioMetadf = expand_field(df, "audioMeta", empty_field)
#                 audioMetadf.to_csv(f"{csv_basepath}/{json_file_name[:-5]}.csv", index=False)
#             except:
#                 print(json_file_name)
            


# # PART 2

# with open("creds.txt", "r") as credsfile:
#     username = credsfile.readline().strip()
#     password = credsfile.readline().strip()

# # Connect to the PostgreSQL database
# conn = psycopg2.connect(
#     host='localhost',
#     database='moj',
#     user=username,
#     password=password
# )
# cursor = conn.cursor()

# # Define the SQL query with a placeholder for the parameter
# query = """
# DELETE FROM temp_audio;

# COPY temp_audio 
# FROM %s
# WITH (FORMAT CSV);

# INSERT INTO audio (audioMeta_audioId, audioMeta_audioName, audioMeta_audioText, audioMeta_compressedThumbUrl, audioMeta_durationInMillis, audioMeta_isFavourite, audioMeta_licensed, audioMeta_popularity, audioMeta_resourceUrl, audioMeta_thumbUrl, i)
# SELECT * FROM temp_audio AS new_data(audioMeta_audioId, audioMeta_audioName, audioMeta_audioText, audioMeta_compressedThumbUrl, audioMeta_durationInMillis, audioMeta_isFavourite, audioMeta_licensed, audioMeta_popularity, audioMeta_resourceUrl, audioMeta_thumbUrl, i)
# ON CONFLICT (i) DO NOTHING;

# select count(*) from audio;
# """
# # Define the parameter value

# # Execute the query with the parameter

# final_csv_names = [f"C:/Users/archi/capstone/data/processed/flows/tempcsvs/{filename}" for filename in listdir("C:/Users/archi/capstone/data/processed/flows/tempcsvs")]

# for param_value in final_csv_names:
#     cursor.execute(query, (param_value,))
#     conn.commit()

# # Fetch the results
# results = cursor.fetchall()

# # Process the results
# for row in results:
#     print(row)

# # Close the cursor and database connection
# cursor.close()
# conn.close()



# PART 3

# folders = listdir(json_base_path)

# athcols = ['ath_DOB', 'ath_a', 'ath_authorAge', 'ath_b', 'ath_bk',
#        'ath_config_bits', 'ath_creatorBadgeDetails', 'ath_creatorGradeDetails',
#        'ath_f', 'ath_fb', 'ath_h', 'ath_i', 'ath_isVirtualGiftEnabled',
#        'ath_likeCount', 'ath_liveStreamLink', 'ath_liveStreamSchedule',
#        'ath_mbv', 'ath_n', 'ath_pc', 'ath_privacyDetails', 'ath_pu', 'ath_tu',
#        'ath_vp', 'ath_s', 'i']

# for folder in folders:
#     if folder == "csvs":
#         continue
#     json_files = listdir(f"{json_base_path}/{folder}")
#     for json_file_name in json_files:
#         with open(f"{json_base_path}/{folder}/{json_file_name}") as datafile:
#             df = pd.read_json(datafile, orient="records")
#             try: 
#                 athMetadf = expand_field(df, "ath", empty_field)
#                 athMetadf[athcols].to_csv(f"{csv_basepath}/{json_file_name[:-5]}.csv", index=False)
#             except:
#                 print(json_file_name)
            


# # PART 4

with open("creds.txt", "r") as credsfile:
    username = credsfile.readline().strip()
    password = credsfile.readline().strip()

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    host='localhost',
    database='moj',
    user=username,
    password=password
)
cursor = conn.cursor()

# Define the SQL query with a placeholder for the parameter
query = """
DELETE FROM temp_authors;

COPY temp_authors 
FROM %s
WITH (FORMAT CSV);

INSERT INTO authors (ath_DOB, ath_a, ath_authorAge, ath_b, ath_bk, ath_config_bits, ath_creatorBadgeDetails, ath_creatorGradeDetails, ath_f, ath_fb, ath_h, ath_i, ath_isVirtualGiftEnabled, ath_likeCount, ath_liveStreamLink, ath_liveStreamSchedule, ath_mbv, ath_n, ath_pc, ath_privacyDetails, ath_pu, ath_tu, ath_vp, ath_s, i)
SELECT * FROM temp_authors AS new_data(ath_DOB, ath_a, ath_authorAge, ath_b, ath_bk, ath_config_bits, ath_creatorBadgeDetails, ath_creatorGradeDetails, ath_f, ath_fb, ath_h, ath_i, ath_isVirtualGiftEnabled, ath_likeCount, ath_liveStreamLink, ath_liveStreamSchedule, ath_mbv, ath_n, ath_pc, ath_privacyDetails, ath_pu, ath_tu, ath_vp, ath_s, i)
ON CONFLICT (i) DO NOTHING;

select count(*) from authors;
"""
# Define the parameter value

# Execute the query with the parameter

final_csv_names = [f"C:/Users/archi/capstone/data/processed/flows/tempcsvs/{filename}" for filename in listdir("C:/Users/archi/capstone/data/processed/flows/tempcsvs")]

for param_value in final_csv_names:
    cursor.execute(query, (param_value,))
    conn.commit()


# Fetch the results
results = cursor.fetchall()

# Process the results
for row in results:
    print(row)

# Close the cursor and database connection
cursor.close()
conn.close()
