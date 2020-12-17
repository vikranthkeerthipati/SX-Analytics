import os
from dotenv import load_dotenv

from eventbrite import Eventbrite
from slack import Slack

load_dotenv()

slack = Slack({})

eventbrite = Eventbrite({
    'api_key': os.environ.get('EVENTBRITE_API_KEY')
})

print(eventbrite.request('/categories'))
