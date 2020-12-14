import config
from flask import Flask, request
import json
from apscheduler.scheduler import Scheduler
from datetime import datetime
import main

app = Flask(__name__)
scheduler = Scheduler({'ap.scheduler.timezone':'America/New_York'})
scheduler.start()

def daily_update():
    try:
        main.main()
        print("success")
    except:
        print("failed")
scheduler.add_interval_job(daily_update, hours = 24, start_date='2020-12-14 9:01')
@app.route("/")
def home():
    return "Hello World!"

@app.route("/sx-bot/update", methods = ['POST', 'GET'])
def handle():
    if request.method == 'POST':
        req_header = config.createHeader()
        datajsonfile = open("currentData.json","r+") 
        datajson = json.load(datajsonfile)
        req_body = config.createBody(datajson["date"],datajson["members"],datajson["active-members"],datajson["daily-posters"],datajson["messages_posted"])
        return req_body
        

if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)

