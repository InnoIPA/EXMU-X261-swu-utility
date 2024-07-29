# Copyright (c) 2023 Innodisk Crop.
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import os
import threading
import subprocess
import time
import json
import socket
import configparser
import ctypes
from ctypes import sizeof
from argparse import ArgumentParser
import importlib.resources as res

from paho.mqtt.client import Client as MQTTClient
from paho.mqtt.client import connack_string

import swu_utility.config as config


def on_connect(client, userdata, flags, rc):
    print(f"MQTT connection returned result: {connack_string(rc)}")
    client.subscribe(userdata.package_topic)
    client.subscribe(userdata.dna_get_topic)


def on_message(client, userdata, message):
    if message.topic == userdata.package_topic:
        payload = json.loads(message.payload)
        userdata.url = payload["url"]
        userdata.mode = payload["mode"]

        with userdata.cv:
            userdata.cv.notify()
    elif message.topic == userdata.dna_get_topic:
        client.publish(userdata.dna_post_topic, payload=userdata.dna)
    else:
        print(
            (
                f"Received message '{message.payload}' on topic '{message.topic}' "
                f"with Qos {message.qos}"
            )
        )


def get_dna():
    with open("/sys/firmware/devicetree/base/__symbols__/AXI_DNA_0", "r") as f:
        base_addr = f.read().split("@")[1].rstrip("\x00")

    dna = ""
    i = 0
    while i < 3:
        addr = int(base_addr, 16) + i * 4
        dna += (
            subprocess.check_output(["devmem", f"0x{addr:x}"], text=True)
            .rstrip()[2:]
            .lower()
        )

        i += 1

    return dna


