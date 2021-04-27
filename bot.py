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
from webexteamssdk.models.cards.card import AdaptiveCard
from webexteamssdk.models.cards.inputs import Text, Number
from webexteamssdk.models.cards.container import ColumnSet
from webexteamssdk.models.cards.components import TextBlock, Column, Image
from webexteamssdk.models.cards.actions import Submit
from webexteamssdk.utils import make_attachment
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

    # Customize the behaviour of the bot here    
    w_room_id = raw_json['data']['roomId']
    msg_from = raw_json['data']['personEmail']
    print('Message from: ' + msg_from)

    if msg_from != WT_BOT_EMAIL:
        message = "Hi, I'm a Webex bot! I'm here to assist you with IT services.. 💻⚠ "
        api.messages.create(roomId=w_room_id, markdown=message)
        send_card(w_room_id,'00_init_card.json')

        # TESTING Generating a card dynamically
        # Generating card
        buttons_list = ['request-software','request-hardware','request-access']
        g_card = generate_card(buttons_list)
        print("Card: " + str(g_card))
        print("Card in JSON: " + str(g_card.to_json))
        api.messages.create(text="Issue sending message", roomId=w_room_id, attachments=[make_attachment(g_card)])

    return jsonify({'success': True})

# Getting an attachment action, triggering the webhook for: attachmentActions:created
@app.route('/attachment_action', methods=['POST'])
def attachment_action_recived():
    raw_json = request.get_json()
    print(raw_json)

    # Customize the behaviour of the attachment action here
    
    # Getting Room and Msg information
    w_room_id = raw_json['data']['roomId']
    w_msg_id = raw_json['data']['messageId']
    
    # Getting the attachment_action on the card
    attach_action = api.attachment_actions.get(raw_json['data']['id'])
    action = attach_action.inputs['action']

    # Deleting the original message since a response has been recieved
    api.messages.delete(w_msg_id)

    # Handling cards' action buttons

    # 00-Initial Card responses:
    if action == 'request':
        send_card(w_room_id, '01_request.json')
    elif action == 'issue':
        send_card(w_room_id, '01_issue.json')   # TODO
    # 01-Request Card responses: 
    elif action == 'request-software':
        send_card(w_room_id, '02_request-software.json') # TODO
    elif action == 'request-hardware':
        send_card(w_room_id, '02_request-hardware.json')  # TODO
    elif action == 'request-access':
        send_card(w_room_id, '02_request-access.json')  # TODO
    elif action == 'request-accessories':
        send_card(w_room_id, '02_request-accessories.json')  # TODO
    # 02-Issue Card responses:
    elif action == 'issue-computer':
        send_card(w_room_id, '02_issue-computer.json')  # TODO
    elif action == 'issue-oracle':
        send_card(w_room_id, '02_issue-oracle.json')  # TODO
    elif action == 'issue-network':
        send_card(w_room_id, '02_issue-network.json')  # TODO
    elif action == 'issue-portal':
        send_card(w_room_id, '02_issue-portal.json')  # TODO
    # Responding to unhandled responses:
    else:
        message = "Your response: '" + action + "' was not recognized. Please try again.."
        api.messages.create(roomId=w_room_id, markdown=message)


    return jsonify({'success': True})

# Getting adaptive card data from the local file
def get_json_card(filepath):
    """
    Get content of JSON card
    """
    with open('cards/'+filepath, 'r') as f:
        json_card = json.loads(f.read())
        f.close()
    return json_card

# Sending an Adaptive card message to Webex room
def send_card(room_id,card_file):
    api.messages.create(
        roomId=room_id,
        text="Card Message: If you see this your client cannot render cards",
        attachments=[{
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": get_json_card(card_file)
        }],
    )

# Generating an Adaptive card with a list of buttons
def generate_card(list_of_buttons):
    c_image = Image(url="https://cdn4.iconfinder.com/data/icons/computer-technology-6/64/Error-computer-notice-warning-512.png", height="50px")
    c_text_block = TextBlock("IT Services", color="Light",size="ExtraLarge")
    col_1 = list()
    col_1.append(c_image)
    col_1.append(c_text_block)
    
    c_column_set_1 = ColumnSet(columns=col_1)
    card = AdaptiveCard(body=c_column_set_1)
    return card


if __name__=="__main__":
    app.run()
