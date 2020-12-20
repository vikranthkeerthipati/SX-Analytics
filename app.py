import os
from dotenv import load_dotenv

from eventbrite import Eventbrite
from slack import Slack

load_dotenv()

slack = Slack({
    'api_key': os.environ.get("SLACK_USER_TOKEN"),
    'secret_key': os.environ.get("SLACK_SIGNING_SECRET")
})


eventbrite = Eventbrite({
    'api_key': os.environ.get('EVENTBRITE_API_KEY')
})

print(eventbrite.request('/categories'))

# slack.fetch_channels()
# slack.fetch_channels_history()

print(slack.fetch_users())
