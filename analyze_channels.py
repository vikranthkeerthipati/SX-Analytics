import pandas as pd
import glob
import json
import csv
import os
from pandas.core.frame import DataFrame
# import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np
from datetime import datetime

path = os.getcwd()
channel_path = path+"/community-messages/"

names = []
for f in os.scandir(channel_path):
    print(f)
    if f.is_dir():   
        names.append(f.name)
big_data = pd.DataFrame()
execs_roster = set(open(path+"/execs_roster.txt").read().split("\n"))
def analyze():

    exec_total_df = pd.DataFrame(columns=["Names","Messages","Channel","Status"])
    member_total_df = pd.DataFrame(columns=["Names","Messages","Channel","Status"])
    for dirName in names:
        files_list = []
        files_list = glob.glob(channel_path + dirName + "/*.json")
        data = []
        execs = {}
        members = {}
        for v in files_list:
            with open(v,'r') as d:
                jdata = json.load(d)
                if jdata:
                    data.append(jdata)

        df = pd.DataFrame(data)
        print(df)
        members_counter = 0
        execs_counter = 0

        for index,row in df.iterrows():
            for j in range(len(df.columns)):
                if row[j] != None and "user_profile" in row[j]:
                    name = row[j]["user_profile"]["real_name"]
                    if(not name in execs_roster):
                        new_message = member_total_df[member_total_df["Names"] == name][member_total_df["Channel"] == dirName]
                        if new_message.index.values.size == 0:
                            member = [{"Names": name,"Messages":1,"Channel": dirName,"Status":"Member"}]
                            member_total_df = pd.concat([member_total_df,pd.DataFrame(member)],ignore_index=True)
                        else:
                            index = member_total_df[member_total_df["Names"] == name][member_total_df["Channel"] == dirName].index.values[0]
                            member_total_df["Messages"][index] += 1
                        members_counter+=1
                    else:
                        new_message = exec_total_df[exec_total_df["Names"] == name][exec_total_df["Channel"] == dirName]
                        if new_message.index.values.size == 0:
                            exec = [{"Names": name,"Messages":1,"Channel": dirName,"Status":"Exec"}]
                            exec_total_df = pd.concat([exec_total_df,pd.DataFrame(exec)],ignore_index=True)
                        else:
                            index = exec_total_df[exec_total_df["Names"] == name][exec_total_df["Channel"] == dirName].index.values[0]
                            exec_total_df["Messages"][index] += 1
                        execs_counter+=1
    exec_total_df.sort_values(["Channel","Messages"],ascending=[True,False],inplace=True,ignore_index=True)
    exec_total_df.to_csv("exec.csv",index=False)
    member_total_df.sort_values(["Channel","Messages"],ascending=[True,False],inplace=True,ignore_index=True)
    member_total_df.to_csv("member.csv",index=False)

def raw_analyze():
    big_data = pd.DataFrame()
    # exec_raw_df = pd.DataFrame(columns=["Date", "Time", "User", "Content", "Content-Type", "Channel", "Status", "Email"])
    # member_raw_df = pd.DataFrame(columns=["Date", "Time", "User", "Content", "Content-Type", "Channel", "Status", "Email"])
    user_list = json.load(open(channel_path+"/users.json", "r"))
    for dirName in names:
        files_list = []
        files_list = glob.glob(channel_path + dirName + "/*.json")
        data = pd.DataFrame()
        execs_roster = set(open(path+"/execs_roster.txt").read().split("\n"))
        execs = {}
        members = {}
        for v in files_list:
            with open(v,'r') as d:
                jdata = json.load(d)
                data = data.append(pd.read_json(v),ignore_index=True)

        data["Channel"] = dirName
        big_data = big_data.append(data, ignore_index=True)
    return big_data
    # big_data.to_csv("testing.csv")

