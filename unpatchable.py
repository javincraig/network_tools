from scrapli.driver.core import IOSXEDriver
from getpass import getpass

# ---------------Gather information---------------------
# credentials gathering
username = input('Username: ')
password = getpass(prompt='Password: ', stream=None)


device_list_raw = """192.168.0.5"""

def show_uptime():
    show_ver_uptime = conn.send_command("show version | inc uptime")
    return show_ver_uptime.result


def interface_info():
    show_interface = conn.send_command("show interface | inc line protocol | Last | Description")
    return show_interface.result


for device in device_list_raw.splitlines():
    my_device = {
        "host": device,
        "auth_username": username,
        "auth_password": password,
        "auth_strict_key": False,
        "transport_options": {"open_cmd": ["-o", "KexAlgorithms=+diffie-hellman-group1-sha1", "-o", "Ciphers=+aes256-cbc"]},
    }

    conn = IOSXEDriver(**my_device)
    conn.open()

    show_uptime_raw = show_uptime()
    interface_info_raw = interface_info()
    interface_dict = {}
    for line in interface_info_raw.splitlines():
        if line[0] != " ":
            current_interface = line.split()[0]
            interface_dict[current_interface] = {}
            interface_dict[current_interface]["description"] = ""
            interface_dict[current_interface]["last_input"] = ""
            interface_dict[current_interface]["last_clearing"] = ""
            if "line protocol is up" in line:
                connected = True
            else:
                connected = False
            interface_dict[current_interface]["connected"] = connected
        if "Last input" in line:
            interface_dict[current_interface]["last_input"] = line
        if "Description:" in line:
            interface_dict[current_interface]["description"] = line
        if "Last clearing" in line:
            interface_dict[current_interface]["last_clearing"] = line
    print(show_uptime_raw)
    for interface in interface_dict:
        if interface_dict[interface]["connected"] == False:
            print(f"{interface} is not connected")
            if interface_dict[interface]["last_input"] != "":
                print(interface_dict[interface]["last_input"])
            if interface_dict[interface]["description"] != "":
                print(interface_dict[interface]["description"])
            if interface_dict[interface]["last_clearing"] != "":
                print(interface_dict[interface]["last_clearing"])
            print('')
