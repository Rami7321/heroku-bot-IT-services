"""
Copyright (c) 2021 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

from flask import Flask, request, jsonify
from webexteamssdk import WebexTeamsAPI
import os
import json

# Get environment variables
WT_BOT_TOKEN = os.environ['WT_BOT_TOKEN']
WT_BOT_EMAIL = os.environ['WT_BOT_EMAIL']

# Start Flask and WT connection
app = Flask(__name__)
api = WebexTeamsAPI(access_token=WT_BOT_TOKEN)


# Getting an initial message, triggering the webhook for: Messages:created
@app.route('/', methods=['POST'])
def initial_message_received():
    raw_json = request.get_json()
    print(raw_json)

    msg_from = raw_json['data']['personEmail']
    print('Message from: ' + msg_from)

    # Customize the behaviour of the bot here
    message = "Hi, I a Webex bot and I'm here to assist you with IT services.. 💻⚠ "
    
    # Replying to the same room that triggered the webhook
    WT_ROOM_ID = raw_json['data']['roomId']
    personEmail_json = raw_json['data']['personEmail']
    if personEmail_json != WT_BOT_EMAIL:
        api.messages.create(roomId=WT_ROOM_ID, markdown=message)
        api.messages.create(
            roomId=WT_ROOM_ID,
            text="Card Message: If you see this your client cannot render cards",
            attachments=[{
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": get_json_card("card.json")
            }],
        )


    return jsonify({'success': True})

# Getting an attachment action, triggering the webhook for: attachmentActions:created
@app.route('/attachment_action', methods=['POST'])
def attachment_action_recived():
    raw_json = request.get_json()
    print(raw_json)

    # Replying to the same room that triggered the webhook
    WT_ROOM_ID = raw_json['data']['roomId']
    WT_MSG_ID = raw_json['data']['messageId']
    
    # Customize the behaviour of the attachment action here

    action = api.attachment_actions.get(raw_json['data']['id'])
    selection = action['inputs']['selection']
    print('Selection: ' + selection)

    message = "Your response: '" + selection + "' has been recieved"
    api.messages.create(roomId=WT_ROOM_ID, parent=WT_MSG_ID, markdown=message)

    return jsonify({'success': True})

# Getting adaptive card data from the local file: card.json
def get_json_card(filepath):
    """
    Get content of JSON card
    """
    with open(filepath, 'r') as f:
        json_card = json.loads(f.read())
        f.close()
    return json_card


if __name__=="__main__":
    app.run()
