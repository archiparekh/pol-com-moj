from google.cloud import storage
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy import text
import json

def get_ocr(blob_name, jsonfile):
    text = []
    times=[]
    if 'text_annotations' not in jsonfile['annotation_results'][0].keys():
        return ''
    for annotation in jsonfile['annotation_results'][0]['text_annotations']:
        if ("text" in annotation.keys()):
            if (annotation['segments'][0]['confidence'] > 0.9):
                
                
                timechunk = annotation['segments'][0]['segment']["start_time_offset"]
                try:

                    offset = 0
                    if "seconds" in timechunk.keys():
                        offset += timechunk['seconds']
                    if "nanos" in timechunk.keys():
                        offset += timechunk['nanos'] / 1000000000

                    times.append(offset)
                    text.append(annotation['text'])
                except:
                    print(blob_name)
                    print('\t', timechunk)


    result = " ".join([y for (x,y) in sorted(zip(times,text))])
    return result

def get_file_name(blob_name):
    return blob_name.split("/")[-1].split()[0]

def write_read(bucket_name, blob_name):
    """Write and read a blob from GCS using file-like IO"""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"

    # The ID of your new GCS object
    # blob_name = "storage-object-name"

    storage_client = storage.Client(project="moj-thesis")
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    with blob.open("r", encoding='utf-8') as f:
        return (f.read())

# Fetch database credentials

with open("../util/creds.txt", "r") as credsfile:
    username = credsfile.readline().strip()
    password = credsfile.readline().strip()

# Create client and get files
    
bucket_name = "output-moj-video-ocr"
storage_client = storage.Client(project="moj-thesis")
blobs = storage_client.list_blobs(bucket_name)

# Turn blobs iterator into a list we can parse ourselves

blob_list = list(blobs)

# Connect to database

conn = psycopg2.connect(
    host='localhost',
    database='moj',
    user=username,
    password=password
)
cursor = conn.cursor()

start_num = 799

for i, blob in enumerate(blob_list[start_num:]):
    
    blob_name = blob.name

    filename = get_file_name(blob_name)

    data = write_read(bucket_name, blob_name)
    jsonfile = json.loads(data)
    result = get_ocr(blob_name, jsonfile)
    result = result.replace('\'', '\'\'')

    query = (f'insert into \"ocr\" values (\'{filename}\', \'{result}\') ON CONFLICT (filename) DO NOTHING;')

    cursor.execute(query)
    conn.commit()

    if (i % 50 == 0):
        print(f"Done with {i}")
    
cursor.close()
conn.close()