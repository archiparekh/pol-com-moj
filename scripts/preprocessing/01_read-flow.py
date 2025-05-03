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
    tag_url = "https://moj-apis.sharechat.com/tag-service/v1.0.0/tag/"

    # tag_url = f"https://moj-apis.sharechat.com/tag-service/v1.0.0/tag/{tag_id}"



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


with open("00_unprocessed_flows.txt", "r") as inputfile:
    raw_filenames = [x.strip() for x in inputfile.readlines()] 

    # in an intial scenario, i am looking for specific files to convert
    # in that case the unprocessed_flows.txt file would have all the file names
    # something that might be easier is to put the date in the file and then 
    # create file names from that date.

    if raw_filenames[0][0].isnumeric():

        actual_file_names = []

        # we need to create a bunch of filenames
        for date in raw_filenames:
            for party in party_names:
                actual_file_names.append(f"{party}-{date}")
        raw_filenames = actual_file_names

# raw_filenames = os.listdir("../../data/raw/flows/summer/")

print(raw_filenames)

for flow in raw_filenames:
    
    print(flow)

    # read into json
    flow_file_name = "..\\..\\data\\raw\\" + flow

    json_folder = determine_json_folder(flow)

    output_file_name = f"..\\..\\data\\processed\\{json_folder}\\{flow}.json"

    print(output_file_name)

    convert_flow_to_json(flow_file_name, output_file_name)

    df = open_file(output_file_name)

    count_unique_posts(df)

    df = preproc(df)

    # print(df["post_datetime"].min())
    # print(df["post_datetime"].max())

    posts = df.to_json(orient="records")
    parsed = json.loads(posts)
    with open(output_file_name, 'w') as outfile:
        json.dump(parsed, outfile, indent=4)

    print("========================")

    
