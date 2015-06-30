from serial import Serial
import time
from core.daemon import Daemon
from core.communication import Comm

from calendar import timegm

class Feeder(Daemon):
    def __init__(self,host='localhost',serial='/dev/ttyUSB0',interval=60,terminator='\0',**kw):
        super().__init__(**kw)
        self.terminator = terminator
        self.interval = interval
        self.allModules = []
        self.messages = []
        #TODO autodetect serial port
        self.comm = Serial(serial,9600,timeout=5)

        try:
            from modules.services import Services
            self.allModules.append(Services(username='guest',
                                            password='N5BY3VhZPFh7qp8uS7fc',
                                            https=False))
        except ImportError: pass
        try:
            from modules.stats import Stats
            self.allModules.append(Stats())
        except ImportError: pass
        try:
            from modules.temperatures import Temperatures
            self.allModules.append(Temperatures())
        except ImportError: pass
        try:
            from modules.ip import Addresses
            self.allModules.append(Addresses())
        except ImportError: pass
        try:
            from modules.mpd import MPD
            self.allModules.append(MPD(host))
        except ImportError: pass
        try:
            from modules.torrent import Torrents
            self.allModules.append(Torrents(host,8112))
        except ImportError: pass

    def update(self):
        for mod in self.allModules:
            try:
                mod.update()
                out = mod.render()
                if isinstance(out,str):
                    self.messages.append(mod.render())
                #elif isinstance(out,bytes):
                #    self.messages.append(mod.render())
                elif isinstance(out,list):
                    self.messages = self.messages + out
            except AttributeError:
                print('No module: "' + str(mod))

    def _syncTime(self):
        timestamp = timegm(time.localtime())
        with Comm(self.comm) as c:
            c.send('T' + str(timestamp))

    def sendAll(self):
        with Comm(self.comm) as c:
            for msg in self.messages:
                c.send(msg)
                time.sleep(1)
            self.messages = []

    def stop(self):
        try:
            # Send error (HALT)
            self.comm.write('H'.encode())
        finally:
            super().stop()

    def run(self):
        self._syncTime()
        while True:
            curr = time.localtime()
            if (curr.tm_hour == 0) and \
               (0 <= curr.tm_min < self.interval + 1):
                self._syncTime()
            self.update()
            self.sendAll()
            time.sleep(self.interval)
