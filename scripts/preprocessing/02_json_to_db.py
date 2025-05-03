import pandas as pd
import json
import os
from os import listdir
import psycopg2
import sys

with open("../util/schema.txt") as schemafile:
    lines = schemafile.readlines()
    cols_included = [x.split()[0] for x in lines[1:-1]]

date = sys.argv[1]

# party_names = ["aap", "aimim", "bjp", "congress", "samajwadi"]
# party_names = ["aap", "aimim", "bjp", "congress", "samajwadi", "arvindkejriwal", "kejriwal", "modi", "samajwadiparty"]

# party_names = ["rss", "rahulnahirukega", "pmmodi", "owaisi", "narendramodi", "incindia", "inc",
#                "bjpfails", "akhileshyadav" ]

# party_names = ["yogi"]
# party_names = ["modi", "owaisi", "akbaruddinowaisi", "kejriwal", "arvindkejriwal"]
party_names = ["aimim", "bjp", "samajwadi", "incindia", "akhileshyadav", 
    "gandhi", "asaduddinowaisi", "akbaruddinowaisi", "narendramodi", "pmmodi", "modi", "rss", 
    "rahulnahirukega", "bjpfails", "yogi", "samajwadiparty", "bjpfails", "owaisi", "sapa"]

json_base_path = "../../data/processed/"
csv_basepath = "../../data/processed/csvs/"

# we need to create a bunch of filenames
filenames = [f"{party}-{date}" for party in party_names]

print(filenames)

# regenerate csvs with all fields needed

for i,filename in enumerate(filenames):

    json_file_name = f"{json_base_path}{party_names[i]}/{filename}.json"

    with open(json_file_name) as datafile:
        df = pd.read_json(datafile, orient="records")
        df["party"] = party_names[i]
        
        temp = filename.split("-")

        df["collected_on"] = date
        df["updated_on"] = date

        csv_file_name = f"{csv_basepath}{filename}.csv"

        try:
            df["us"] = df["us"].fillna(0).apply(int)
            df["usc"] = df["usc"].fillna(0).apply(int)
            df["incrClipId"] = df["incrClipId"].fillna(0).apply(int)
            df[cols_included].to_csv(csv_file_name, index=False, header=False)
        except:
            df['adult'] = "0"
            df['approved'] = 1
            df['clarifaiScore'] = None
            df['permalink'] = None
            df['usc'] = 0
            df['us'] = 0
            df['y'] = None
            df['bottomVisibilityFlag'] = None
            df['encodedText'] = None
            df['favouriteCount'] = None
            df['hideHeader'] = None
            df['hidePadding'] = None
            df['c2'] = 0
            df[cols_included].to_csv(csv_file_name, index=False, header=False)


final_csv_names = [csv_basepath + filename + ".csv" for filename in filenames]

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
DELETE FROM temp_posts;

COPY temp_posts 
FROM %s
WITH (FORMAT CSV);

INSERT INTO posts (i, a, ad, adult, approved, attributedVideoUrl, audioId, authorId, authorIdStatus, b, bottomVisibilityFlag, c, c2, cd, clarifaiScore, compressedVideoUrl, d, duetEnabled, duetOriginalAuthorId, duetOriginalPostId, encodedText, encodedTextV2, favouriteCount, h, hideHeader, hidePadding, incrClipId, isFeatured, isMuted, isPrivate, l, langStatus, lc, m, meta, n, newsPublisherStatus, o, permalink, thumb, us, usc, v, w, y, post_day, post_month, post_year, post_date_string, party, collected_on, updated_on)
SELECT * FROM temp_posts AS new_data(i, a, ad, adult, approved, attributedVideoUrl, audioId, authorId, authorIdStatus, b, bottomVisibilityFlag, c, c2, cd, clarifaiScore, compressedVideoUrl, d, duetEnabled, duetOriginalAuthorId, duetOriginalPostId, encodedText, encodedTextV2, favouriteCount, h, hideHeader, hidePadding, incrClipId, isFeatured, isMuted, isPrivate, l, langStatus, lc, m, meta, n, newsPublisherStatus, o, permalink, thumb, us, usc, v, w, y, post_day, post_month, post_year, post_date_string, party, collected_on, updated_on)
ON CONFLICT (i) DO UPDATE SET updated_on = excluded.collected_on, a = excluded.a, ad = excluded.ad, adult = excluded.adult, approved = excluded.approved, attributedVideoUrl = excluded.attributedVideoUrl, audioId = excluded.audioId, authorIdStatus = excluded.authorIdStatus, b = excluded.b, bottomVisibilityFlag = excluded.bottomVisibilityFlag, c = excluded.c, c2 = excluded.c2, cd = excluded.cd, clarifaiScore = excluded.clarifaiScore, compressedVideoUrl = excluded.compressedVideoUrl, d = excluded.d, duetEnabled = excluded.duetEnabled, duetOriginalAuthorId = excluded.duetOriginalAuthorId, duetOriginalPostId = excluded.duetOriginalPostId, encodedText = excluded.encodedText, encodedTextV2 = excluded.encodedTextV2, favouriteCount = excluded.favouriteCount, h = excluded.h, hideHeader = excluded.hideHeader, hidePadding = excluded.hidePadding, incrClipId = excluded.incrClipId, isFeatured = excluded.isFeatured, isMuted = excluded.isMuted, isPrivate = excluded.isPrivate, l = excluded.l, langStatus = excluded.langStatus, lc = excluded.lc, m = excluded.m, meta = excluded.meta, n = excluded.n, newsPublisherStatus = excluded.newsPublisherStatus, o = excluded.o, permalink = excluded.permalink, thumb = excluded.thumb, us = excluded.us, usc = excluded.usc, v = excluded.v, w = excluded.w, y = excluded.y, post_day = excluded.post_day, post_month = excluded.post_month, post_year = excluded.post_year, post_date_string = excluded.post_date_string, party = excluded.party;

select count(*) from posts;
"""
# Define the parameter value

# Execute the query with the parameter

# this works
# param_value = 'C:\\Users\\archi\\capstone\\data\\processed\\flows\\summer\\csvs\\bjp-6-5-take1.csv'
# cursor.execute(query, (param_value,))

for param_value in final_csv_names:
    try:
        cursor.execute(query, (param_value,))
        conn.commit()
    except:
        print(param_value)

# Fetch the results
results = cursor.fetchall()

# Process the results
for row in results:
    print(row)

# Close the cursor and database connection
cursor.close()
conn.close()


