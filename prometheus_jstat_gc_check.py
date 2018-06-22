#!/usr/bin/env python
#coding=utf-8

import re,time
import commands
import subprocess
import prometheus_client
from prometheus_client import Gauge,start_http_server


jstat_cmd = "/ops/jdk8/bin/jstat"
jvmname_cmd = "ps -ef | grep -v grep | grep war | awk '{print $24,$2}' |  cut -d '/' -f 5 "



jstat_dict = {
        "YGC":"Young.GC.Count",
        "FGC":"Old.GC.Count",
        "OC":"Old.Total",
        "OU":"Old.Used",
        "Young.Heap.Total":"Young.Heap.Total",
        "Young.Heap.Used":"Young.Heap.Used"
    }


def jvm_port_discovery():

    output = subprocess.Popen(jvmname_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    jvm_port_lists = output.stdout.readlines()
    jvm_port_proce = []
    for jvm_port_tmp in jvm_port_lists:
         jvm_port_proce.append(jvm_port_tmp.split())
    return jvm_port_proce



def get_status(cmd,opts,pid):

    value = commands.getoutput('sudo %s -%s %s' % (cmd,opts,pid)).strip().split('\n')

    #print value

    kv = []
    for i in value[0].split(' '):
        if i != '':
            kv.append(i)

    vv = []
    for i in value[1].split(' '):
        if i != '':
            vv.append(i)

    data = dict(zip(kv,vv))
	
    data['Young.Heap.Total'] =float(data["S0C"]) + float(data["S1C"]) + float(data["EC"])
    data['Young.Heap.Used'] =float(data["S0U"]) + float(data["S1U"]) + float(data["EU"])
    #print data
	
    return data


def get_jmx(jname,jprocess):

    status_list = []

    gcutil_data = get_status(jstat_cmd,"gc",jprocess)
    data_dict = dict(gcutil_data.items())
 
    #print data_dict
    
    for jmxkey in data_dict.keys():
        if jmxkey in jstat_dict.keys():
            cur_key = jstat_dict[jmxkey]
            status_list.append({cur_key:data_dict[jmxkey]})

    return status_list


if __name__ == '__main__':
    g = Gauge('jstat_gc','Description of gauge',['app_name','jstat_name'])
    start_http_server(9902)
    while True:
      jvmname_list = jvm_port_discovery()
      for jvm_tmp in jvmname_list:
          if len(jvm_tmp) !=2:
             continue
          else:
             jvmname = jvm_tmp[0]
             jvmprocess = jvm_tmp[1]
             for key in get_jmx(jvmname,jvmprocess):
                 for k,v in key.iteritems():
                     k = re.sub(r'-','_',k)
                     #print jvmname[:-4]
                     g.labels(app_name=jvmname[:-4],jstat_name=k).set(v)
      time.sleep(180)
