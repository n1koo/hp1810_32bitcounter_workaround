Monitoring HP 1810(v1 & v2) via SNMP 
==============
HP 1810 switches use Counter32-types for counters. These counters are unreliably for traffic burst (and even less than that) with more than 100Mbps of bandwidth if you can't poll them every minute or more. 

This workaround/hack/whatnot polls the counters every 10s to avoid overflows. 

## This repo

- switch_getcounters.py, monitor the counters every 10s
- readsnmp, print the values for munin
- snmp__if_, modified Munin plugin for the interface statistics

## Original work
All the work was done by Gregor Dorfbauer ( http://blog.lagentz.com/python/handling-snmp-counter32-overflows-on-hp1810-g-correctly/
 ), but this repo has the scripts in correct intendations that the blog post doesn't.