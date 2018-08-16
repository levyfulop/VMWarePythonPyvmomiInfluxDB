#!/usr/bin/python
import atexit
from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
import time
import datetime
from datetime import datetime, date
from pyVmomi import vmodl
from threading import Thread
from pyVim import connect
from pyVmomi import vim
from tools import cli
from decimal import Decimal
import resource
resource.setrlimit(resource.RLIMIT_NOFILE, (65536, 65536))


class perfdata():
   def perfcounters(self):
      perfcounter=['cpu.ready.summation','cpu.usage.average','mem.usage.average','net.usage.average','datastore.totalWriteLatency.average','datastore.totalReadLatency.average','disk.numberWrite.summation','disk.numberRead.summation']
      return perfcounter

   def run(self,content,vm,counter_name):
          output=[]
#       try:
          perf_dict = {}
          perfManager = content.perfManager
          perfList = content.perfManager.perfCounter
          for counter in perfList: #build the vcenter counters for the objects
              counter_full = "{0}.{1}.{2}".format(counter.groupInfo.key,counter.nameInfo.key,counter.rollupType)
              perf_dict[counter_full] = counter.key
          counterId = perf_dict[counter_name]
          metricId = vim.PerformanceManager.MetricId(counterId=counterId,instance="")
#          query = vim.PerformanceManager.QuerySpec(entity=vm,metricId=[metricId],startTime=startTimeendTime,maxSample=60)
          query = vim.PerformanceManager.QuerySpec(entity=vm,intervalId=20,metricId=[metricId])

          stats=perfManager.QueryPerf(querySpec=[query])
          count=0
          if len(stats) > 0:
           for val in stats[0].value[0].value:
              perfinfo={}
              val = "%.2f" % (float(val)/100.00)
              perfinfo['timestamp']= (datetime.strptime(str(stats[0].sampleInfo[count].timestamp), "%Y-%m-%d %H:%M:%S+00:00"))
              perfinfo['hostname']=vm.name
              perfinfo['value']=val
              output.append(perfinfo)
              count+=1
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

   container = content.rootFolder
   viewType = [vim.VirtualMachine]
   recursive = True

   containerView = content.viewManager.CreateContainerView(container,
                                                            viewType,
                                                            recursive)
   children = containerView.view
   for child in children:
    search_index=content.searchIndex
    vm=child
    print(vm)
    for counter in counters:
        p = Thread(target=perf.run,args=(content,vm,counter,))
        if vm.summary.runtime.powerState == 'poweredOn':
         p.start()
         time.sleep(.100)

# start
if __name__ == "__main__":
    main()
