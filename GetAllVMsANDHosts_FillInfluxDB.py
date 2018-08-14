from __future__ import print_function
import atexit
from time import clock

from pyVim import connect
from pyVmomi import vim
from tools import cli
from tools import pchelper
import os
from datetime import datetime
import time
import numpy as np
import humanize
import sys

START = clock()
MBFACTOR = float(1 << 20)

#read the vCenters Config File
vCentersCSVArray = np.genfromtxt('./Config/vCenters.csv', delimiter=";",dtype=None,skip_header=1)

data = {}

d = (datetime.now()).strftime('%s.%f')
d_in_ms = int(float(d)*1000000000)
print(d_in_ms)

def GetVMHosts(content):
    print("Getting all ESX hosts ...")
    host_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                        [vim.HostSystem],
                                                        True)
    obj = [host for host in host_view.view]
    host_view.Destroy()
    return obj

def quote_ident(value):
    """Indent the quotes."""
    return "{0}".format(value
                           .replace("\\", "\\\\")
                           .replace("\"", "\\\"")
                           .replace("\n", "\\n")
                           .replace(" ", "\ "))


def Host2Dict(dc, cluster, hostname, ESXiObject):
    #dc.name, cluster.name, hostname, xhost
    hardware = ESXiObject.hardware

    memorySize = ESXiObject.hardware.memorySize
    vendor = ESXiObject.hardware.systemInfo.vendor
    model = ESXiObject.hardware.systemInfo.model
    PowerPolicy = ESXiObject.hardware.cpuPowerManagementInfo.currentPolicy

    NumCpuCores = ESXiObject.hardware.cpuInfo.numCpuCores
    NumCpuThreads = ESXiObject.hardware.cpuInfo.numCpuThreads
    NumCpuPackages = ESXiObject.hardware.cpuInfo.numCpuPackages

    Uptime = ESXiObject.summary.quickStats.uptime
    ConnectionState = ESXiObject.runtime.connectionState

    Hypervisor = ESXiObject.config.product.fullName
    HypervisorVersion = ESXiObject.config.product.version
    HypervisorBuild = ESXiObject.config.product.build
    HypervisorHyperThreadactive = ESXiObject.config.hyperThread.active

#    print(hardware)
#    print(NumCpuCores)
#    sys.exit(0)
#    data['NumCpuPackages'] = ESXiObject[hardware.cpuinfo.NumCpuPackages]

#    data[dc][cluster][host]['mem'] = {}
#    data[dc][cluster][host]['mem'] = memorySize
#    print(data)

def printHostInformation(host):
    try:
        summary = host.summary
        stats = summary.quickStats
        hardware = host.hardware
        cpuUsage = stats.overallCpuUsage
        memoryCapacity = hardware.memorySize
        memoryCapacityInMB = hardware.memorySize/MBFACTOR
        memoryUsage = stats.overallMemoryUsage
        freeMemoryPercentage = 100 - (
            (float(memoryUsage) / memoryCapacityInMB) * 100
        )
        print("-" * 70)
        print("Host name:   {0}".format(host.name))
        print("Host CPU usage:  {0}".format(cpuUsage))
        print("Host memory: {0}".format( humanize.naturalsize(memoryCapacity,binary=True)))
        print("-" * 70)
    except Exception as error:
        print("Unable to access information for host")
        print(error)
        pass

def printComputeResourceInformation(computeResource):
    try:
        hostList = computeResource.host
        print("##################################################")
        print("Compute resource name: ", computeResource.name)
        print("##################################################")
        for host in hostList:
            printHostInformation(host)
    except Exception as error:
        print("Unable to access information for compute resource ")
        print(error)
        pass

def endit():
    """
    times how long it took for this script to run.
    :return:
    """
    end = clock()
    total = end - START
    print("Completion time: {0} seconds.".format(total))

# List of properties.
# See: http://goo.gl/fjTEpW
# for all properties.

vm_properties = ["name", "config.hardware.numCPU","guest.hostName","guest.toolsVersion","guest.guestFamily","config.managedBy",
                 "config.hardware.memoryMB", "guest.guestState","summary.config.numVirtualDisks","runtime.host",
                 "config.guestFullName", "config.guestId",
                 "config.version","summary.guest.toolsRunningStatus",
                 "summary.config.numEthernetCards","config.template","summary.runtime.powerState","summary.config.vmPathName"]
