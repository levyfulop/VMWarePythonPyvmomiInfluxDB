#!/usr/bin/python
'''
Written by Gaurav Dogra
Github: https://github.com/dograga
Script to extract vm performance data
'''
import atexit
from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
import time
import datetime
from pyVmomi import vmodl
from threading import Thread
from pyVim import connect
from pyVmomi import vim
from tools import cli


class perfdata():
   def perfcounters(self):
      perfcounter=['cpu.usage.average','mem.usage.average']
      return perfcounter

   def run(self,content,vm,counter_name):
          output=[]
#       try:
          perf_dict = {}
          perfManager = content.perfManager
          perfList = content.perfManager.perfCounter
#          print(perfList)
          for counter in perfList: #build the vcenter counters for the objects
              counter_full = "{0}.{0}.{0}".format(counter.groupInfo.key,counter.nameInfo.key,counter.rollupType)
#              perf_dict[counter_full] = counter.key
              perf_dict[counter_full] = 6
#              counterIDs = [m.counterId for m in
#                            perfManager.QueryAvailablePerfMetric(entity=vm)]
#              print(counterIDs)
#          counterId = perf_dict[counter_name]
          counterId = 6
          metricId = vim.PerformanceManager.MetricId(counterId=counterId, instance="")
          print(metricId)
          timenow=datetime.datetime.now()
          startTime = timenow - datetime.timedelta(hours=2)
          print startTime
          endTime = timenow
#          query = vim.PerformanceManager.QuerySpec(entity=vm,metricId=[metricId],startTime=startTime,endTime=endTime,maxSample=10)
          query = vim.PerformanceManager.QuerySpec(entity=vm,metricId=[metricId],maxSample=1)

#          print(query)
          stats=perfManager.QueryPerf(querySpec=[query])
          count=0
          for val in stats[0].value[0].value:
              perfinfo={}
#              val=float(val/100)
              val=val
              perfinfo['timestamp']=stats[0].sampleInfo[count].timestamp
              perfinfo['hostname']=vm.name
              perfinfo['value']=val
              output.append(perfinfo)
              count+=1
 #             print(val)
          for out in output:
              print "Counter: {0} Hostname: {1}  TimeStame: {2} Usage: {3}".format (counter_name,out['hostname'],out['timestamp'],out['value'])
#       except vmodl.MethodFault as e:
#           print("Caught vmodl fault : " + e.msg)
#          return 0
#      except Exception as e:
#          print("Caught exception : " + str(e))
#          return 0

def main():
   args = cli.get_args()
   vmip = '10.130.1.200'
   try:
        si = connect.SmartConnect(host=args.host,
                                  user=args.user,
                                  pwd=args.password,
                                  port=int(args.port))

   except:
        print "Failed to connect"
   atexit.register(Disconnect, si)
   content = si.RetrieveContent()
   perf=perfdata()
   counters=perf.perfcounters()
   print(perf)
   print(counters)
   search_index=content.searchIndex
   vm=search_index.FindByIp(None, vmip, True)
   print(vm)
   ##vm=search_index.FindByDnsName(None, vmdnsname, True)     //vm dnsname is Hostname as reported by vmtool
   for counter in counters:
        p = Thread(target=perf.run,args=(content,vm,counter,))
        p.start()

# start
if __name__ == "__main__":
    main()
