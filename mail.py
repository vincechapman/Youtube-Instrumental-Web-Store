from __future__ import print_function

import base64
import mimetypes
from email.message import EmailMessage
from flask import send_file

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from googleapiclient.http import MediaIoBaseDownload

import io

'''-------------------------
MY MODULES'''
from credentials import creds
from config import sender_address
from drive import drive_service

def send_confirmation_email(order_id, beat_name, video_title, recipient_address, lease_id):

    try:
        service = build('gmail', 'v1', credentials=creds)
        message = EmailMessage()

        message.set_content(f"Thank you for your order!\nOrder Id: {order_id}, Beat: {beat_name} ({video_title})")

        message['To'] = recipient_address
        message['From'] = sender_address
        message['Subject'] = f'Your order: {beat_name} ({order_id})'

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()) \
            .decode()

        create_message = {
            'raw': encoded_message
        }
        # pylint: disable=E1101
        send_message = (service.users().messages().send
                        (userId="me", body=create_message).execute())
        print(F'Message Id: {send_message["id"]}')
    except HttpError as error:
        print(F'An error occurred: {error}')
        send_message = None
    return send_message

if __name__ == '__main__':
    send_confirmation_email('012345TEST', 'TESTBEATNAME', 'TESTVIDEOTITLE', 'vince@elevatecopy.com')
