# -*- coding:utf-8 -*-
import argparse
from message_api import *
from message_controller import check_available, init_mobile, r, message_info,check_login
import queue
import sys
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED, as_completed
import time
import random


def sed_msg(mobile, set_of_times, interval_time, remainder):
    init_mobile(mobile, set_of_times)
    available_msg = []
    while len(available_msg) < remainder:
        m = random.choice(all_message_info)
        if check_available(m):
            available_msg.append(m)
    pool = ThreadPoolExecutor(500)
    SHARE_Q = queue.Queue(remainder)
    while SHARE_Q.qsize() < remainder:
        SHARE_Q.put(random.choice(available_msg))
    all_task = []
    for t in range(SHARE_Q.qsize()):
        mg = SHARE_Q.get()
        try:
            all_task.append(pool.submit(eval(mg), mg, mobile))
        except KeyboardInterrupt:
            r.delete('%s_%d' % (mobile, set_of_times))
            sys.exit(0)
        if interval_time:
            time.sleep(interval_time)
    wait(all_task, return_when=ALL_COMPLETED)


def main(mobile, set_of_times, interval_time):
    mobile_incr = '%s_%d' % (mobile, set_of_times)
    while True:
        if r.get(mobile_incr):
            sed_count = int(r.get(mobile_incr))
        else:
            sed_count = 0
        if sed_count >= set_of_times:
            break
        if sed_count:
            remainder = set_of_times - sed_count
        else:
            remainder = set_of_times
        sed_msg(mobile, set_of_times, interval_time, remainder)
    r.delete(mobile_incr)


if __name__ == '__main__':
    check_login()
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', required=True, type=int, dest='m', metavar='Mobile', help='接收短信的手机号码')
    parser.add_argument('-c', required=True, type=int, dest='c', metavar='Count', help='发送短信数量')
    parser.add_argument('-s', required=False, type=int, dest='s', metavar='Seconds', help='设置每条短信发送的时间间隔,默认为连续发送')
    args = parser.parse_args()
    mobile = str(args.m)
    if len(mobile) < 11 or not mobile.startswith('1'):
        sys.exit('手机号码格式错误')
    set_of_times = args.c
    interval_time = args.s
    all_message_info = [m for m in message_info()]
    try:
        main(mobile, set_of_times, interval_time)
    except KeyboardInterrupt:
        r.delete('%s_%d' % (mobile, set_of_times))
        sys.exit(0)
