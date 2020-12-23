import os
from googleapiclient.discovery import build
from oauth2client import file, client, tools
from apiclient import errors
from httplib2 import Http
import mimetypes
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.mime.multipart import MIMEMultipart
import os.path
import base64
import email
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


def authentication(credentials, token, scopes):
    """Authenticate to use gmail api service

    Args:
        credentials: path to the credentials json file
        token: path to the token json file
        scopes: permission levels. Should be a list

    Available scopes =  ['https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.modify',
          'https://www.googleapis.com/auth/gmail.compose'
          ]
    """
    creds = None
    if os.path.exists(token):
        with open(token, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials, scopes)
            creds = flow.run_local_server(port=0)
        with open(token, 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service


def query_mails(service, query='', label_ids=[], maxResults=None):
    """Query to filter out emails for developer's preference

    Args:
        service: email service created from authentication() function
        query: query to filter mails
        label_ids: ids of lables
        maxResults: maximum number of outputs required
    """
    try:
        response = service.users().messages().list(userId="me", q=query,
                                                   labelIds=label_ids,
                                                   maxResults=maxResults).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])

        while 'nextPageToken' in response:
            if len(messages) >= maxResults:
                break
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId="me", q=query,
                                                       labelIds=label_ids,
                                                       pageToken=page_token).execute()
            messages.extend(response['messages'])
        return messages
    except errors.HttpError as error:
        print('An error occurred: %s' % error)
        return


def send_mail(service, to, subject, content, cc=None, bcc=None, files=[]):
    """Send mail

    Args:
        service: email service created from authentication() function
        to: email address or receiver.
        comma separated email addresses for more than one address eg: john@example.com, peter@example.com
        subject: subject of the mail
        content: content of the mail
        cc: email address to whom carbon copy should be sent.comma separated email addresses for more than one address
        bcc: email address to whom blind carbon copy should be sent.comma separated email addresses for more than
        one address

    """
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = "me"
    message['subject'] = subject
    message['cc'] = cc
    message['bcc'] = bcc

    msg = MIMEText(content)
    message.attach(msg)

    for file in files:
        content_type, encoding = mimetypes.guess_type(file)

        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'
        main_type, sub_type = content_type.split('/', 1)
        fp = open(file, 'rb')
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
        fp.close()
        filename = os.path.basename(file)
        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        message.attach(msg)

        encoders.encode_base64(msg)

    try:
        raw_msg = {'raw': (base64.urlsafe_b64encode(message.as_bytes()).decode())}
        message = (service.users().messages().send(userId="me", body=raw_msg).execute())
        print('Message Id: {}'.format(message['id']))
        return message
    except errors.HttpError as error:
        print('An error occurred: {}'.format(error))


def send_mail_html(service, to, subject, content, cc=None, bcc=None, files=[]):
    """Send mail in html format

    Args:
        service: email service created from authentication() function
        to: email address or receiver.
        comma separated email addresses for more than one address eg: john@example.com, peter@example.com
        subject: subject of the mail
        content: content of the mail
        cc: email address to whom carbon copy should be sent.comma separated email addresses for more than one address
        bcc: email address to whom blind carbon copy should be sent.comma separated email addresses for more than
        one address
        files: files to be attached as a list

    """
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = "me"
    message['subject'] = subject
    message['cc'] = cc
    message['bcc'] = bcc

    msg = MIMEText(content,"html")
    message.attach(msg)

    for file in files:
        content_type, encoding = mimetypes.guess_type(file)

        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'
        main_type, sub_type = content_type.split('/', 1)
        fp = open(file, 'rb')
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
        fp.close()
        filename = os.path.basename(file)
        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        message.attach(msg)

        encoders.encode_base64(msg)

    try:
        raw_msg = {'raw': (base64.urlsafe_b64encode(message.as_bytes()).decode())}
        message = (service.users().messages().send(userId="me", body=raw_msg).execute())
        print('Message Id: {}'.format(message['id']))
        return message
    except errors.HttpError as error:
        print('An error occurred: {}'.format(error))


