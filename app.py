from threading import Thread
from click import command
from flask import Flask, make_response, request, jsonify
import json
import requests
import os
import sys
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import time
from key import key
path=os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)
apikey=key()

#api to get the request message from slack
@app.route('/api/slack', methods=['POST'])
def slack_post():
   json_data = json.loads(request.data)
   print(json_data)
   try:
     challenge = json_data['challenge']
     
   except KeyError:
     challenge = None
     print("No Challenge")  
   
   if challenge is None:
     channel = json_data['event']['channel']
     ts = json_data['event']['ts']
     text = json_data['event']['text'].split(' ')[1:]
     t1 = Thread(target=send_message,kwargs={'channel':channel,'ts':ts,'text':text})
     t1.start()
    #  send_message(channel,ts, text)
   response = make_response(jsonify(challenge),200)
   print(text[0])

  #  print(response)
  #  print(response.status)
  #  print(response.headers)
  #  print(response.response)
   return response
  
#function to send the message to slack 
def send_message(channel,ts, text):
    channel_id = channel
    ts_id = ts #make this empty if you don't want to send the message as a reply message
    credentials= apikey.slackkey
    oauth_token = credentials
    client=WebClient(token=oauth_token)
   
    
    if "waflist" in text:
        
        os.system(""" 
        curl "https://docs.google.com/spreadsheets/d/e/2PACX-1vQFo3cneii8CkIaLP-kClutWu42JzRsaw1SaLYJSRQXf0EX9RyE6psTq1HZUw3WieV9Ehqh1WQ1t11j/pub?output=csv" -Ls | tr -d ' ' |  sort -V | uniq  > {}/waflist.txt
        """.format(path))
        file_name = '{}/waflist.txt'.format(path)
        msg = "附檔為 WAF ip 網段"
        try:
            result = client.files_upload(

                channels=channel_id,
                thread_ts=ts,
                initial_comment='{}'.format(msg),
                file=file_name,
            )
        except SlackApiError as text:
            url = 'https://mlytics.slack.com/api/chat.postMessage?'
            headers = { "Authorization": "Bearer " + credentials}
            data = {
                        "channel":channel_id,
                        "thread_ts": ts,
                        "text":text
                        }
            requests.post(url,json=data,headers=headers).json()

    elif "find" in text : 
      dm = text[1]
      print(dm)

      if "http" in dm :
        dm = dm.split('|')[0]
        dm = dm.replace("<http://","")
      print(dm)

      os.system("sh {}/finddm.sh {} > {}/dminfo.txt".format(path,dm,path))
      file_name = f'{path}/dminfo.txt'
      msg = f"Domain: {dm} info."
      try:
          result = client.files_upload(

              channels=channel_id,
              thread_ts=ts,
              initial_comment='{}'.format(msg),
              file=file_name,
          )
      except SlackApiError as text:
            url = 'https://mlytics.slack.com/api/chat.postMessage?'
            headers = { "Authorization": "Bearer " + credentials}
            data = {
                        "channel":channel_id,
                        "thread_ts": ts,
                        "text":text
                        }
            requests.post(url,json=data,headers=headers).json()
    
    elif "getdomainlist" in  text : 
      cusID = text[1]
      print(cusID)
      print("sh {}/getcusdm.sh {} > {}/customer-domain-list.txt".format(path,cusID,path))
      os.system(f"sh {path}/getcusdm.sh {cusID} > {path}/customer-domain-list.txt")
      file_name = f"{path}/customer-domain-list.txt"
      msg = f"This is domain list from customer {cusID}"
      try:
          result = client.files_upload(

              channels=channel_id,
              thread_ts=ts,
              initial_comment='{}'.format(msg),
              file=file_name,
          )
      except SlackApiError as text:
            url = 'https://mlytics.slack.com/api/chat.postMessage?'
            headers = { "Authorization": "Bearer " + credentials}
            data = {
                        "channel":channel_id,
                        "thread_ts": ts,
                        "text":text
                        }
            requests.post(url,data=data,headers=headers).json()

    elif "getoriginlist" in text : 
      cusID = text[1]
      print(cusID)
      print("sh {}/getorigin.sh {} > {}/customer-origin-list.txt".format(path,cusID,path))
      os.system(f"sh {path}/getorigin.sh {cusID} > {path}/customer-origin-list.txt")
      file_name = f"{path}/customer-origin-list.txt"
      msg = f"This is origin list from customer {cusID}"
      try:
          result = client.files_upload(

              channels=channel_id,
              thread_ts=ts,
              initial_comment='{}'.format(msg),
              file=file_name,
          )
      except SlackApiError as text:
            url = 'https://mlytics.slack.com/api/chat.postMessage?'
            headers = { "Authorization": "Bearer " + credentials}
            data = {
                        "channel":channel_id,
                        "thread_ts": ts,
                        "text":text
                        }
            requests.post(url,data=data,headers=headers).json()

    elif text[0] == "help" :
      msg = """
waflist
> Get waf list from devops workspace. 
> example: @Bosco_alert waflist

find <domain>
> Get about domain info. 
> example: @Bosco_alert find bosco.hxhxtyd.com

getdomainlist <CustomerID>
> Get domain list from CustomerID.
> example: @Bosco_alert getdomainlist 1001528874647

getoriginlist <CustomerID>
> Get origin list from CustomerID.
> example: @Bosco_alert getoriginlist 1001528874647

      """
      url = 'https://mlytics.slack.com/api/chat.postMessage?'
      headers = { "Authorization": "Bearer " + credentials}
      data = {
                  "channel":channel_id,
                  "thread_ts": ts,
                  "text":msg
                  }
      requests.post(url,json=data,headers=headers)


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80, debug=True)

