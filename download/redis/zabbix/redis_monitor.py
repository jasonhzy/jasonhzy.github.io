#!/usr/bin/env python
# -------------------------------------------------------------------------------
# desc :       get redis discovery
# author:      jason hu<jasonhzy@beecloud.cn>
# since:       2018-04-24 20:37
# -------------------------------------------------------------------------------
import os, sys, json

redis_cli = "/etc/redis/redis-4.0.2/src/redis-cli"
passwd = "123456"
stderror = "2>/dev/null"


#zabbix redis/sentinel ports
def get_port():
    if sys.argv[2] == 'redis':
        key = '{#REDISPORT}'
        t = os.popen("netstat -nltp|awk -F: '/redis-server/&&/LISTEN/{print $2}'|awk '{print $1}'| grep -v grep | grep -v '^$'")
    elif sys.argv[2] == 'sentinel':
        key = '{#SENTINELPORT}'
        t = os.popen("netstat -nltp|awk -F: '/redis-sentinel/&&/LISTEN/{print $2}'|awk '{print $1}'| grep -v grep | grep -v '^$'")

    ports = []
    for port in t.readlines():
        #r = os.path.basename(port.strip())
        r = port.strip()
        ports += [{key: r}]
    return json.dumps({'data': ports}, sort_keys=True, indent=4, separators=(',', ':'))

#zabbix redis server(master/salve)
def get_ping():
    return os.popen(redis_cli + " -h localhost -p " + sys.argv[2] + " -a " + passwd + " ping " + stderror + " | grep -c PONG").read().strip()

def get_info():
    r = os.popen(redis_cli + " -h localhost -p " + sys.argv[3] + " -a " + passwd + " info " + stderror + " | grep -w " + sys.argv[2] + " | cut -d: -f2").read().strip()
    if r == "" and (sys.argv[2] not in ["role"]):
        return 0
    return r

#zabbix sentinel
def get_sentinel_ping():
    return os.popen(redis_cli + " -h localhost -p " + sys.argv[2] + " ping " + stderror + " | grep -c PONG").read().strip()

def get_sentinel_info():
    if sys.argv[2] == "cluster_name":
        return os.popen(redis_cli + " -h localhost -p " + sys.argv[3] + " info " + stderror + " | grep ^master0:name | sed 's/^.*:name=//' | sed 's/,status=.*$//'").read().strip()
    elif sys.argv[2] == "slaves_num":
        command = redis_cli + " -h localhost -p " + sys.argv[3] + " info " + stderror + " | grep ^master0:name | sed 's/^.*slaves=//'|sed 's/,sentinels=.*$//'"
    elif sys.argv[2] == "sentinels_num":
        command = redis_cli + " -h localhost -p " + sys.argv[3] + " info " + stderror + " | grep ^master0:name | sed 's/^.*sentinels=//'"
    else:
        command = redis_cli + " -h localhost -p " + sys.argv[3] + " info " + stderror + " | grep -w " + sys.argv[2] + " | cut -d: -f2"

    r = os.popen(command).read().strip()
    if r == "" and (sys.argv[2] not in ["redis_mode"]):
        return 0
    return r

#zabbix items for redis
if sys.argv[1] == 'discovery':
    print(get_port())

elif sys.argv[1] == 'ping':
    print(get_ping())

elif sys.argv[1] == 'info':
    print(get_info())

elif sys.argv[1] == 'sentinel_ping':
    print(get_sentinel_ping())

elif sys.argv[1] == 'sentinel_info':
    print(get_sentinel_info())