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
                                                            recursive)
    children = containerView.view
    for child in children:
     print(child)
     summary = child.summary

     print("Name       : ", summary.config.name)
     print("Template   : ", summary.config.template)
     print("Path       : ", summary.config.vmPathName)
     print("Guest      : ", summary.config.guestFullName)
     print("Instance UUID : ", summary.config.instanceUuid)
     print("Bios UUID     : ", summary.config.uuid)
     annotation = summary.config.annotation
     if annotation:
      print("Annotation : ", annotation)
     print("State      : ", summary.runtime.powerState)


if __name__ == "__main__":
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
