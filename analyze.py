import pandas as pd
import os
import glob
import whoosh
from datetime import datetime
import parse
import json
import os
from dotenv import load_dotenv

env_path = os.path.abspath(os.getcwd())
load_dotenv(env_path+"/.env")

def analyze():
    
    #Locating the saved file
    result = []
    while(result == []):
        path = os.path.abspath(os.getcwd())
        os.chdir(path)
        result = glob.glob('*.{}'.format("csv"))
        print(result)
    filename = result[0]

    #Turning the read csv file into a dataframe
    data = pd.read_csv(filename)

    #Storing last and second to last rows
    today = data.tail(1)
    yesterday = data.tail(2)
    date = today['Date'].values[0]

    #Generating json file if not in path
    if(not os.path.exists(os.path.abspath(os.getcwd())+"/cumulative.json")):
        data.to_json(os.path.abspath(os.getcwd())+"/cumulative.json")

    #Appends to json file
    else:
        f = open(os.path.abspath(os.getcwd())+"/cumulative.json")
        past_data_json = json.load(f)
        past_data_df = pd.DataFrame(past_data_json)
        past_data_df.drop(past_data_df.tail(1).index, inplace=True)
        if(past_data_df['Date'].tail(1).values[0] != date):
            past_data_df.append(today, ignore_index=True)
            print("analytics updated!")
        else:
            print("today's value already added!")
        f.close()

    #Obtaining the current date    
    formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%B %dth, %Y")
    datajson = open(os.path.abspath(os.getcwd())+"/currentData.json","w")

    #Little caveat: have to switch to r+ after creating json else we can't read
    datajson = open(os.path.abspath(os.getcwd())+"/currentData.json","r+")
    empty = (datajson.read() == "")

    #Creates last row's json file is not existent
    if empty:
        print("running...")
        data = {"":""}
        json.dump(data,datajson)
    datajson.seek(0)
    currentData = json.load(datajson)

    #Saving last row data into json
    if(currentData == {"":""} or currentData['date'] != formatted_date):
        print("saving...")
        datajson.seek(0)
        datajson.truncate()
        total_members = today['Total membership'].values[0].astype('U')
        daily_active_members = today['Daily active members'].values[0].astype('U')
        daily_posters = today['Daily members posting messages'].values[0].astype('U')
        weekly_active_members = today['Weekly active members'].values[0].astype('U')
        weekly_posters = today['Weekly members posting messages'].values[0].astype('U')
        messages_posted_today = (yesterday['Messages posted'].values[1] - yesterday['Messages posted'].values[0]).astype('U')
        data = {
        "date": formatted_date,
        "members": total_members,
        "active-members": daily_active_members,
        "daily-posters": daily_posters,
        "messages_posted" : messages_posted_today
        }
        json.dump(data,datajson)  

    #Sets up header 
    req_headers = parse.createHeader()
    datajson.seek(0)
    currentData = json.load(datajson)
    #Sets up text via Block Styling
    # req_body = config.createBody(current_data.formatted_date, current_data.total_members, current_data.daily_active_members, current_data.daily_posters, current_data.messages_posted_today)
    req_body = parse.createBody(currentData["date"],currentData["members"],currentData["active-members"],currentData["daily-posters"],currentData["messages_posted"])
    whoosh.send(req_headers,req_body,filename)

