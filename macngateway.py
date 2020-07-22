from scrapli.driver.core import IOSXEDriver
from getpass import getpass

# ---------------Gather information---------------------
# credentials gathering
username = input('Username: ')
password = getpass(prompt='Password: ', stream=None)


device_list_raw = """192.168.0.5"""


def show_macaddress():
    show_mac_raw = conn.send_command("show mac-address table")
    return show_mac_raw.result


def show_gateway():
    show_ip_route_raw = conn.send_command("show ip route")
    if "Default gateway is not set" in show_ip_route_raw.result:
        show_default_route_raw = conn.send_command("show run | include ip route 0.0.0.0 0.0.0.0")
        default_gateway = show_default_route_raw.result.strip("ip route 0.0.0.0 0.0.0.0 ")
    else:
        show_default_gateway_raw = conn.send_command("show run | include ip default-gateway")
        if "ip default-gateway" in show_default_gateway_raw.result:
            default_gateway = show_default_gateway_raw.result.strip("ip default-gateway ")
        else:
            default_gateway = input("Please enter the layer 3 device")
    print(default_gateway)


for device in device_list_raw.splitlines():
    my_device = {
        "host": device,
        "auth_username": username,
        "auth_password": password,
        "auth_strict_key": False,
        "transport": "paramiko",
    }

    conn = IOSXEDriver(**my_device)
    conn.open()

    show_gateway()
#except ScrapliAuthenticationFailed:
#    print("Authentication Failed")
