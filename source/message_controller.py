# -*- coding:utf-8 -*-
import json
import time
import datetime
import redis
from hashlib import md5
import requests
import pymysql
import getpass
import re
import os
import sys
from tempfile import gettempdir
import chardet
import psutil
from DBUtils.SteadyDB import connect
from elasticsearch import Elasticsearch


es = Elasticsearch('es:9200',http_auth=(os.getenv('es_user'), os.getenv('es_passwd')))

ip = re.findall('window.sohu_user_ip="(.*?)"', requests.get('http://txt.go.sohu.com/ip/soip').text)[0]
pool = redis.ConnectionPool(host='redis', port=6379, decode_responses=True)
r = redis.Redis(connection_pool=pool)

already_send = 0
set_of_times = 0
mobile = ''
user_name = ''
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
}


def message_info(debug=True):
    last_m_sql = 'SELECT name FROM available_url WHERE id = (SELECT MAX(id) FROM `available_url` where black=0 and maximum is not NULL and `interval` is not NULL)'
    last_m = mysql(last_m_sql)[0][0]['name']
    all_m_sql = "SELECT `name`,`maximum`,`interval` FROM `available_url` WHERE maximum is not NULL and `interval` is not NULL and black=0"
    if not r.hget('message',last_m):
        ret = mysql(all_m_sql)[0]
        r.delete('message')
        for m in ret:
            r.hset('message', m['name'], '{"maximum":%s,"interval":%s}' % (m['maximum'], m['interval']))
    all_message_info = r.hgetall('message')
    for m_name, m_info in all_message_info.items():
        all_message_info[m_name] = json.loads(m_info)
    return all_message_info


def check_available(mg):
    sql = "SELECT available_count from `user` WHERE username = '%s'" % (user_name)
    _available_count = mysql(sql)[0][0]['available_count']
    if _available_count < set_of_times:
        print('用户:%s,账户剩余短信发送数为:%d,请充值' % (user_name, _available_count))
        sys.exit(-1)
    m_info = json.loads(r.hget(mobile, mg))
    if not m_info.get('last_time'):
        return True
    if not m_info['remainder']:
        return False
    interval = m_info['interval']
    last_send_time = datetime.datetime.strptime(m_info.get('last_time'), '%Y-%m-%d %H:%M:%S')
    now_time = datetime.datetime.strptime(get_now_time(), '%Y-%m-%d %H:%M:%S')
    delta = now_time - last_send_time
    # 可用发送数大于0 发送间隔
    if m_info['remainder'] > 0 and delta.seconds > interval:
        return True


def local_img(content):
    with open('img.png', 'wb') as f:
        f.write(content)


def login():
    print('未登录或登录信息已过期')
    while True:
        user = input('请输入用户名:')
        passwd = getpass.getpass('请输入密码:')
        sql = "SELECT password from `user` WHERE username = '%s'" % (passwd)
        if mysql(sql)[0]:
            p = mysql(sql)[0][0]['password']
        else:
            p = ''
        if p == md5(bytes(passwd, encoding='utf-8')).hexdigest():
            token = md5(bytes(user + passwd + get_now_time(), encoding='utf-8')).hexdigest()
            r.hmset(user, {'token': token, 'ip': ip, 'login_time': get_now_time()})
            with open(os.path.join(gettempdir(), 'login.json'), 'w') as f:
                data = '{"user_name":"%s","token":"%s"}' % (user, token)
                json.dump(data, f)
            print('登陆成功,请继续使用')
            sys.exit(0)
        print('账号或密码输入错误')


def check_login():
    global user_name
    if os.path.exists(os.path.join(gettempdir(), 'login.json')):
        try:
            login_file = open(os.path.join(gettempdir(), 'login.json'), 'r')
            login_info = json.loads(json.load(login_file))
            if r.exists(login_info['user_name']):
                local_token = login_info['token']
                r_token = r.hget(login_info['user_name'], 'token')
                if local_token == r_token:
                    user_name = login_info['user_name']
                    return True
        except Exception:
            pass
    login()


def init_mobile(m, s_time):
    global mobile, set_of_times
    mobile = m
    set_of_times = s_time
    if not r.exists(mobile):
        all_msg_info = message_info()
        for mg in all_msg_info:
            _m = all_msg_info[mg]
            m_info = '{"remainder": %s,"interval":%s}' % (_m['maximum'], _m['interval'])
            r.hset(mobile, mg, m_info)


def write_log(status, content):
    with open(status + '.log', 'a+') as f:
        f.write(content)
    f.close()


def get_now_time():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))


