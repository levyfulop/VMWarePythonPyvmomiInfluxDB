#!/usr/bin/env python
from pyVmomi import vim
from tools import cli
from pyVim.connect import SmartConnectNoSSL, Disconnect
import atexit
import getpass
import time
import platform
import json
start_time = time.time()

print(platform.python_version())


def main():

    args = cli.get_args()

    # Connect to the host without SSL signing
    try:
        si = SmartConnectNoSSL(
            host=args.host,
            user=args.user,
            pwd=args.password,
            port=int(args.port))
        atexit.register(Disconnect, si)

    except IOError as e:
        pass

    if not si:
        raise SystemExit("Unable to connect to host with supplied info.")

    content = si.RetrieveContent()

    # create a list of vim.VirtualMachine objects so
    # that we can query them for statistics
    container = content.rootFolder
    viewType = [vim.VirtualMachine]
    recursive = True

    containerView = content.viewManager.CreateContainerView(container,
                                                            viewType,
    root_folder = service_instance.content.rootFolder
    view = pchelper.get_container_view(service_instance,
                                   obj_type=[vim.VirtualMachine])
    vm_data = pchelper.collect_properties(service_instance, view_ref=view,
                                      obj_type=vim.VirtualMachine,
                                      path_set=vm_properties,
                                      include_mors=True)
    for vm in vm_data:
     print("-" * 70)
     print("Name:                    {0}".format(vm["name"]))
     print("BIOS UUID:               {0}".format(vm["config.uuid"]))
     print("CPUs:                    {0}".format(vm["config.hardware.numCPU"]))
     print("MemoryMB:                {0}".format(vm["config.hardware.memoryMB"]))
     print("Guest PowerState:        {0}".format(vm["guest.guestState"]))
     print("Guest Full Name:         {0}".format(vm["config.guestFullName"]))
     print("Guest Container Type:    {0}".format(vm["config.guestId"]))
     print("Container Version:       {0}".format(vm["config.version"]))

print("")
print("Found {0} VirtualMachines.".format(len(vm_data)))
if __name__ == "__main__":
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
