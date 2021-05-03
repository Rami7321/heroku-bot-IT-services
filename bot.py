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

    # Customize the behaviour of the bot here    
    w_room_id = raw_json['data']['roomId']
    msg_from = raw_json['data']['personEmail']
    print('Message from: ' + msg_from)

    if msg_from != WT_BOT_EMAIL:
        message = "Hi, I'm a Webex bot! I'm here to assist you with IT services.. 💻⚠ "
        api.messages.create(roomId=w_room_id, markdown=message)
        send_card(w_room_id,'000_init_card.json')

    return jsonify({'success': True})

# Getting an attachment action, triggering the webhook for: attachmentActions:created
@app.route('/attachment_action', methods=['POST'])
def attachment_action_received():
    raw_json = request.get_json()
    print(raw_json)

    # Customize the behaviour of the attachment action here
    
    # Getting Room and Msg information
    w_room_id = raw_json['data']['roomId']
    w_msg_id = raw_json['data']['messageId']
    
    # Deleting the original message since a response has been recieved
    api.messages.delete(w_msg_id)

    # Calling Webex API to get the attachment_action by id
    attach_action = api.attachment_actions.get(raw_json['data']['id'])
    
    # Checking if the recieved card is an action, or userdata, or unknown
    if('action' in attach_action.inputs):
        action = attach_action.inputs['action']

        # Handling cards' action buttons
        # 00-Initial Card responses:
        if action == 'request':
            send_card(w_room_id, '011_request.json')
        elif action == 'issue':
            send_card(w_room_id, '021_issue.json')
        
        # 01-Request Card responses: 
        elif action == 'request-software':
            send_card(w_room_id, '012_request-software.json')
        elif action == 'request-hardware':
            send_card(w_room_id, '012_request-hardware.json')
        elif action == 'request-access':
            send_card(w_room_id, '012_request-access.json')
        elif action == 'request-accessories':
            send_card(w_room_id, '012_request-accessories.json')
        
        # 02- Completed Request handling:
        elif 'request-' in action:
            request_type = action.replace('request-', '')
            message = "Your request for : **" + request_type + "** has been recieved."
            api.messages.create(roomId=w_room_id, markdown=message)
            send_card(w_room_id, '013_provide_information.json')

        elif 'submit-request' in action:
            print()

        
        # 02- Issue 'Computer, Printer, Software' handling:
        elif action == 'issue-computer-pc':
            send_card(w_room_id, '0221_issue-computer-pc.json')
        elif action == 'issue-computer-printing':
            send_card(w_room_id, '0221_issue-computer-printing.json')
        elif action == 'issue-computer-software':
            send_card(w_room_id, '0221_issue-computer-software.json')
        
        # 02- Issue 'Oracle / E-Business & Kronos' handling:
        elif action == 'issue-oracle-employee':
            send_card(w_room_id, '0222_issue-oracle-employee.json')
        elif action == 'issue-oracle-iperform':
            send_card(w_room_id, '0222_issue-oracle-iperform.json')
        elif action == 'issue-oracle-kronos':
            send_card(w_room_id, '0222_issue-oracle-kronos.json')

        # 02- Issue 'Network services' handling:
        elif action == 'issue-network-remote':
            send_card(w_room_id, '0223_issue-network-remote.json')
        elif action == 'issue-network-internet':
            send_card(w_room_id, '0223_issue-network-internet.json')
        elif action == 'issue-network-wifi':
            send_card(w_room_id, '0223_issue-network-wifi.json')

        # 02- Issue 'Portal, Website, Sharepoint, SMS' handling:
        elif action == 'issue-portal-policy':
            send_card(w_room_id, '0224_issue-portal-policy.json')
        elif action == 'issue-portal-website':
            send_card(w_room_id, '0224_issue-portal-website.json')
        elif action == 'issue-portal-intranet':
            send_card(w_room_id, '0224_issue-portal-intranet.json')
        elif action == 'issue-portal-sms':
            send_card(w_room_id, '0224_issue-portal-sms.json')

        # 03- Completed Issue handling:
        elif 'issue-' in action:
            issue = action.replace('issue-', '')
            message = "Your report for *issue*: **" + issue + "** has been recieved."
            api.messages.create(roomId=w_room_id, markdown=message)
            send_card(w_room_id, '023_ask_to_login.json')  # TODO
        
        # Responding to unhandled responses:
        else:
            message = "Your response: '" + action + "' was not recognized. Please try again.."
            api.messages.create(roomId=w_room_id, markdown=message)
    else:
        print('No actions/inputs were detected. Please contact support')
    

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


if __name__=="__main__":
    app.run()