def med_analyze():
    #Initializes the overall dataframe returned
    big_data = pd.DataFrame()


    #Obtains a list of users within the slack to map user ids to actual names
    user_list = json.load(open(channel_path+"/users.json", "r"))

    #Get the name of every directory in analytics
    for dirName in names:
        #Initialize and get all files under that directory(aka channel)
        files_list = []
        files_list = glob.glob(channel_path + dirName + "/*.json")

        #Initialize dataframe to be used for each channel
        data = pd.DataFrame()

        #Going through each json file in each channel
        for v in files_list:
            with open(v,'r') as d:
                #List of columns to drop from raw data(either too repetitive or requires slack api)
                drop_columns=["team",
                            "user_team",
                            "source_team",
                            "subscribed",
                            "display_as_bot",
                            "bot_profile",
                            "username",
                            "old_name",
                            "name",
                            "purpose",
                            "topic",
                            "hidden",
                            "inviter",
                            "upload",
                            "user_profile",
                            "thread_ts",
                            "parent_user_id",
                            "last_read",
                            "thread_ts",
                            "attachments",
                            "files",
                            "blocks",
                            "bot_id",
                            "root",
                            "edited",
                            
                            #The below are fields that can be received with API
                            "replies",
                            "latest_reply",
                            "reply_users"
                            ]

                #Formats current json file into pandas dataframe
                jdata = pd.read_json(v)

                #Drops each column in drop_columns list to prevent unnecessary overhead
                for column in drop_columns:
                    if column in jdata.columns:
                        jdata.drop(columns=[column],inplace=True)


                #Iterate through each row 
                for index, row in jdata.iterrows(): 

                    #Checks if there are reactions and if there is actualtion value(not NaN)
                    if "reactions" in row and not isinstance(row["reactions"],float):
                        #Goes through each reaction
                        for reaction in row["reactions"]:
                            #Goes thorugh each user for users who have reacted
                            for id in reaction["users"]:
                                #Sets up new row entry containing type, text(which will be the actual reaction), and user
                                reaction_entry = {
                                    "type": "reaction",
                                    "text": reaction["name"],
                                    "user": id,
                                    "client_msg_id": row["client_msg_id"] if "client_msg_id" in row else ""
                                }
                                #Adds the new row into channel dataframe
                                jdata = jdata.append(reaction_entry, ignore_index=True)

                    #Check if subtype is in the row(not all jsons will create this column as they dont have this action) and if its a string(prevents NaN ValueError) 
                    if "subtype" in row and type(row["subtype"]) == str:
                        #Replaces the type with subtype
                        jdata.at[index,"type"] = row["subtype"]

                    if "ts" in row and not np.isnan(row["ts"]):
                        full_time = datetime.fromtimestamp(row["ts"]).strftime("%m/%d/%Y %H:%M")
                        date_time = full_time.split(" ")
                        jdata.at[index,"date"] = date_time[0]
                        jdata.at[index,"time"] = date_time[1]
                    
                for index, row in jdata.iterrows(): 
                    if "user" in row:
                        for slack_user in user_list:
                            if(slack_user["id"] == row["user"]):
                                name = slack_user["profile"]["real_name"]
                                jdata.at[index,"user"] = name
                                status = ""
                                if name in execs_roster:
                                    status = "Exec"
                                    email = slack_user["profile"]["email"]
                                    jdata.at[index,"email"] = email
                                elif slack_user["is_bot"]:
                                    status = "Bot"
                                else:
                                    status = "Member"
                                    email = slack_user["profile"]["email"]
                                    jdata.at[index,"email"] = email
                                jdata.at[index,"status"] = status
                    
                #Adds json file's dataframe to channel's dataframe
                data = data.append(jdata,ignore_index=True)

        #For all the entries in a channel, add the channel name to the dataframe
        data["channel"] = str(dirName)
        #Adds the current channel dataframe to dataframe containing data on all channels
        big_data = big_data.append(data, ignore_index=True)

    #Drops the reaction column since we create new rows with type reaction and drops subtype since we perform substitution
    big_data.drop(columns=["reactions","subtype", "ts"],inplace=True)

    print(big_data)
    
    big_data.to_csv("testing.csv")
    return big_data
