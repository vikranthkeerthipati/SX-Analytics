import requests
from slack_bolt import App
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from logging import Logger
from sqlalchemy import create_engine, Column, Integer, String, Table
from sqlalchemy import MetaData
from sqlalchemy.pool import StaticPool
import json
from slackTables.base import Base
from sqlalchemy.orm import sessionmaker
from slackTables.slackuser import SlackUser
from slackTables.profile import Profile


class Slack:
    def __init__(self, config):
        self.api_url = "https://slack.com/api"
        self.api_key = config['api_key']
        self.secret_key = config["secret_key"]
        self.client = WebClient(token=self.api_key)
        self.engine = create_engine("sqlite:///:memory:", echo=True,connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Session = sessionmaker(bind=self.engine)
        self.metadata = MetaData()
        self.session = Session()
        print("initialized!")

    def fetch_channels(self):
        logger = Logger("channel")
        try:
            result = self.client.conversations_list()["channels"]

            f = open("channels.json","w")
            json.dump(result, f)
            print(result)


        except SlackApiError as e:
            logger.error("Error fetching conversations: {}".format(e))
    
    def fetch_channels_history(self):
        logger = Logger("history")

        try:
            #TODO: Modify to work with SQL Tables
            f = open("channels.json","r+")
            channels = json.load(f)
            for channel in channels:
                channel_id = channel["id"]
                result = self.client.conversations_history(channel=channel_id)
                print(result)

        except SlackApiError as e:
            logger.error("Error fetching conversations: {}".format(e))
        
    def fetch_users(self):
        logger = Logger("users")
        
        try:
            users = self.client.users_list()["members"]
            list_of_users = []
            for user in users:
                profile = user["profile"]
                user_profile = Profile(title = profile["title"],
                                        phone = profile["phone"],
                                        skype = profile["skype"],
                                        real_name = profile["real_name"],
                                        real_name_normalized = profile["real_name_normalized"],
                                        display_name = profile["display_name"],
                                        display_name_normalized = profile["display_name_normalized"],
                                        status_text = profile["status_text"],
                                        status_emoji = profile["status_emoji"],
                                        status_expiration = profile["status_expiration"],
                                        avatar_hash = profile["avatar_hash"],
                                        always_active = profile["always_active"] if "always_active" in profile else False,
                                        first_name = profile["first_name"] if "first_name" in profile else "",
                                        last_name = profile["last_name"] if "last_name" in profile else "",
                                        image_24 = profile["image_24"],
                                        image_32 = profile["image_32"],
                                        image_48 = profile["image_48"],
                                        image_72 = profile["image_72"],
                                        image_192 = profile["image_192"],
                                        image_512 = profile["image_512"],
                                        status_text_canonical = profile["status_text_canonical"],
                                        team = profile["team"],
                                        )
                test_user = SlackUser(user_id=user["id"], 
                                    team_id = user["team_id"], 
                                    name = user["name"],
                                    deleted = user["deleted"],
                                    color = user["color"] if "color" in user else "",
                                    real_name = user["real_name"] if "real_name" in user else "",
                                    tz = user["tz"] if "tz" in user else "",
                                    tz_label = user["tz_label"] if "tz_label" in user else "",
                                    tz_offset = user["tz_offset"] if "tz_offset" in user else "",
                                    profile = user_profile,
                                    is_bot = user["is_bot"],
                                    is_app_user = user["is_app_user"],
                                    updated = user["updated"]
                                    )   
                list_of_users.append(test_user)
            self.session.add_all(list_of_users)
            Base.metadata.create_all(self.engine)
        except SlackApiError as e:
            logger.error("Error fetching conversations: {}".format(e))       


    def request(self, endpoint):
        url = f"{self.api_url}{endpoint}"
        headers = {
            "Authorization" : f"Bearer {self.api_key}"
        }
        return requests.get(url,headers=headers)


