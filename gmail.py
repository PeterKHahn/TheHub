from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

import base64
import email
import re


def get_piazza(creds):
    res = []
    service = build('gmail', 'v1', credentials=creds)

    results = service.users().threads().list(userId='me', q='[Instr Note]', maxResults=10).execute()['threads']

    for result in results:
        identity = result['id']
        results2 = service.users().messages().get(userId='me', id=identity, format='raw').execute()


        #print(results2['messages'])
        #print(results2['raw'].encode('ASCII'))

        msg_str = str(base64.urlsafe_b64decode(results2['raw'].encode('UTF-8')))

        #mime_msg = email.message_from_string(str(msg_str))
        #print(msg_str)
        #print(type(msg_str))
        #print(msg_str)
        prog = re.compile(r'bypassing user email preferences\.\\r\\n\\r\\n(.*?)\\r\\n')

        regres = prog.findall(msg_str)
        #regres = re.findall(prog, msg_str)
        for string in regres:
            #.replace("\\r\\n", "\n").replace("=C2=A0", " ")
            res.append(regres[0])


    return res
