#!/usr/bin/env python3
#
# Implement part of the Sony Camera Remote API in a scriptable way.
#
# Copyright (C) 2015 Julien Desfossez
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA  02110-1301, USA.

import cv2
from urllib.request import urlopen, Request
import numpy as np
import json


class SonyControl:
    def __init__(self):
        self.url = 'http://192.168.122.1:8080/sony/camera'
        self.id = 1

    def send_rq(self, data):
        req = Request(self.url)
        req.add_header('Content-Type', 'application/json')
        data["id"] = self.id
        self.id += 1
        response = urlopen(req, bytes(json.dumps(data), encoding='utf8'))
        r = json.load(response)
        return r

    def send_basic_cmd(self, cmd, params=[]):
        data = {"method": cmd,
                "params": params,
                "version": "1.0"}
        return self.send_rq(data)

    def liveview(self):
        stream = urlopen(self.live)
        img_bytes = b''
        while True:
            img_bytes += stream.read(1024)
            a = img_bytes.find(b'\xff\xd8')
            b = img_bytes.find(b'\xff\xd9')
            if a != -1 and b != -1:
                jpg = img_bytes[a:b+2]
                img_bytes = img_bytes[b+2:]
                i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),
                                 cv2.IMREAD_COLOR)
                cv2.imshow('i', i)
                if cv2.waitKey(1) == 27:
                    exit(0)

    def getVersions(self):
        r = self.send_basic_cmd("getVersions")
        print("Version %s" % r["result"][0][0])

    def startRecMode(self):
        r = self.send_basic_cmd("startRecMode")
        if r["result"][0] == 0:
            print("Rec mode started")

    def stopRecMode(self):
        r = self.send_basic_cmd("stopRecMode")
        if r["result"][0] == 0:
            print("Rec mode stopped")

    def getEvent(self):
        r = self.send_basic_cmd("getEvent", params=[True])
        for i in r["result"]:
            print(i)
            if i == "isoSpeedRateCandidates":
                print("LA")
        print("isoSpeedRateCandidates : %s" % (r["result"][0]))

    def startLiveview(self):
        r = self.send_basic_cmd("startLiveview")
        self.live = r["result"][0]
        self.liveview()

if __name__ == "__main__":
    s = SonyControl()
    s.stopRecMode()
    s.getVersions()
    s.startRecMode()
#    s.getEvent()
    s.startLiveview()
