#!/bin/bash

SERVER='127.0.0.1:8080'

case $1 in
  ping)
    /usr/sbin/pidof nginx | wc -l
    ;;
  active)
    /usr/bin/curl "http://$SERVER/status" 2>/dev/null | grep 'Active' | awk '{print $NF}'
    ;;
  reading)
    /usr/bin/curl "http://$SERVER/status" 2>/dev/null | grep 'Reading' | awk '{print $2}'
    ;;
  writing)
    /usr/bin/curl "http://$SERVER/status" 2>/dev/null | grep 'Writing' | awk '{print $4}'
    ;;
  waiting)
    /usr/bin/curl "http://$SERVER/status" 2>/dev/null | grep 'Waiting' | awk '{print $6}'
    ;;
  accepts)
    /usr/bin/curl "http://$SERVER/status" 2>/dev/null | awk NR==3 | awk '{print $1}'
    ;;
  handled)
    /usr/bin/curl "http://$SERVER/status" 2>/dev/null | awk NR==3 | awk '{print $2}'
    ;;
  requests)
    /usr/bin/curl "http://$SERVER/status" 2>/dev/null | awk NR==3 | awk '{print $3}'
    ;;
  *)
   echo "Usage: %0 {active | reading | writing| waiting| accepts | handled | requests}"
   ;;
esac