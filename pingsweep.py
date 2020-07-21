# The base of this code is derived from from https://rubysash.com/programming/python/python-3-multi-threaded-ping-sweep-scanner/
# Modifications to come as required

import time  # let's time our script
import os
import ipaddress  # https://docs.python.org/3/library/ipaddress.html
                  # convert ip/mask to list of hosts
import subprocess  # https://docs.python.org/3/library/subprocess.html
                   # to make a popup window quiet
import threading  # for threading functions, lock, queue
from queue import Queue  # https://docs.python.org/3/library/queue.html

# define a lock that we can use later to keep
# prints from writing over itself
print_lock = threading.Lock()

# Prompt the user to input a network address
address_list_raw = """10.192.16.0/24
10.192.17.0/24
10.192.18.0/24
10.192.19.0/24
10.192.20.0/24
10.192.21.0/24
10.192.22.0/24
10.192.23.0/24"""

#net_addr = input("Enter Network (192.168.1.0/24): ")

# actual code start time
startTime = time.time()


try:
    info = subprocess.STARTUPINFO()
    info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    info.wShowWindow = subprocess.SW_HIDE
except Exception:
    pass

for net_addr in address_list_raw.splitlines():

    # Create the network
    ip_net = ipaddress.ip_network(net_addr)

    # Get all hosts on that network
    all_hosts = list(ip_net.hosts())
    # Configure subprocess to hide the console window

    # quick message/update
    print('Sweeping Network with ICMP: ', net_addr)


    # the actual ping definition and logic.
    # it's called from a pool, repeatedly threaded, not serial
    online = []
    offline = []
    def pingsweep(ip):
        # for windows:   -n is ping count, -w is wait (ms)
        # for linux: -c is ping count, -W is wait (seconds)
        # I didn't test subprocess in linux, but know the ping count must change if OS changes
        if os.name == 'nt':
            output = subprocess.Popen(['ping', '-n', '3', '-w', '300', str(
                all_hosts[ip])], stdout = subprocess.PIPE, startupinfo=info).communicate()[0]
        elif os.name == 'posix':
            output = subprocess.Popen(['ping', '-c', '3', '-W', '1', str(all_hosts[ip])], stdout=subprocess.PIPE).communicate()[0]

        # lock this section, until we get a complete chunk
        # then free it (so it doesn't write all over itself)
        with print_lock:
            if "Reply".upper() in output.decode('utf-8').upper():  # I do NOT believe this is the correct value to match on, but will work
                online.append(all_hosts[ip])
            elif "bytes from".upper() in output.decode('utf-8').upper():  # bytes from seems to be a good value in ubuntu.
                online.append(all_hosts[ip])
            elif "Destination host unreachable".upper() in output.decode('utf-8').upper():
                pass
            elif "Request timed out".upper() in output.decode('utf-8').upper():
                pass
            else:
                # print colors in green if online
                print("UNKNOWN", end='')


    # defines a new ping using def pingsweep for each thread
    # holds task until thread completes
    def threader():
        while True:
            worker = q.get()
            pingsweep(worker)
            q.task_done()


    q = Queue()

    # up to 100 threads, daemon for cleaner shutdown
    # just spawns the threads and makes them daemon mode
    for x in range(100):
        t = threading.Thread(target=threader)
        t.daemon = True
        t.start()

    # loops over the last octet in our network object
    # passing it to q.put (entering it into queue)
    for worker in range(len(all_hosts)):
        q.put(worker)

    # queue management
    q.join()

    for entry in online:
        print(entry)
# ok, give us a final time report
runtime = float("%0.2f" % (time.time() - startTime))
print("Run Time: ", runtime, "seconds")
done = input("Press enter when done:")
