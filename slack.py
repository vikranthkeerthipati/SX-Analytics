import requests
from slack_bolt import App
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from logging import Logger
from sqlalchemy import create_engine, Column, Integer, String, Table,Boolean, ForeignKey
from sqlalchemy import MetaData
from sqlalchemy.pool import StaticPool
import json
from sqlalchemy.orm import sessionmaker
# from slackTables.base import Base
# from slackTables.slackuser import SlackUser
# from slackTables.profile import Profile
from slackTables import *

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
            channels = self.client.conversations_list()["channels"]
            list_of_channels = []
            for slack_channel in channels:
                channel_topic = slack_channel["topic"]
                channel_topic["creator_id"] = channel_topic.pop("creator")
                topic = Topic(**channel_topic)
                slack_channel["topic"] = topic

                channel_purpose = slack_channel["purpose"]
                channel_purpose["creator_id"] = channel_purpose.pop("creator")
                purpose = Purpose(**channel_purpose)
                slack_channel["purpose"] = purpose

                slack_channel["creator_id"] = slack_channel.pop("creator")
                # print (team for team in slack_channel.pop("shared_team_ids"))
                temp_list = []
                for team in slack_channel["shared_team_ids"]:
                    list_item = SharedTeamId(team_id=team) if "shared_team_ids" in slack_channel else SharedTeamId(team_id="")
                    temp_list.append(list_item)
                slack_channel["shared_team_ids"] = temp_list
                temp_list.clear()

                for pending in slack_channel["pending_shared"]:
                    temp_list.append(PendingShared(pending_id=pending))
                slack_channel["pending_shared"] = temp_list
                temp_list.clear()

                for pending in slack_channel["pending_connected_team_ids"]:
                    temp_list.append(PendingConnectedTeamId(pending_connected_team_id = pending))
                slack_channel["pending_connected_team_ids"] = temp_list
                temp_list.clear()

                for prevname in slack_channel["previous_names"]:
                    temp_list.append(PreviousName(previous_name=prevname))
                slack_channel["previous_names"] = temp_list
                temp_list.clear()

                channel = Channel(**slack_channel)
            self.session.add_all(list_of_channels)
            Base.metadata.create_all(self.engine)
            self.session.commit()
            for name in self.session.query(PreviousName):
                print("-------------")
                print(previous_names_previous_name)
            return("written")
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
            for slack_user in users:
                profile = slack_user["profile"]
                print(profile)
                user_profile = Profile(**profile)
                slack_user["profile"] = user_profile
                slack_user["user_id"] = slack_user.pop("id")
                user = SlackUser(**slack_user)
                list_of_users.append(user)
            self.session.add_all(list_of_users)
            Base.metadata.create_all(self.engine)
            self.session.commit()
            return("written!")
        except SlackApiError as e:
            logger.error("Error fetching conversations: {}".format(e))       




