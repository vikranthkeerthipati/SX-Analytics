import parse
from flask import Flask, request
import json
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import main

#Intiailizes Flask server and scheduler for daily updates
app = Flask(__name__)
scheduler = BackgroundScheduler({'ap.scheduler.timezone':'America/New_York'})
scheduler.start()

#Runs the scraping program
def daily_update():
    try:
        print("running")
        main.main()
        print("success")
    except:
        print("failed")

#Runs every day at 9:01
scheduler.add_job(daily_update, trigger='cron',  minute="1", hour="9")

@app.route("/sx-bot/update", methods = ['POST', 'GET'])
def handle():
    print("running")
    if request.method == 'POST':
        #Creates the header and body from currentData.json
        req_header = parse.createHeader()
        datajsonfile = open("currentData.json","r+") 
        datajson = json.load(datajsonfile)
        req_body = parse.createBody(datajson["date"],datajson["members"],datajson["active-members"],datajson["daily-posters"],datajson["messages_posted"])
        return req_body
        
app.run(debug=True)

