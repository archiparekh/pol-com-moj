import pandas as pd
import numpy as np
from selenium import webdriver
import time

#july_links = pd.read_csv("download_csvs/july_videos_for_script.csv")
july_links = pd.read_csv("../temp/july_videos_for_script.csv")
print(len(july_links))


link_index = 0
max_links = 200

while link_index < max_links:
    
    driver = webdriver.Chrome();

    num_links = np.random.randint(6,10)

    for i in range(link_index, link_index+num_links):
        try:
            if i >= max_links:
                break

            print("fetching video...")
            driver.get(july_links.iloc[i].v);
            time_bw_links = round((np.random.random() + np.random.randint(1, 3)), 2)
            time.sleep(5)
            time.sleep(time_bw_links)


        except:
            print("Invalid URL")
    driver.quit()
    
    link_index+= num_links
    time_bw_batches = round((np.random.random() + np.random.randint(4, 15)), 2)
    time.sleep(time_bw_batches)