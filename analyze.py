import pandas as pd
import os
import glob
import whoosh
from datetime import datetime
import config

def analyze():
    
    #Locating the saved file and reading it through PANDAS
    result = []
    while(result == []):
        path = "./"
        os.chdir(path)
        result = glob.glob('*.{}'.format("csv"))
        print(result)
    filename = result[0]
    data = pd.read_csv(filename)

    #Getting last and 2nd to last entry with associated data
    today = data.tail(1)
    yesterday = data.tail(2)
    date = today['Date'].values[0]
    total_members = today['Total membership'].values[0]
    daily_active_members = today['Daily active members'].values[0]
    daily_posters = today['Daily members posting messages'].values[0]
    weekly_active_members = today['Weekly active members'].values[0]
    weekly_posters = today['Weekly members posting messages'].values[0]
    messages_posted_today = yesterday['Messages posted'].values[1] - yesterday['Messages posted'].values[0]
    print(total_members)
    print(daily_active_members)
    print(daily_posters)
    print(messages_posted_today)

    formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%B %dth, %Y")
    #Setting up slack messages
  

    #Sets up header 
    req_headers = {'Content-type': 'application/json'}
    #Sets up text via Block Styling
    req_body = config.createBody(formatted_date, total_members.astype('U'), daily_active_members.astype('U'), daily_posters.astype('U'), messages_posted_today.astype('U'))
    whoosh.send(req_headers,req_body,filename)