#"guest.ipStack"
args = cli.get_args()
print(args)
service_instance = None
try:
    service_instance = connect.SmartConnect(host=args.host,
                                            user=args.user,
                                            pwd=args.password,
                                            port=int(args.port))
    atexit.register(connect.Disconnect, service_instance)
    atexit.register(endit)
except IOError as e:
    pass

if not service_instance:
    raise SystemExit("Unable to connect to host with supplied info.")


content_h = service_instance.RetrieveContent()
#hosts = GetVMHosts(content_h)

#for xhost in hosts:
 #data[xhost] = {}

children = content_h.rootFolder.childEntity

for child in children:  # Iterate though DataCenters
  dc = child
  data[dc.name] = {}  # Add data Centers to data dict
  clusters = dc.hostFolder.childEntity

  for cluster in clusters:  # Iterate through the clusters in the DC
    # Add Clusters to data dict
    data[dc.name][cluster.name] = {}
    hosts = cluster.host  # Variable to make pep8 compliance
    for host in hosts:  # Iterate through Hosts in the Cluster
     hostname = host.summary.config.name
     print(hostname)
     # Add VMs to data dict by config name
     data[dc.name][cluster.name][hostname] = {}
#     Host2Dict(dc.name, cluster.name, hostname, host)
     ESXiObject = host
#     hardware = ESXiObject.hardware

     memorySize = ESXiObject.hardware.memorySize
     vendor = ESXiObject.hardware.systemInfo.vendor
     model = ESXiObject.hardware.systemInfo.model
     PowerPolicy = ESXiObject.hardware.cpuPowerManagementInfo.currentPolicy

     data[dc.name][cluster.name][hostname]['powerpolicy'] = PowerPolicy
     print(data[dc.name])
     sys.exit(0)
     NumCpuCores = ESXiObject.hardware.cpuInfo.numCpuCores
     NumCpuThreads = ESXiObject.hardware.cpuInfo.numCpuThreads
     NumCpuPackages = ESXiObject.hardware.cpuInfo.numCpuPackages

     Uptime = ESXiObject.summary.quickStats.uptime
     ConnectionState = ESXiObject.runtime.connectionState

     Hypervisor = ESXiObject.config.product.fullName
     HypervisorVersion = ESXiObject.config.product.version
     HypervisorBuild = ESXiObject.config.product.build
     HypervisorHyperThreadactive = ESXiObject.config.hyperThread.active
     print(HypervisorHyperThreadactive)
sys.exit(0)


#Trying to get the full VMHost data (including the datacenters)
for datacenter in content_h.rootFolder.childEntity:
    if hasattr(datacenter.hostFolder, 'childEntity'):
                hostFolder = datacenter.hostFolder
                computeResourceList = hostFolder.childEntity
                for computeResource in computeResourceList:
                    printComputeResourceInformation(computeResource)




root_folder = service_instance.content.rootFolder
view = pchelper.get_container_view(service_instance,
                                   obj_type=[vim.VirtualMachine])

vm_data = pchelper.collect_properties(service_instance, view_ref=view,
                                      obj_type=vim.VirtualMachine,
                                      path_set=vm_properties,
                                      include_mors=True)
for vm in vm_data:
    if vm.has_key("runtime.host"):
#      print("*" * 70)
#      print("in if")
      vmHost = format((vm["runtime.host"]).name)
#      print(vmHost)
    else:
      vmHost = ''

#    host_pos = hosts.index(vmHost)
#    viewHost = hosts[host_pos]