def failure(mg, text):
    if chardet.detect(bytes(text, encoding='utf-8'))['encoding'] != 'utf-8':
        text = text.encode('utf-8').decode('unicode_escape')
    now = get_now_time()
    body = {"user": user_name, "message": mg, "mobile": mobile, "ip": ip, "time": get_now_time(), "respond": text}
    write_log('error', now + ' ' + mg + ' ' + mobile + ' ' + text + ' ' + '\n')
    es.index(index='m_error_log', body=body)
    if not r.exists(user_name):
        print('你被强制下线,如有疑问请联系管理员')
        p = psutil.Process(os.getpid())
        p.terminate()
        sys.exit(-1)


def success(mg, text):
    # 发送短信成功后把当前短信接口的可用数减一，和设置的发送短信数加一，及更新最后一次成功的时间
    if chardet.detect(bytes(text, encoding='utf-8'))['encoding'] != 'utf-8':
        text = text.encode('utf-8').decode('unicode_escape')
    mobile_incr = '%s_%d' % (mobile, set_of_times)
    r.incr(mobile_incr)
    now = get_now_time()
    body = {"user": user_name, "message": mg, "mobile": mobile, "ip": ip, "time": now, "respond": text}
    es.index(index='m_success_log', body=body)
    print(now, mg, text)
    write_log('success', now + ' ' + mg + ' ' + mobile + ' ' + text + ' ' + '\n')
    m_info = json.loads(r.hget(mobile, mg))
    m_info['remainder'] = m_info['remainder'] - 1
    m_info['last_time'] = get_now_time()
    r.hset(mobile, mg, json.dumps(m_info))
    sql = "update user set send_count=send_count+1 where username = '%s'" % (user_name)
    mysql(sql)
    sql = "update user set available_count=available_count-1 where username = '%s'" % (user_name)
    mysql(sql)
    if not r.exists(user_name):
        print('你被强制下线,如有疑问请联系管理员')
        p = psutil.Process(os.getpid())
        p.terminate()
        sys.exit(-1)
    return True


def mysql(sql):
    data, result = "", ""
    host = "mysql"
    user = os.getenv('mysql_user')
    pw = os.getenv('mysql_passwd')
    db = os.getenv('mysql_db')
    port = 3306
    # 使用连接池
    connection = connect(
        creator=pymysql,host=host,
        user=user, password=pw, database=db,
        autocommit=True, charset='utf8', port=port,
        cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            connection.commit()
            if "select" or "show" in sql:
                data = cursor.fetchall()
    except Exception as e:
        print(e)
        connection.rollback()
    else:
        result = True

    finally:
        connection.close()

    return data, result


def fateadm(url=None, s=requests, code_type=4, debug=False):
    try:
        get_code_type = str([30100, 30200, 30300, 30400, 30500][code_type - 1])
    except Exception:
        get_code_type = str(code_type)
    img = s.get(url)
    img_content = img.content
    timestamp = str(int(time.time()))
    pd_id = ''
    pd_key = ''

    app_id = '313198'
    app_key = 'oIwP/WtbJZhyLz4b5y6f7dpB6ZZM6AV+'
    _sign = md5(bytes(timestamp + pd_key, encoding='utf-8')).hexdigest()
    sign = md5(bytes(pd_id + timestamp + _sign, encoding='utf-8')).hexdigest()
    _asign = md5(bytes(timestamp + app_key, encoding='utf-8')).hexdigest()
    asign = md5(bytes(app_id + timestamp + _asign, encoding='utf-8')).hexdigest()
    files = {
        'img_data': ('img_data', img_content)
    }
    data = {'user_id': pd_id,
            'timestamp': timestamp,
            'sign': sign,
            'asign': asign,
            'up_type': 'mt',
            'predict_type': get_code_type,
            }
    r = requests.post('http://pred.fateadm.com/api/capreg',
                      data=data, headers=headers, files=files)
    if r.json()['RetCode'] == '0':
        if debug:
            with open('img.png', 'wb') as f:
                f.write(img_content)
            print(json.loads(r.json()['RspData'])['result'])
        return json.loads(r.json()['RspData'])['result']
    return False


def yundama(url=None, s=requests, code_type=4, debug=False):
    get_code_type = [1001, 1002, 1003, 1004, 1005][code_type - 1]
    username = ''
    password = ''
    appid = 1
    appkey = '22cc5376925e9387a23cf797cb9ba745'
    api_url = 'http://api.yundama.com/api.php'
    codetype = get_code_type
    timeout = 60
    data = {'method': 'upload', 'username': username, 'password': password, 'appid': appid, 'appkey': appkey,
            'codetype': str(codetype), 'timeout': str(timeout)}
    img = s.get(url, headers=headers)
    img_content = img.content
    files = {'file': img_content}
    ret = requests.post(api_url, files=files, data=data)
    cid = str(ret.json()['cid'])
    ret_url = 'http://api.yundama.com/api.php?cid=%s&method=result' % cid
    while True:
        ret = requests.get(ret_url)
        data = ret.json()
        if data.get('text'):
            if debug:
                with open('img.png', 'wb') as f:
                    f.write(img_content)
                print(data.get('text'))
            return data['text']
