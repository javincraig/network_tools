# The base of this code is derived from from
# https://rubysash.com/programming/python/python-3-multi-threaded-ping-sweep-scanner/


import time  # For timing the script
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

# List of IP addresses
address_list_raw = """192.168.0.0/24
192.168.1.0/24
192.168.2.0/24
192.168.3.0/24
192.168.4.0/24"""

# actual code start time
startTime = time.time()

try:  # the following commands only seem to work on windows
    info = subprocess.STARTUPINFO()
    info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    info.wShowWindow = subprocess.SW_HIDE
except Exception:  # this will continue the process for Linux
    pass

# Dictionaries for use later
online_dict = {}
offline_dict = {}

# Split the lines into individual networks and process each each network individually
for net_addr in address_list_raw.splitlines():
    # Creation of a dictionary entry for the network
    online_dict[net_addr] = []
    offline_dict[net_addr] = []
    # Creation of list for immediate use
    online = []
    offline = []
    # Create the network
    ip_net = ipaddress.ip_network(net_addr)

    # Get all hosts on that network
    all_hosts = list(ip_net.hosts())

    # Prints to the user what network is being scanned
    print('Sweeping Network with ICMP: ', net_addr)


    def pingsweep(ip):
        # for windows:   -n is ping count, -w is wait (ms)
        # for linux: -c is ping count, -w is wait (ms)
        # I didn't test subprocess in linux, but know the ping count must change if OS changes
        if os.name == 'nt':
            output = subprocess.Popen(['ping', '-n', '1', '-w', '1000', str(all_hosts[ip])],
                                      stdout=subprocess.PIPE, startupinfo=info).communicate()[0]
        elif os.name == 'posix':  # Linux needs work. Something isn't working correctly. 
            output = subprocess.Popen(['ping', '-c', '1', '-w', '10', str(all_hosts[ip])],
                                      stdout=subprocess.PIPE).communicate()[0]

        # lock this section, until we get a complete chunk
        # then free it (so it doesn't write all over itself)
        # upper used because of case issues
        with print_lock:
            if "Reply".upper() in output.decode('utf-8').upper():
                online.append(all_hosts[ip])
                online_dict[net_addr].append(all_hosts[ip])
            elif "bytes from".upper() in output.decode('utf-8').upper():
                online.append(all_hosts[ip])
                online_dict[net_addr].append(all_hosts[ip])
            elif "Destination host unreachable".upper() in output.decode('utf-8').upper():
                offline.append(all_hosts[ip])
                offline_dict[net_addr].append(all_hosts[ip])
                pass
            elif "Request timed out".upper() in output.decode('utf-8').upper():
                offline.append(all_hosts[ip])
                offline_dict[net_addr].append(all_hosts[ip])
                pass
            else:
                offline.append(all_hosts[ip])
                offline_dict[net_addr].append(all_hosts[ip])


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

    # prints each online entry
    for entry in online:
        print(entry)
# ok, give us a final time report
runtime = float("%0.2f" % (time.time() - startTime))
print("Run Time: ", runtime, "seconds")
print(online_dict)
done = input("Press enter when done:")
