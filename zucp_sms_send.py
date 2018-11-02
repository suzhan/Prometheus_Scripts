#!/usr/bin/env python
#coding:utf-8

# zucp 信息 API 调用发报警信息

from flask import Flask
from flask import request
import json,commands,urllib,requests
import sys
reload(sys)
sys.setdefaultencoding('utf8')

SN = "<sn>"
PW = "<pw>"
name = "【test】"
SZ = name.decode('utf-8').encode('gbk')

def transform(text):
    textMap = json.loads(text)
    alert_list = []
    for alert in textMap['alerts']:
        print('-------------')
        #time = alert['startsAt'] + ' -- ' + alert['endsAt']
        time = alert['startsAt']
        summary = alert['annotations']['summary']
        description = alert['annotations']['description']
        status = alert['status']
        #title = alert['labels']['alertname']
        links = '【告警事件】' + summary + '\n' + '【详细信息】' + description + '\n' + '【告警时间】' + time + '\n'
    alert_list.append(links)
    return alert_list
app = Flask(__name__)

@app.route('/',methods=['POST'])
def send():
    if request.method == 'POST':
        post_data1 = request.get_data()
        #post_data = json.dumps(transform(post_data1))
        #alert_data(post_data)
    with open('./alert.log','a') as f:
        f.write(post_data1)
    post_data = transform(post_data1)
    for alertdata in post_data:
        alertdata_json = json.dumps(alertdata)
        alert_data(alertdata_json)
    return "ok"
    
def alert_data(data):
    url = 'http://sdk2.zucp.net:8060/webservice.asmx/mt?'
    data = data.decode('unicode_escape').encode('gbk')
    for mobile_number in commands.getoutput('cat ./mobile_file').split('\n'):
        Data = {"sn": SN,"pwd": PW,"mobile": mobile_number,"content": data + SZ,"ext": "","stime": "","rrid": ""}
        r = requests.get(url,params=Data)
        
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8180)

