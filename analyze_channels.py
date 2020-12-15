import pandas as pd
import glob
import json
import csv
import os

from pandas.core.frame import DataFrame
# import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np

def analyze():
    path = os.getcwd()
    channel_path = path+"/community-messages/"
    names = []

    for f in os.scandir(channel_path):
        print(f)
        if f.is_dir():   
            names.append(f.name)
    exec_total_df = pd.DataFrame(columns=["Names","Messages","Channel","Status"])
    member_total_df = pd.DataFrame(columns=["Names","Messages","Channel","Status"])
    for dirName in names:
        files_list = []
        files_list = glob.glob(channel_path + dirName + "/*.json")
        data = []
        execs_roster = set(open(path+"/execs_roster.txt").read().split("\n"))
        execs = {}
        members = {}
        for v in files_list:
            with open(v,'r') as d:
                jdata = json.load(d)
                if jdata:
                    data.append(jdata)

        df = pd.DataFrame(data)

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

