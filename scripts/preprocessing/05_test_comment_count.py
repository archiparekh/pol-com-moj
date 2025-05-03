# For part of the dataset, the Moj API was returning 
# comment counts in a different way. Here, we review and validate the comment counts

import pandas as pd
from os import listdir
import psycopg2




"""
Read a mitmproxy dump file.
Modified from https://docs.mitmproxy.org/stable/addons-examples/#io-read-saved-flows
Takes flow file name and output file name as inputs
Run from capstone/scripts/publishing
"""
import cmd
from mitmproxy import io, http
from mitmproxy.exceptions import FlowReadException
import pprint
import sys
import json
import re
import os
import pandas as pd
import numpy as np
import datetime
import logging

def convert_to_date(t):
    if t < 0:
        return None
    return datetime.datetime.fromtimestamp(t)
def get_post_day(d):
    if d:
        return d.day
    return None  
def get_post_month(d):
    if d:
        return d.month
    return None
def get_post_year(d):
    if d:
        return d.year
    return None
def get_date_string(d):
    if d:
        return d.strftime('%Y-%m-%d')
    return ''

def convert_flow_to_json(flow_file_name, output_file_name): 
    tag_id_dict = {
        "5768886": "bjp", 
        "5110479": "congress", 
        "3824320": "aap",
        "4464286": "samajwadi",
        "5262439": "aimim",
        "5324100": "narendramodi",
        "2594918": "rahulgandhi", 
        "5128614": "akhileshyadav", 
        "2600232": "owaisi",
        "5780624": "modi", 
        "2009552": "akbaruddinowaisi",
        "2852427": "asaduddinowaisi",
        "4481165": "kejriwal",
        "4138855": "arvindkejriwal", 
        "5583320": "aaap",
        "5128611": "samajwadiparty", 
        "5750986": "yogi",
        "5702387": "inc",
        "5713020": "bjpfails",
        "24887235": "rahulnahirukega",
        "5280097": "godimedia",
        "5684543": "rss",
        "124361": "incindia",
        "5433682": "pmmodi",
        "10771546": "samajwadidigitalforce",
        "1080015": "sapa"
    }

    x = 0
    tag_id = None
    tag_id = "5768886"
    # tag_url = "https://moj-apis.sharechat.com/tag-service/v1.0.0/tag/"

    tag_url = f"https://moj-apis.sharechat.com/tag-service/v1.0.0/tag/{tag_id}"



    with open(flow_file_name, "rb") as logfile:
        with open(output_file_name, "w") as outfile:
            freader = io.FlowReader(logfile)
            outfile.write('{ \"posts\": [')  # opening for final json file
            pp = pprint.PrettyPrinter(indent=4)
            try:
                for f in freader.stream():
                    if isinstance(f, http.HTTPFlow):
                        if (tag_id == None) and (tag_url in f.request.url):
                            tag_id = re.findall('\d\d+', f.request.url)[0]
                            tag_url += tag_id
                            print(f"STORING POSTS FOR TAG {tag_id}")
                            # print(f"STORING POSTS FOR TAG {tag_id} assoc with #{tag_id_dict[tag_id]}...")
                        if tag_url in f.request.url:
                            if f.response is not None:
                                if f.response.status_code == 200:
                                    data = json.loads(f.response.get_content())
                                    # pp.pprint(data)
                                    if data['posts']:
                                        for post in data['posts']:
                                            if "c2" not in post.keys():
                                                post["c2"] = "-1"
                                            json.dump(post, outfile, indent=4)
                                            outfile.write(',')
                                            x+=1
                outfile.seek(outfile.tell() - 1, os.SEEK_SET)   # Backspace on final comma 
                # print(outfile.tell())
                outfile.write('')
                outfile.write("]}")
                print(f"SUCCESS: Wrote {x} posts to file...")
            except FlowReadException as e:
                print(f"Flow file corrupted: {e}")

def open_file(output_file_name):
    with open(output_file_name, 'r') as datafile:
        data = json.load(datafile)
        df = pd.DataFrame(data['posts'])
        return df
    
    
def count_unique_posts(df):
    num_unique = len(df.i.unique())
    print(f"{num_unique} out of {len(df)} = {num_unique/len(df)}")

    num_views = df.drop_duplicates(subset=['i']).l.apply(lambda x: int(x)).sum()
    print(f"Views: {num_views}")

