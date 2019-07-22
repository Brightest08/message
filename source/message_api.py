# -*- coding:utf-8 -*-
import re
import requests
import json
from message_controller import success, failure
from message_controller import yundama as yundama
from hashlib import md5
import codecs
import time
import execjs

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
}

def chaoxing(fun, mobile):
    s = requests.session()
    s.headers = headers
    r = s.get('http://passport2.chaoxing.com/num/phonecode?phone=%s&needcode=false' % (mobile))
    if r.json()['result']:
        return success(fun, r.text)
    failure(fun, r.text)

def asprova(fun, mobile):
    g = requests.get('http://www.asprova.cn/register.html', headers=headers)
    token = re.findall('false\|async\|(.*?)\.split', g.text)[0][:-1]
    data = {'appid': '24653', 'to': mobile, 'project': 'L4hZT2', 'signature': token}
    r = requests.post('https://api.mysubmail.com/message/xsend', headers=headers, data=data)
    if r.json()['status'] == 'success':
        return success(fun, r.text)
    failure(fun, r.text)

def morequick(fun, mobile):
    data = {'item': 'get', 'type': '5', 'tel': mobile}
    r = requests.post('https://itv.morequick.net/webapi/sms_code', data=data, headers=headers)
    if r.json() == {"ret": 1, "data": "ok"}:
        return success(fun, r.text)
    failure(fun, r.text)

def pailixiang(fun, mobile):
    s = requests.session()
    headers['Referer'] = 'http://heimaohui.pailixiang.com/register.html'
    s.headers = headers
    s.get('http://heimaohui.pailixiang.com/register.html')
    data = {'mobile': mobile}
    r = s.post('http://heimaohui.pailixiang.com/Services/SendSms.ashx?t=1&rid=reqlfd6ocg3a1ug', data=data)
    if r.json()['Code'] == 1:
        return success(fun, r.text)
    failure(fun, r.text)

def happigo(fun, mobile):
    s = requests.session()
    s.headers = headers
    g = s.get('https://www.happigo.com/register/')
    send_mobile_key = re.findall('<input type="hidden" id="send_mobile_key" name="send_mobile_key" value="(.*?)" />',g.text)[0]
    m = s.get('https://ecimg.happigo.com/resource/web/js/md5.js')
    ctx = execjs.compile(m.text)
    send_mobile_token = ctx.call('hex_md5',send_mobile_key+mobile)
    data = {'token':'ok','mobile':mobile,'send_mobile_key':send_mobile_key,'send_mobile_token':send_mobile_token,'v':'1.0','t':str(int(time.time()*1000))}
    s.headers['referer'] = 'https://www.happigo.com/register/'
    s.headers['x-requested-with'] = 'XMLHttpRequest'
    s.headers['x-tingyun-id'] = 'JEZ7HInwfsc;r=747473032'
    s.cookies['traceguid'] = 'webportalef19626169fd56134181bae74abdfd59'
    r = s.post('https://www.happigo.com/shop/index.php?act=login&op=send_auth_code&type=2',data=data)
    decoded_data = codecs.decode(bytes(r.text,encoding='utf-8'), 'utf-8-sig')
    if json.loads(decoded_data)['state'] == 'true':
        return success(fun, r.text)
    failure(fun, r.text)