def reply_email(service, to, subject, content, uni_msg_id, thr_id, cc=None, bcc=None, files=[]):
    """reply to a mail

    Args:
        service: email service created from authentication() function
        to: email address or receiver.
        comma separated email addresses for more than one address eg: john@example.com, peter@example.com
        subject: subject of the mail
        content: content of the mail
        uni_msg_id: universal email id of the received mail
        thr_id: thread id of the received mail. gmail specific
        cc: email address to whom carbon copy should be sent.comma separated email addresses for more than one address
        bcc: email address to whom blind carbon copy should be sent.comma separated email addresses for more than
        one address
        files: files to be attached as a list

    """
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = "me"
    message['subject'] = subject
    message['cc'] = cc
    message['bcc'] = bcc

    msg = MIMEText(content)
    message.attach(msg)

    for file in files:
        content_type, encoding = mimetypes.guess_type(file)

        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'
        main_type, sub_type = content_type.split('/', 1)
        fp = open(file, 'rb')
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
        fp.close()
        filename = os.path.basename(file)
        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        message.attach(msg)

    message.add_header('Reference', uni_msg_id)
    message.add_header('In-Reply-To', uni_msg_id)

    try:
        raw_msg = {'raw': (base64.urlsafe_b64encode(message.as_bytes()).decode())}
        raw_msg['threadId'] = thr_id
        message = (service.users().messages().send(userId="me", body=raw_msg).execute())
        print('Message Id: {}'.format(message['id']))
        return message
    except errors.HttpError as error:
        print('An error occurred: {}'.format(error))


def reply_mail_html(service, to, subject, content, universal_msg_id, thr_id, cc=None, bcc=None, files=[]):
    """Query to filter out emails for developer's preference

    Args:
        service: email service created from authentication() function
        to: email address or receiver.
        comma separated email addresses for more than one address eg: john@example.com, peter@example.com
        subject: subject of the mail
        content: content of the mail
        universal_msg_id: universal email id of the received mail
        thr_id: thread id of the received mail. gmail specific
        cc: email address to whom carbon copy should be sent.comma separated email addresses for more than one address
        bcc: email address to whom blind carbon copy should be sent.comma separated email addresses for more than
        one address
        files: files to be attached as a list

    """

    message = MIMEMultipart()
    message['to'] = to
    message['from'] = "me"
    message['subject'] = subject
    message['cc'] = cc
    message['bcc'] = bcc

    msg = MIMEText(content,'html')
    message.attach(msg)

    for file in files:
        content_type, encoding = mimetypes.guess_type(file)

        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'
        main_type, sub_type = content_type.split('/', 1)
        fp = open(file, 'rb')
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
        fp.close()
        filename = os.path.basename(file)
        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        message.attach(msg)

    message.add_header('Reference', universal_msg_id)
    message.add_header('In-Reply-To', universal_msg_id)

    try:
        raw_msg = {'raw': (base64.urlsafe_b64encode(message.as_bytes()).decode())}
        raw_msg['threadId'] = thr_id
        message = (service.users().messages().send(userId="me", body=raw_msg).execute())
        print('Message Id: {}'.format(message['id']))
        return message
    except errors.HttpError as error:
        print('An error occurred: {}'.format(error))


def get_attachments(service, msg_id, prefix=""):
    try:
        message = service.users().messages().get(userId="me", id=msg_id).execute()

        for part in message['payload']['parts']:
            if part['filename']:
                if 'data' in part['body']:
                    data=part['body']['data']
                else:
                    att_id=part['body']['attachmentId']
                    att=service.users().messages().attachments().get(userId="me", messageId=msg_id,id=att_id).execute()
                    data=att['data']
                file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                path = prefix+part['filename']

                with open(path, 'w') as f:
                    f.write(file_data)
    except errors.HttpError as error:
        print ('An error occurred: %s' % error)


def get_google_mail_id(service, query='', label_ids=[], maxResults=1):
    email = query_mails(service, query, label_ids, maxResults)
    if len(email) == 0:
        return "No Matching Email"
    else:
        msg_id = email[0]['id']
        return msg_id


def get_google_thread_id(service,query='', label_ids=[],maxResults=1):
    email = query_mails(service, query, label_ids, maxResults)
    if len(email) == 0:
        print("No Matching Email")
    else:
        msg_id = email[0]['threadId']
        return msg_id


def get_msg_as_string(service,google_msg_id):
    try:
        message = service.users().messages().get(userId="me", id=google_msg_id).execute()
        content = str(message['snippet'])
        return content
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def get_mime_message(service, msg_id):
    try:
        message = service.users().messages().get(userId="me", id=msg_id,format='raw').execute()
        msg_str = base64.urlsafe_b64decode(message['raw']).decode()
        mime_msg = email.message_from_string(msg_str)
        return mime_msg
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def get_universal_msg_id(msg_id,gmail_service):
    try:
        ms = get_mime_message(gmail_service, msg_id)
        uni_msg_id = format(ms['Message-ID'])
        return uni_msg_id
    except Exception as e:
        print ("No Matching Email")


def get_mime_data(msg_id,data):
    try:
        ms = get_mime_message(authentication, "me", msg_id)
        uni_msg_id = format(ms[data])
        return uni_msg_id
    except Exception as e:
        print("No Matching Email")