def get_mac():
    macs = subprocess.Popen('cat /sys/class/net/e*/address', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    mac,err = macs.communicate()
    return mac.rstrip()[0:17].decode('utf-8')


def get_swupdate_args(url, mode):
    # https://sbabic.github.io/swupdate/2022.05/swupdate.html#command-line-parameters
    def selection(e):
        return ("-e", e)

    def hw_info():
        return ("-H", "EXMU-X261:revA")

    def remote_url(url):
        return ("-d", f"-u {url}")

    def local_image(path):
        return ("-i", path)

    def verbose():
        return "-v"

    def log_level(l):
        return ("-l", l)

    args = ["swupdate"]

    if mode == "AB":
        root_part = subprocess.check_output(
            ["findmnt", "-no", "SOURCE", "/"], text=True
        )
        root_part = root_part.strip()
        # root_part = "/dev/mmcblk1p2"
        if root_part == "/dev/mmcblk0p2":
            args.extend(selection("EXMU-X261,alt"))
        elif root_part == "/dev/mmcblk1p2":
            args.extend(selection("EXMU-X261,main"))

    args.extend(remote_url(url))
    args.extend(hw_info())
    args.extend(log_level("4"))

    return args


def try_connect_to_swupdate(addr, limit=5):
    # https://github.com/sbabic/swupdate/blob/2022.05/ipc/progress_ipc.c
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    while limit > 0:
        try:
            s.connect(addr)
        except FileNotFoundError:
            limit -= 1
            time.sleep(0.1)
        else:
            return s

    s.close()
    return None


# Keep sending telemetry data to mqtt broker until `s` is closed
def collect_and_send_telemetry(client, s, topic):
    p_msg = progress_msg()
    while True:
        msg, err = s.recvfrom(sizeof(p_msg))
        if len(msg) == 0:  # socket is closed
            break

        ctypes.memmove(ctypes.byref(p_msg), msg, sizeof(p_msg))
        client.publish(topic, payload=p_msg.to_json())


# application data
class Data:
    def __init__(self, dna):
        self.cv = threading.Condition()
        self.url = ""
        self.mode = ""
        self.is_updating = False

        self.dna = dna
        self.dna_get_topic = f"v0/EXMU-X261/ota/dna/get"
        self.dna_post_topic = f"v0/EXMU-X261/ota/dna/post"
        self.package_topic = f"v0/EXMU-X261/ota/package/{self.dna}"
        self.telemetry_topic = f"v0/EXMU-X261/ota/telemetry/{self.dna}"


# This struct is defined in here.
# https://github.com/sbabic/swupdate/blob/d542b7fa7c8b7ddb75e7cb3335f5a2590df2edab/include/progress_ipc.h#L22-L39
class progress_msg(ctypes.Structure):
    _fields_ = [
        ("magic", ctypes.c_uint),  #  Magic Number
        (
            "status",
            ctypes.c_uint,
        ),  # (RECOVERY_STATUS)  Update Status (Running, Failure)
        ("dwl_percent", ctypes.c_uint),  #  % downloaded data
        ("dwl_bytes", ctypes.c_ulonglong),  #  total of bytes to be downloaded
        ("nsteps", ctypes.c_uint),  #  No. total of steps
        ("cur_step", ctypes.c_uint),  #  Current step index
        ("cur_percent", ctypes.c_uint),  #  % in current step
        ("cur_image", ctypes.c_char * 256),  #  Name of image to be installed
        ("hnd_name", ctypes.c_char * 64),  #  Name of running handler
        (
            "sourcetype",
            ctypes.c_int,
        ),  # (sourcetype)  Interface that triggered the update
        ("infolen", ctypes.c_uint),  #  Len of data valid in info
        ("info", ctypes.c_char * 2048),  #  additional information about install
    ]

    def to_json(self):
        ret = {}
        ret["magic"] = self.magic
        ret["status"] = self.status
        ret["dwl_percent"] = self.dwl_percent
        ret["dwl_bytes"] = self.dwl_bytes
        ret["nsteps"] = self.nsteps
        ret["cur_step"] = self.cur_step
        ret["cur_percent"] = self.cur_percent
        ret["cur_image"] = self.cur_image.decode("utf-8")
        ret["hnd_name"] = self.hnd_name.decode("utf-8")
        ret["sourcetype"] = self.sourcetype

        return json.dumps(ret)


def main():
    # Initialization
    parser = ArgumentParser()
    parser.add_argument("-f", "--file", help="path to config file", dest="config")
    args = parser.parse_args()

    if args.config:
        config_file = open(args.config)
    else:
        config_file = res.open_text(config, "config.ini")

    with config_file as c:
        opt = configparser.ConfigParser()
        opt.read_file(c)
        broker_host = opt["broker"]["host"]
        broker_port = opt["broker"].getint("port")

    platfrom = subprocess.check_output(["uname", "-p"]).rstrip()
    if platfrom == b'aarch64':
        dna = get_dna()
    elif platfrom == b'x86_64':
        dna = get_mac()
    else:
        print(f"Invalid platform: {platfrom}")
        exit()

    print(f"Device DNA: {dna}")

    # application data
    # This object is shared between main thread and mqtt thread
    userdata = Data(dna)

    # Connect to mqtt broker
    client = MQTTClient(userdata=userdata)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect_async(broker_host, broker_port)
    client.loop_start()  # spawn mqtt thread

    with userdata.cv:
        userdata.cv.wait()  # Wait for an update
        # an update is available

    # Run swupdate
    args = get_swupdate_args(userdata.url, userdata.mode)

    env = os.environ.copy()
    env.update({"LUA_PATH": "/opt/innodisk/swu-client/swupdate_handlers.lua"})
    swupdate = subprocess.Popen(args, env=env)

    s = try_connect_to_swupdate("/tmp/swupdateprog")

    if s:
        collect_and_send_telemetry(client, s, userdata.telemetry_topic)
        s.close()

    # Wait for swupdate to update the system
    swupdate.wait()

    client.disconnect()

    if swupdate.returncode == 0:
        subprocess.run(["reboot"])


if __name__ == "__main__":
    main()
