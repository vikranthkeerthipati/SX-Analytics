import requests
from slack_bolt import App
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from logging import Logger
from sqlalchemy import create_engine, Column, Integer, String, Table,Boolean, ForeignKey
from sqlalchemy import MetaData
from sqlalchemy.pool import StaticPool
import json
from sqlalchemy.orm import sessionmaker, scoped_session
import os
from slackTables import *

class Slack:
    def __init__(self, config):
        self.api_url = "https://slack.com/api"
        self.api_key = config['api_key']
        self.secret_key = config["secret_key"]
        self.database_url = config["database_url"]
        self.client = WebClient(token=self.api_key)
        self.engine = create_engine(self.database_url,echo=True)
        # self.engine = create_engine("sqlite:///:memory:", echo=True,connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Session = scoped_session(sessionmaker(bind=self.engine))
        self.session = Session()
        Base.metadata.bind = self.engine
        print("initialized!")

    def fetch_channels(self):
        logger = Logger("channel")
        try:
            channels = self.client.conversations_list(types="public_channel, private_channel")["channels"]
            list_of_channels = []
            for slack_channel in channels:
                if "topic" in slack_channel:
                    channel_topic = slack_channel["topic"]
                    channel_topic["creator_id"] = channel_topic.pop("creator")
                    topic = Topic(**channel_topic)
                    slack_channel["topic"] = topic
                
                if "purpose" in slack_channel:
                    channel_purpose = slack_channel["purpose"]
                    channel_purpose["creator_id"] = channel_purpose.pop("creator")
                    purpose = Purpose(**channel_purpose)
                    slack_channel["purpose"] = purpose

                if "creator_id" in slack_channel:
                    slack_channel["creator_id"] = slack_channel.pop("creator")

                temp_list = []
                if "shared_team_ids" in slack_channel:
                    for team in slack_channel["shared_team_ids"]:
                        list_item = SharedTeamId(team_id=team) if "shared_team_ids" in slack_channel else SharedTeamId(team_id="")
                        temp_list.append(list_item)
                    slack_channel["shared_team_ids"] = temp_list
                    temp_list.clear()

                if "pending_shared" in slack_channel:
                    for pending in slack_channel["pending_shared"]:
                        temp_list.append(PendingShared(pending_id=pending))
                    slack_channel["pending_shared"] = temp_list
                    temp_list.clear()

                if "pending_connected_team_ids" in slack_channel:
                    for pending in slack_channel["pending_connected_team_ids"]:
                        temp_list.append(PendingConnectedTeamId(pending_connected_team_id = pending))
                    slack_channel["pending_connected_team_ids"] = temp_list
                    temp_list.clear()

                if "previous_names" in slack_channel:
                    for prevname in slack_channel["previous_names"]:
                        temp_list.append(PreviousName(previous_name=prevname))
                    slack_channel["previous_names"] = temp_list
                    temp_list.clear()   

                slack_channel["channel_id"] = slack_channel.pop("id")
                channel = Channel(**slack_channel)
                list_of_channels.append(channel)
            self.session.add_all(list_of_channels)
            Base.metadata.create_all(self.engine)
            self.session.commit()
        except SlackApiError as e:
            logger.error("Error fetching conversations: {}".format(e))
    
    def fetch_channels_history(self):
        logger = Logger("history")
        
        try:
            #TODO: Modify to work with SQL Tables
            channels = self.session.query(Channel).all()
            channel_history_list = []
            for slack_channel in channels:
                id = slack_channel.channel_id
                name = slack_channel.name
                print("0000000000")
                print(name + "\n" + id)
                print("0000000000")
                result = self.client.conversations_history(channel=id,limit=10000)["messages"]
                # f= open(id+".json","w")
                # json.dump(result, f)
                messages = []
                for slack_message in result:
                    slack_message["_type"] = slack_message.pop("type")
                    if "user" in slack_message:
                        slack_message["user_id"] = slack_message.pop("user")

                    if "blocks" in slack_message:
                        blocks = []
                        for slack_block in slack_message["blocks"]:
                            slack_block["_type"] = slack_block.pop("type")
                            if "elements" in slack_block:
                                elements = []
                                for slack_element in slack_block["elements"]:
                                    slack_element["_type"] = slack_element.pop("type")
                                    if "elements" in slack_element:
                                        slack_element["subelements"] = slack_element.pop("elements")
                                        subelements = []
                                        for slack_subelement in slack_element["subelements"]:
                                            slack_subelement["_type"] = slack_subelement.pop("type")
                                            if "text" in slack_subelement:
                                                if type(slack_subelement["text"]) is dict:
                                                    slack_subelement["text"]["_type"] = slack_subelement["text"].pop("type")
                                                    slack_subelement["text"] = Text(**slack_subelement["text"])
                                                else:
                                                    slack_subelement["text"] = Text(text=slack_subelement["text"])
                                                #0000
                                                slack_subelement.pop("text")

                                            if "elements" in slack_subelement:
                                                #TODO: Deal with elements within subelements
                                                slack_subelement.pop("elements")
                                            if "style" in slack_subelement:
                                                slack_subelement["style"] = Style(**slack_subelement["style"])
                                            subelement = Subelement(**slack_subelement)
                                            subelements.append(subelement)
                                        slack_element["subelements"] = subelements
                                    if "text" in slack_element:
                                        #0000
                                        slack_element.pop("text")
                                        # if type(slack_subelement["text"]) is dict:
                                        #     slack_element["text"]["_type"] = slack_element["text"].pop("type")
                                        #     slack_element["text"] = Text(**slack_element["text"])
                                        # else:
                                        #     slack_element["text"] = Text(text=slack_subelement["text"])
                                    element = Element(**slack_element)
                                    elements.append(element)
                                slack_block["elements"] = elements
                            if "text" in slack_block:
                                text = slack_block["text"]
                                text["_type"] = text.pop("type")
                                slack_block["text"] = [Text(**text)]
                                #00000
                                slack_block.pop("text")
                            if "fields" in slack_block:
                                fields = []
                                for slack_field in slack_block.pop("fields"):
                                    slack_field["_type"] = slack_field.pop("type")
                                    field = Text(**slack_field)
                                    fields.append(field)
                                slack_block["text"] = fields
                                #000
                                slack_block.pop("text")
                            block = Block(**slack_block)
                            blocks.append(block)
                        slack_message["blocks"] = blocks

                    if "reactions" in slack_message:
                        reactions = []
                        for slack_reaction in slack_message["reactions"]:
                            slack_reaction["reaction_users"] = slack_reaction.pop("users")
                            reaction_users = []
                            for slack_user in slack_reaction["reaction_users"]:
                                reaction_user = ReactionUser(user_id = slack_user)
                                reaction_users.append(reaction_user)
                            slack_reaction["reaction_users"] = reaction_users
                            reaction = Reaction(**slack_reaction)
                        slack_message["reactions"] = reactions

                    if "reply_users" in slack_message:
                        reply_users = []
                        for slack_reply_user in slack_message["reply_users"]:
                            reply_user = ReplyUser(user_id = slack_reply_user)
                            reply_users.append(reply_user)
                        slack_message["reply_users"] = reply_users
                    
                    if "files" in slack_message:
                        files = []
                        for slack_file in slack_message["files"]:
                            if "id" in slack_file:
                                slack_file["file_id"] = slack_file.pop("id")
                            if "user" in slack_file:
                                slack_file["user_id"] = slack_file.pop("user")
                            _file = File(**slack_file)
                            files.append(_file)
                        slack_message["files"] = files
                    
                    if "x_files" in slack_message:
                        slack_message["x_files"] = slack_message["x_files"][0]

                    if "attachments" in slack_message:
                        attachments = []
                        for slack_attachment in slack_message["attachments"]:
                            if "id" in slack_attachment:
                                slack_attachment["attachment_id"] = slack_attachment.pop("id")
                            if "mrkdwn_in" in slack_attachment:
                                slack_attachment["mrkdwn_in"] = slack_attachment["mrkdwn_in"][0]
                            if "blocks" in slack_attachment:
                                blocks = []
                                for slack_block in slack_attachment["blocks"]:
                                    slack_block["_type"] = slack_block.pop("type")
                                    if "call" in slack_block:
                                        slack_call = slack_block["call"]["v1"]
                                        slack_call["media_backend_type"] = slack_block["call"].pop("media_backend_type")
                                        if "app_icon_urls" in slack_call:
                                            slack_call["app_icon_urls"] = AppIcon(**slack_call["app_icon_urls"])
                                        call = Call(**slack_call)
                                        slack_block["call"] = call
                                    if "text" in slack_block:
                                        slack_block.pop("text")
                                        # print(slack_block)
                                        # slack_block["text"] = Text(**slack_block["text"])
                                    
                                    blocks.append(AttachmentBlock(**slack_block))
                                slack_attachment["blocks"] = blocks
                            #000000
                            if "fields" in slack_attachment:
                                slack_attachment.pop("fields")
                            attachment = Attachment(**slack_attachment)
                            attachments.append(attachment)
                        slack_message["attachments"] = attachments

                    if "pinned_to" in slack_message:
                        slack_message["pinned_to"] = slack_message["pinned_to"][0]

                    if "pinned_info" in slack_message:
                        slack_message["pinned_info"] = PinnedInfo(**slack_message["pinned_info"])

                    if "edited" in slack_message:
                        slack_message["edited"] = Edit(**slack_message["edited"])
                    
                    
                    if "root" in slack_message:
                        slack_root = slack_message.pop("root")
                        if "client_msg_id" in slack_root:
                            slack_message["root_client_msg_id"] = slack_root["client_msg_id"]
                            result.append(slack_root)
                    
                    if "bot_profile" in slack_message:
                        slack_profile = slack_message["bot_profile"]
                        if "icons" in slack_profile:
                            slack_profile["icons"] = BotIcon(**slack_profile["icons"])
                        if "id" in slack_profile:
                            slack_profile["bot_id"] = slack_profile.pop("id")
                        slack_message["bot_profile"] = BotProfile(**slack_profile)

                    if "user_profile" in slack_message:
                        slack_message["user_profile"] = UserProfile(**slack_message["user_profile"])

                    if "icons" in slack_message:
                        slack_message["icons"] = MessageIcon(**slack_message.pop("icons"))

                    message = Message(**slack_message)
                    messages.append(message)
                channel = ChannelHistory(channel_id = name, messages = messages)
                self.session.add(channel)
                Base.metadata.create_all(self.engine)
                print(channel)
                self.session.commit()
                # channel_history_list.append(channel)
            # self.session.add_all(channel_history_list)
            # Base.metadata.create_all(self.engine)
            # self.session.commit()

        except SlackApiError as e:
            logger.error("Error fetching conversations: {}".format(e))
        
        print("the goddamn thing worked")
        print(Base.metadata.tables.keys())
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
            for user in self.session.query(SlackUser).all():
                print(user.real_name)
            return("written!")
        except SlackApiError as e:
            logger.error("Error fetching conversations: {}".format(e))       




