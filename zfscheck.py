import subprocess
import httplib2
import os
import base64

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from email.mime.text import MIMEText

issues = []

maxCapacity = 80 # 80% for best performance, generally

## Google client section
SCOPES = ['https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/gmail.readonly']
CLIENT_SECRET_FILE = 'client_secret.json'

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

store = Storage('google_credentials.json')
credentials = store.get()
if not credentials or credentials.invalid:
    flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
    if flags:
        credentials = tools.run_flow(flow, store, flags)
    else:
        credentials = tools.run(flow, store)

http = credentials.authorize(httplib2.Http())
service = discovery.build('gmail', 'v1', http=http)

## Check capacity
currCapacity = 0
try:
    currCapacity = subprocess.check_output(['zpool', 'list', '-H', '-o', 'capacity']).replace('\n', '')
    currCapacity = int(currCapacity.replace('%', ''))
except:
    issues.append('Error checking zpool capacity')

if currCapacity > maxCapacity:
    issues.append('Low storage. zpool is at {}% capacity'.format(currCapacity))

# zpool health check
try:
    check = subprocess.check_output(['zpool', 'status', '-x']).replace('\n', '')
    if check == 'all pools are healthy':
        healthy = True
    else:
        issues.append(check)
except:
    issues.append('Error checking zpool health')

# scrub check TODO: Actually do this
volumes = []
try:
    volumes = subprocess.check_output(['zpool', 'list', '-H', '-o', 'name']).split('\n')
    volumes = filter(None, volumes)
except:
    issues.append('Error checking zpool scrub status')

if issues:
    r = service.users().getProfile(userId='me').execute()
    user = r['emailAddress']
    message = MIMEText('[*] {}'.format('\n[*] '.join(issues)))
    message['to'] = user
    message['from'] = user
    message['subject'] = 'Issues with your ZFS zpool'
    message = {'raw': base64.urlsafe_b64encode(message.as_string())}

    try:
        service.users().messages().send(userId=user, body=message).execute()
    except:
        pass
