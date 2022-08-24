# More details can be found here: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sesv2.html#SESV2.Client.send_email

import boto3
from . config import from_email_address, reply_to_address

client = boto3.client('sesv2')
CHARSET = 'UTF-8'


def send_email(to_address: str, subject: str, body: str):

    response = client.send_email(
        FromEmailAddress=from_email_address['address'],
        FromEmailAddressIdentityArn=from_email_address['arn'],
        Destination={'ToAddresses': [to_address]},
        ReplyToAddresses=[reply_to_address],
        Content={
            'Simple': {
                'Subject': {
                    'Data': subject,
                    'Charset': CHARSET
                },
                'Body': {
                    'Text': {
                        'Data': body,
                        'Charset': CHARSET
                    },
                    # 'Html': {
                    #     'Data': 'string',
                    #     'Charset': CHARSET
                    # }
                }
            },
        },
    )

    return response


def send_confirmation_email(order_id, beat_name, video_title, recipient_address, lease_id):

    if __name__ == '__main__':
        def get_domain():
            return 'test.com'
    else:
        from .. import get_domain

    body = f"Order ID: {order_id}\n\nBeat: {beat_name}\nVideo name: {video_title}\n\nDownload your files and lease agreement here: {get_domain()}/{order_id}/{lease_id}/receipt\n\nFeel free to reply directly to this email if you have any questions!\n\n— Vince"

    return send_email(
        to_address=recipient_address,
        subject=f'Your order: {beat_name} ({order_id})',
        body=body
    )


if __name__ == '__main__':
    print(send_confirmation_email('012345TEST', 'TESTBEATNAME', 'TESTVIDEOTITLE', 'vince@elevatecopy.com', '1Eny9AaVXVbFvAljb2rD47pP6exeuzvPgoeW5gep-0BY'))