#    print("-" * 70)
#    print("FullObject:              {0}".format(vm))
#    print("Name:                    {0}".format(vm["name"]))
#    print(                          vmHost)
#    print("CPUs:                    {0}".format(vm["config.hardware.numCPU"]))
#    print("MemoryMB:                {0}".format(vm["config.hardware.memoryMB"]))
#    print("Guest PowerState:        {0}".format(vm["guest.guestState"]))
#    print("Guest Full Name:         {0}".format(vm["config.guestFullName"]))
#    print("Guest Container Type:    {0}".format(vm["config.guestId"]))
#    print("Container Version:       {0}".format(vm["config.version"]))

    VMName = format(vm["name"])
    VMToolsStatus = format(vm["summary.guest.toolsRunningStatus"])
    if not VMToolsStatus == "guestToolsNotRunning":
        passVMHostName = format(vm["guest.hostName"])

    VMHostVM = vmHost

    if vm.has_key("guest.guestFamily"):
        VMTypeShort = format(vm["guest.guestFamily"])
    else:
        VMTypeShort = ""

    if vm.has_key("config.guestId"):
     VMTypeDetail = format(vm["config.guestId"])
    else:
     VMTypeDetail = ""

    if vm.has_key("config.guestFullName"):
     VMTypeLong = format(vm["config.guestFullName"])
    else:
     VMTypeLong = ""

    if vm.has_key("config.version"):
     VMHardWareVersion = format(vm["config.version"])
    else:
     VMHardWareVersion = ""

    if vm.has_key("guest.toolsVersion"):
        VMToolsVersion = format(vm["guest.toolsVersion"])
    else:
        VMToolsVersion = ""

    VMvCPU = int(format(vm["config.hardware.numCPU"]))
    VMRAM_MB = (int(format(vm["config.hardware.memoryMB"])) /1024)

    if vm.has_key("summary.runtime.powerState"):
     VMPowerState = format(vm["summary.runtime.powerState"])
    else:
     VMPowerState = ""

    if vm.has_key("summary.config.vmPathName"):
     VMPathDatastore = format(vm["summary.config.vmPathName"])
     FirstOccurence = int(VMPathDatastore.find("[") + 1)
     FirstOfLastOccurence = VMPathDatastore.find("]")
     VMPathDatastore = VMPathDatastore[FirstOccurence:FirstOfLastOccurence]
    else:
     VMPathDatastore = ""

    if vm.has_key("summary.config.numEthernetCards"):
     VMNetworkCardCount = format(vm["summary.config.numEthernetCards"])
    else:
     VMNetworkCardCount = ""

    if vm.has_key("summary.config.numVirtualDisks"):
     VMVirtualDisksCount = format(vm["summary.config.numVirtualDisks"])
    else:
     VMVirtualDisksCount = ""

    if vm.has_key("config.template"):
     VMTemplate = format(vm["config.template"])
    else:
     VMTemplate = ""


    cmd = "curl -XPOST http://localhost:8086/write?db=VMInventory  --data-binary "
    cmd = cmd + "'Current_VMs_Inventory,vCenter=" + quote_ident(vCentersCSVArray[0][0])
    cmd = cmd + (",VMName=" + quote_ident(VMName))
    cmd = cmd + (",PowerState=" + quote_ident (VMPowerState))
    cmd = cmd + (",VMHostVM="+ quote_ident(VMHostVM))
    cmd = cmd + ((",VMTypeShort=" + quote_ident(VMTypeShort)) if not VMTypeShort=="" else '')
    cmd = cmd + ((",VMTypeLong=" + quote_ident(VMTypeLong)) if not VMTypeLong=="" else '')
    cmd = cmd + ((",VMTypeDetail=" + quote_ident(VMTypeDetail)) if not VMTypeDetail=="" else '')
    cmd = cmd + ((",VMToolsStatus=" + quote_ident(VMToolsStatus)) if not VMToolsStatus=="" else '')
    cmd = cmd + ((",VMToolsVersion=" + quote_ident(VMToolsVersion)) if not VMToolsVersion=="" else '')
    cmd = cmd + ((",VMHardWareVersion=" + quote_ident(VMHardWareVersion)) if not VMHardWareVersion=="" else '')
    cmd = cmd + ((",VMPathDatastore=" + quote_ident(VMPathDatastore)) if not VMPathDatastore=="" else '')
    cmd = cmd + ((",VMTemplate=" + quote_ident(VMTemplate)) if not VMTemplate=="" else '')
    cmd = cmd + ((" VMvCPU=" + str(VMvCPU)) if not VMvCPU=="" else '')
    cmd = cmd + ((",VMRAM_MB=" + str(VMRAM_MB)) if not VMRAM_MB=="" else '')
    cmd = cmd + ((",VMNetworkCardCount=" + str(VMNetworkCardCount)) if not VMNetworkCardCount=="" else '')
    cmd = cmd + ((",VMVirtualDisksCount=" + str(VMVirtualDisksCount)) if not VMVirtualDisksCount=="" else '')

    cmd = cmd + " " + str(d_in_ms) + "'"

    #print(cmd)
    os.system(cmd)






print("")
print("Found {0} VirtualMachines.".format(len(vm_data)))
