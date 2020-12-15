from numpy.core.numeric import full
import analyze_channels
import plotly.express as px
import os
import pandas as pd
import json
import csv
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

env_path = os.path.abspath(os.getcwd())
load_dotenv(env_path+"/.env")
database_url =  os.getenv("DATABASE_URL")
engine = create_engine(database_url,poolclass=NullPool)
conn = engine.connect()
# conn = psycopg2.connect(database_url, sslmode='require')


#Get working directory and directory with channel folders


path = os.getcwd()
channel_path = path+"/community-messages/"

#If csv file doesn't exist, then run analysis(this assumes stagnant data)
if(not os.path.exists(path+"/exec.csv") or not os.path.exists(path+"/member.csv")):
    analyze_channels.analyze()

#Loading csv file as pandas df
exec_total_df = pd.read_csv(open(path + "/exec.csv","r"))
member_total_df = pd.read_csv(open(path + "/member.csv","r"))

#df with both members and execs
total_df = pd.concat([exec_total_df,member_total_df],ignore_index=True)

#List of activemembers within channel
f = open("activemembers.txt","w")
activeusers = set(total_df["Names"].unique())
for i in activeusers:
    f.write(i + "\n")
f.close()

#Opens list of users provided by slack
r = open(channel_path+"/users.json","r+")
fullusers = []
total_roster = json.load(r)

#Creating dataframe of users with name and email
for user in total_roster:
    if "profile" in user and "email" in user["profile"]:
        fullusers.append((user["profile"]["real_name_normalized"],user["profile"]["email"]))

#Creating list of inactive users with name and email
inactiveusers = []
for user in fullusers:
    if not user[0] in activeusers:
        inactiveusers.append(user)

        #This is done to make converting into a series easier

execs_roster = set(open('execs_roster.txt').read().split("\n"))
update = open(os.getcwd()+"/inactive.txt","w")
for i in inactiveusers:
    isExec = i[0] in execs_roster
    #Labels exec members
    if(isExec):
        update.write("\nEXEC MEMBER: ")
    update.write(i[0] + ", " + i[1])
    status = "Exec" if isExec else "Member"
    #Add members to the total database
    entry = pd.DataFrame({
        "Names":i[0],
        "Messages":0,
        "Channel":"general",
        "Status": status
        },index=[0])
    print(entry)
    # print(total_df.head(1))
    total_df = total_df.append(entry,ignore_index=True)
    if(i[0] in execs_roster):
        update.write("\n")
    update.write("\n")
update.close()
#Exports inactive members as txt and xlsx
updatecsv = open(path+"/inactive.txt","r+")
df = pd.read_csv(updatecsv)
df.to_excel("inactive.xlsx",index=None)


total_df.sort_values(["Channel","Messages"],ascending=[True,False],ignore_index=True,inplace=True)
print(total_df)

#UNCOMMENT BELOW IF YOU WANT TO WRITE TO HEROKU PSQL(NOTE: ALL EXISTING DATA WILL BE LOST SO BE CAREFUL!)
# total_df.to_sql("sx-data",conn,if_exists="replace",index=False)

conn.close()
#Graph with Plotly of members and exec combined
# fig = px.bar(total_df, x="Names", y="Messages",color="Channel")
# fig.update_layout(xaxis={"categoryorder":"total descending"})
# fig.show()

# #Graph with Plotly of exec
# fig_exec = px.bar(exec_total_df, x="Names", y="Messages",color="Channel")
# fig_exec.update_layout(xaxis={"categoryorder":"total descending"})
# fig_exec.show()


# #Graph with Plotly of members
# fig_member = px.bar(member_total_df, x="Names", y="Messages",color="Channel")
# fig_member.update_layout(xaxis={"categoryorder":"total descending"})
# fig_member.show()