def preproc(df):
    df.drop_duplicates(subset=['i'], inplace=True)
    df['o'] = pd.to_numeric(df['o'])
    df['post_datetime'] = df['o'].apply(convert_to_date)
    df['post_day'] = df['post_datetime'].apply(get_post_day)
    df['post_month'] = df['post_datetime'].apply(get_post_month)
    df['post_year'] = df['post_datetime'].apply(get_post_year)
    df['post_date_string'] = df['post_datetime'].dt.strftime('%Y-%m-%d')

    return df

party_names = "bjp congress aap samajwadi aimim".split()

def determine_json_folder(flow_name):
    for party in party_names:
        if party in flow_name:
            return party
    return flow_name.split("-")[0]


for flow in listdir("C:/Users/archi/capstone/data/raw/flows/summer")[:1]:
    
    print(flow)

    flow = "bjp-6-13"

    # read into json
    flow_file_name = "..\\..\\data\\raw\\flows\\summer\\" + flow

    json_folder = determine_json_folder(flow)

    output_file_name = f"..\\..\\data\\processed\\flows\\temp\\{flow}.json"

    print(output_file_name)

    convert_flow_to_json(flow_file_name, output_file_name)

    df = open_file(output_file_name)

    count_unique_posts(df)

    df = preproc(df)

    posts = df.to_json(orient="records")
    parsed = json.loads(posts)
    with open(output_file_name, 'w') as outfile:
        json.dump(parsed, outfile, indent=4)

    print("========================")

    

# PART 2

# create database table (i, has_c2)

# import numpy as np

# base_path = "C:/Users/archi/capstone/data/processed/flows/temp/"

# json_files = listdir(f"{base_path}")

# for json_file_name in json_files[138:]:
#     print(json_file_name)
#     with open(f"{base_path}/{json_file_name}") as datafile:
#         df = pd.read_json(datafile, orient="records")
#         df['isDisabled'] = df.ath.apply(lambda x: x['privacyDetails']['comments']['disabled'])
#         df["c2"] = np.where(((df["c2"] == -1) & (df['isDisabled'] == 0)), "0", df["c2"])
#         csv_file_name = f"C:/Users/archi/capstone/data/processed/flows/tempcsvs/{json_file_name[:-5]}.csv"
#         df[["i", "c2", "isDisabled"]].to_csv(csv_file_name, index=False)

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
# DELETE FROM temp_has_comments;

# COPY temp_has_comments 
# FROM %s
# WITH (FORMAT CSV);

# INSERT INTO has_comments (i,c2,isDisabled)
# SELECT * FROM temp_has_comments AS new_data(i,c2,isDisabled)
# ON CONFLICT (i) DO NOTHING;

# SELECT count(*) from has_comments;
# """
# # Define the parameter value

# # Execute the query with the parameter

# # this works
# # param_value = 'C:\\Users\\archi\\capstone\\data\\processed\\flows\\summer\\csvs\\bjp-6-5-take1.csv'
# # cursor.execute(query, (param_value,))

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

# PART 4
    
# def getCommentStatus(x):
#     if (x is None):
#         return 1 
#     return x['privacyDetails']['comments']['disabled'] 
# # json_file_name = "bjp-7-17-2.json"
# # json_file_name = "bjp-6-10-1.json"
# json_file_name = "yogi-8-2.json"
# # json_file_name = "bjp-6-13.json"
# base_path = "C:/Users/archi/capstone/data/processed/flows/summer/yogi/"

# with open(f"{base_path}/{json_file_name}") as datafile:
#     tempdf = pd.read_json(datafile, orient="records")
#     tempdf['isDisabled'] = tempdf.ath.apply(getCommentStatus)
#     tempdf["c2"] = np.where(((tempdf["c2"] == -1) & (tempdf['isDisabled'] == 0)), "0", tempdf["c2"])


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
# DELETE FROM temp_has_comments;

# COPY temp_has_comments 
# FROM %s
# WITH (FORMAT CSV);

# INSERT INTO has_comments (i,c2,isDisabled)
# SELECT * FROM temp_has_comments AS new_data(i,c2,isDisabled)
# ON CONFLICT (i) DO NOTHING;

# SELECT count(*) from has_comments;
# """
# # Define the parameter value

# # Execute the query with the parameter

# # this works
# # param_value = 'C:\\Users\\archi\\capstone\\data\\processed\\flows\\summer\\csvs\\bjp-6-5-take1.csv'
# # cursor.execute(query, (param_value,))

# final_csv_names = ["C:/Users/archi/capstone/data/processed/flows/tempcsvs//has_comments_with_missing.csv"]
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