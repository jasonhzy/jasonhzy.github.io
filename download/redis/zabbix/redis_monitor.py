#!/usr/bin/env python
# -------------------------------------------------------------------------------
# desc :       get redis discovery
# author:      jason hu<jasonhzy@beecloud.cn>
# since:       2018-04-24 20:37
# -------------------------------------------------------------------------------
import os, sys, json

redis_cli = "/root/redis/redis-4.0.2/src/redis-cli"
passwd = "beecloud"
stderror = "2>/dev/null"


#zabbix redis/sentinel ports
def get_port():
    if sys.argv[2] == 'redis':
        key = '{#REDISPORT}'
        t = os.popen("ps -ef | grep redis-server | grep -v grep | awk -F'0.0.0.0:' '{print $2}'")
    elif sys.argv[2] == 'sentinel':
        key = '{#SENTINELPORT}'
        t = os.popen("ps -ef | grep redis-sentinel | grep -v grep | awk -F'0.0.0.0:' '{print $2}' | cut -d' ' -f1")

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
    #used_memory / maxmemory => ratio
    if sys.argv[2] == "used_memory_ratio":
        used_memory = os.popen(redis_cli + " -h localhost -p " + sys.argv[3] + " -a " + passwd + " info " + stderror + " | grep -w used_memory | cut -d: -f2").read().strip()
        maxmemory = os.popen(redis_cli + " -h localhost -p " + sys.argv[3] + " -a " + passwd + " info " + stderror + " | grep -w maxmemory | cut -d: -f2").read().strip()
        #maxmemory = os.popen(redis_cli + " -p " + sys.argv[3] + " -a " + passwd + " CONFIG GET maxmemory | tail -n1").read().strip()
        r = 0
        if maxmemory > 0:
            r = round(int(used_memory) / int(maxmemory) * 100, 2)
    else:
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
        r = os.popen(redis_cli + " -h localhost -p " + sys.argv[3] + " info " + stderror + " | grep ^master0:name | sed 's/^.*slaves=//'|sed 's/,sentinels=.*$//'").read().strip()
    elif sys.argv[2] == "sentinels_num":
        r = os.popen(redis_cli + " -h localhost -p " + sys.argv[3] + " info " + stderror + " | grep ^master0:name | sed 's/^.*sentinels=//'").read().strip()
    else:
        r = os.popen(redis_cli + " -h localhost -p " + sys.argv[3] + " info " + stderror + " | grep -w " + sys.argv[2] + " | cut -d: -f2").read().strip()
    if r == "" and (sys.argv[2] not in ["redis_mode"]):
        return 0
    return r

# write log file
def logs(conent, result="", file="/tmp/xx"):
    fsock = open(file, "a")
    fsock.write(conent)
    fsock.write("\n")
    fsock.write(result)
    fsock.write("\n")
    fsock.close()

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