import psycopg2
from sqlalchemy import create_engine
from sqlalchemy import text
import json
import os


# Fetch database credentials

with open("../util/creds.txt", "r") as credsfile:
    username = credsfile.readline().strip()
    password = credsfile.readline().strip()

# Connect to database

conn = psycopg2.connect(
    host='localhost',
    database='moj',
    user=username,
    password=password
)
cursor = conn.cursor()

base_path = "C:/Users/archi/capstone/audio_data"
folders = os.listdir(base_path)

for folder in folders:
    if folder != "videos_17":
        continue
    files = os.listdir(f"{base_path}/{folder}")
    for i, input_filename in enumerate(files):

        filename = input_filename[:-5]
        try:
            with open(f"{base_path}/{folder}/{input_filename}", "r", encoding='utf-8') as data:
                jsonfile = json.load(data)
            result_text = jsonfile["text"]
            result_text = result_text.replace('\'', '\'\'')
            # result_lang = jsonfile["lang"]
            # for videos_17
            result_lang = jsonfile["language"]  

            query = (f'insert into \"audio_transcripts\" values (\'{filename}\', \'{result_text}\', \'{result_lang}\') ON CONFLICT (filename) DO NOTHING;')

            cursor.execute(query)
            conn.commit()

        except:
            print(f"{folder}/{input_filename}")
        if (i % 50 == 0):
            print(f"Done with {i}")
    
cursor.close()
conn.close()