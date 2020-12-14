import os

# username = "vkeerthipati@gatech.edu"
# password = "v39v39123"
# webhook = "https://hooks.slack.com/services/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"
# download_path = os.path.abspath(os.getcwd())
# #http://54.185.191.33/community-update/update
# listen_path = "/sx-bot/update"

def createHeader():
    return {'Content-type': 'application/json'}
def createBody(formatted_date, total_members, daily_active_members, daily_posters, messages_posted_today):
    intro_s = "It's our daily analysis of community :construction:"
    date_s = "This is an evaluation of " +  formatted_date + ""
    members_s = "As a reminder, our current number of members is " + total_members + "!"
    active_s = "Today, there were *" + daily_active_members + "* active members!"
    poster_s = "There were *" + daily_posters + "* members who posted!"
    messages_s = "Finally, *" + messages_posted_today +"* messages were sent today!"
    req_body = {
        "text": "Daily Community Update",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": intro_s,
                }
            },
            {
                "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": date_s
                        
                }
            },
            {
                "type": "divider"
            },
            {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": members_s + "\n\t:man-with-bunny-ears-partying: " + active_s + "\n\t:steam_locomotive: " + poster_s + "\n\t:memo: " + messages_s
                }
            }
        ]
    }
    return req_body
