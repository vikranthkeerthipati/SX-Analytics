import config
from flask import Flask, request
import json
app = Flask(__name__)

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
    app.run(host="0.0.0.0:5000",debug=True)

