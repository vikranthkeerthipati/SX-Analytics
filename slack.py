import requests
from slack_bolt import App
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from logging import Logger
from sqlalchemy import create_engine, Column, Integer, String, Table,Boolean, ForeignKey
from sqlalchemy import MetaData
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import SQLAlchemyError
import json
from sqlalchemy.orm import sessionmaker, scoped_session
import os
import time
from datetime import datetime
import concurrent.futures
from slackTables import *

class Slack:
    def __init__(self, config):
        self.api_url = "https://slack.com/api"
        self.user_token = config['user_token']
        self.bot_token = config['bot_token']
        self.secret_key = config["secret_key"]
        self.database_url = config["database_url"]
        self.client = WebClient(token=self.user_token)
        self.bot_client = WebClient(token=self.bot_token)
        #Testing replies api   
        self.replies = 0
        #UNCOMMENT IF YOU WISH TO WRITE TO DB
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
                    slack_channel["topic"] = self.create_topic(channel_topic)
 
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
            self.bot_client.chat_postMessage(channel="U01BRCTASEL", text=("Slack API error: " + e))
            logger.error("Error fetching conversations: {}".format(e))
            raise
        except SQLAlchemyError as e:
            self.bot_client.chat_postMessage(channel="U01BRCTASEL", text=("Database write error: " + e))
            logger.error("Error writing database: {}".format(e))
            raise
        except Exception as e:
            self.bot_client.chat_postMessage(channel="U01BRCTASEL", text=("Unknown error: " + e))
            logger.error("Error writing database: {}".format(e))
            raise




    
    def fetch_channels_history(self):
        logger = Logger("history")
        
        try:
            channels = self.session.query(Channel).all()
            channel_history_list = []
            for slack_channel in channels:
                self.replies = 0
                id = slack_channel.channel_id
                name = slack_channel.name
                print("0000000000")
                print(name + "\n" + id)
                print("0000000000")
                result = self.client.conversations_history(channel=id,limit=200)
                cursor = result["response_metadata"]["next_cursor"] if result["response_metadata"] != None else ""
                print(cursor)
                slack_messages = result["messages"]
                while(len(cursor) > 0):
                    cursor = result["response_metadata"]["next_cursor"] if result["response_metadata"] != None else ""
                    print(cursor)
                    result = self.client.conversations_history(channel=id, limit = 200, cursor = cursor)
                    slack_messages += result["messages"]
                #Uncomment to see channel information
                # f= open(id+".json","w")
                # json.dump(slack_messages, f)
                messages = []
                root_ids = set()
                for slack_message in slack_messages:
                    processed_message = self.process_message(id,slack_message)
                    message = Message(**processed_message)
                    messages.append(message)
                channel = ChannelHistory(channel_id = name, messages = messages)
                self.session.add(channel)
                Base.metadata.create_all(self.engine)
                print(channel)
                self.session.commit()
                print(self.session.query(Reply).all())
                self.bot_client.chat_postMessage(channel="U01BRCTASEL", text=(name +" written"))
                # channel_history_list.append(channel)
            # self.session.add_all(channel_history_list)
            # Base.metadata.create_all(self.engine)
            # self.session.commit()

        except SlackApiError as e:
            self.bot_client.chat_postMessage(channel="U01BRCTASEL", text=("Slack API error: " + str(e)))
            logger.error("Error fetching conversations: {}".format(e))
            raise
        except SQLAlchemyError as e:
            self.bot_client.chat_postMessage(channel="U01BRCTASEL", text=("Database write error: " + str(e)))
            logger.error("Error writing database: {}".format(e))
            raise
        except Exception as e:
            self.bot_client.chat_postMessage(channel="U01BRCTASEL", text=("Unknown error: " + str(e)))
            logger.error("Error writing database: {}".format(e))
            raise
        
        print("the goddamn thing worked")
        self.bot_client.chat_postMessage(channel="U01BRCTASEL", text=("the goddamn thing worked"))
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

    def fetch_replies(self, channel, thread_ts, client_msg_id):
        self.replies += 1
        # print("replies called: " + str(self.replies))
        print(datetime.fromtimestamp(float(thread_ts)).strftime("%m/%d/%Y") + ": " + client_msg_id)
        logger = Logger("replies")
        for attempt in range(4):
            try:
                time.sleep(1.3)
                messages = self.client.conversations_replies(channel=channel,ts=thread_ts)["messages"]
                replies = []
                for message in messages:
                    if("subtype" in message and message["subtype"] == "thread_broadcast" or "reply_count" in message and message["reply_count"] > 0):
                        message = {}
                        continue
                    message.pop("thread_ts")
                    message = self.process_message(channel,message)
                    message["root_client_msg_id"] = client_msg_id
                    message["type"] = "reply"
                    # message["reply"] = True
                    replies.append(Reply(**message))
                return replies
            except SlackApiError as e:
                if(e.response["error"] == "ratelimited"):
                    print("")
                    print("cooldown",end="",flush=True)
                    for i in range(60):
                        print(".", end="",flush=True)
                        time.sleep(0.5)
                    print("")
                    print("continuing!")
                    print("")
                    continue
                else:
                    logger.error("Error fetching conversations: {}".format(e))       

    #Creation of SQLClasses            
    def create_topic(self,channel_topic):
            channel_topic["creator_id"] = channel_topic.pop("creator")
            topic = Topic(**channel_topic)
            return topic

    def process_message(self,id,message):
        # print(".", end="",flush=True)
        slack_message = message
        slack_message["user_id"] = slack_message.pop("user","")

        if "blocks" in slack_message:
            blocks = []
            for slack_block in slack_message["blocks"]:
                slack_block["_type"] = slack_block.pop("type","")

                #Checking elements
                if "elements" in slack_block:
                    elements = []
                    #Iterating through each element
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

                                #TODO: Deal with elements within subelements
                                slack_subelement.pop("elements","")
                                if "style" in slack_subelement:
                                    slack_subelement["style"] = Style(**slack_subelement["style"])
                                subelement = Subelement(**slack_subelement)
                                subelements.append(subelement)
                            slack_element["subelements"] = subelements
                        if "text" in slack_element:
                            if type(slack_element["text"]) is dict:
                                slack_element["text"]["_type"] = slack_element["text"].pop("type")
                                slack_element["text"] = Text(**slack_element["text"])
                            else:
                                slack_element["text"] = Text(text=slack_element["text"])

                        #TODO: Include in schema
                        slack_element.pop("confirm","")
                        #TODO: Include in schema
                        slack_element.pop("fallback","")

                        # if "style" in slack_element:
                        #     if type(slack_element["style"]) is dict:
                        #         print(slack_element["style"])
                        #         slack_element["style"] = Style(slack_element["style"])
                        #     else:
                        #         print(slack_element["style"])
                        element = Element(**slack_element)
                        elements.append(element)
                    slack_block["elements"] = elements
                if "text" in slack_block:
                    text = slack_block["text"]
                    text["_type"] = text.pop("type","")
                    slack_block["text"] = [Text(**text)]

                if "fields" in slack_block:
                    fields = []
                    for slack_field in slack_block.pop("fields"):
                        slack_field["_type"] = slack_field.pop("type","")
                        field = Text(**slack_field)
                        fields.append(field)
                    slack_block["text"] = fields
                    #000
                    slack_block.pop("text")
                
                if "accessory" in slack_block:
                    slack_block["accessory"]["_type"] = slack_block["accessory"].pop("type","")
                    #TODO: Adjust for options
                    slack_block["accessory"].pop("options","")
                    slack_block["accessory"] = Accessory(**slack_block["accessory"])

                block = Block(**slack_block)
                blocks.append(block)
            slack_message["blocks"] = blocks

        if "reactions" in slack_message:
            reactions = []
            for slack_reaction in slack_message["reactions"]:
                slack_reaction["reaction_users"] = slack_reaction.pop("users","")
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
                            slack_call["media_backend_type"] = slack_block["call"].pop("media_backend_type") if "media_backend_type" in slack_call else ""
                            slack_call["call_id"] = slack_call.pop("id")
                            if "app_icon_urls" in slack_call:
                                slack_call["app_icon_urls"] = AppIcon(**slack_call["app_icon_urls"])
                            #000000
                            join = ","
                            slack_call["active_participants"] = join.join(slack_call["active_participants"])
                            slack_call["all_participants"] = join.join(slack_call["all_participants"])
                            slack_call["channels"] = slack_call["channels"][0]
                            #000000
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
                    fields = []
                    for slack_field in slack_attachment["fields"]:
                        if "type" in slack_field:
                            slack_field["_type"] = slack_field.pop("type")
                            slack_field = Field(**slack_field)
                            fields.append(slack_field)
                    slack_attachment["fields"] = fields
                if "actions" in slack_attachment:
                    actions = []
                    for slack_action in slack_attachment["actions"]:
                        slack_action["action_id"] = slack_action.pop("id")
                        slack_action["_type"] = slack_action.pop("type")
                        if(type(slack_action["text"]) is dict):
                            slack_action["text"] = Text(**slack_action["text"])
                        else:
                            slack_action["text"] = Text(text=slack_action["text"])
                        # print(slack_action["style"])
                        # slack_action["style"] = Style(**slack_action["style"])
                        action = Action(**slack_action)
                        actions.append(action)
                    slack_attachment["actions"] = actions

                if "files" in slack_attachment:
                    files = []
                    for slack_file in slack_attachment["files"]:
                        if "id" in slack_file:
                            slack_file["file_id"] = slack_file.pop("id")
                        if "user" in slack_file:
                            slack_file["user_id"] = slack_file.pop("user")
                        _file = File(**slack_file)
                        files.append(_file)
                    slack_attachment["files"] = files
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
            slack_message.pop("root")
            # slack_root = slack_message.pop("root")
            # if "client_msg_id" in slack_root:
            #     slack_message["root_client_msg_id"] = slack_root["client_msg_id"]
            #     slack_messages.append(slack_root)
        
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
        if "subtype" in slack_message and slack_message["subtype"] == "thread_broadcast":
            print("gtfo")
            slack_message.pop("thread_ts")


        if "thread_ts" in slack_message and not "reply" in slack_message:
            print("1111111")
            print(slack_message)
            thread_ts = slack_message.pop("thread_ts")
            message_id = ""
            if "client_msg_id" in slack_message:
                message_id = slack_message["client_msg_id"]
            else:
                message_id = thread_ts   
            # if(not message_id in root_ids):
            #     root_ids.add(message_id)
            if not "root_client_msg_id" in slack_message:
                replied_messages = self.fetch_replies(id, thread_ts, message_id)
                print("run")
                # slack_messages += replied_messages
                slack_message["replies"] = replied_messages
            print("1111111")
            print("")
            # else:
            #     slack_message = {}
        return slack_message
