import os

class Stats(object):
    load = ()
    uptime = 0

    def __init__(self,start='#'):
        self.start = start
        self.update()

    def _parseUptime(self,seconds):
        days = int(seconds/86400)
        seconds -= days*86400
        hours = int(seconds/3600)
        seconds -= hours*3600
        minutes = int(seconds/60)
        seconds -= minutes*60
        seconds = int(seconds)
        return (days,hours,minutes,seconds)

    def getUptime(self):
        f = open('/proc/uptime', 'r')
        up = float(f.readline().split()[0])
        f.close()
        return self._parseUptime(up)

    def getLoad(self):
        return os.getloadavg()

    def update(self):
        self.load = self.getLoad()
        self.uptime = self.getUptime()

    def render(self):
        out = ''
        for i in self.load:
            temp = "%.1f" % i
            out += temp.rjust(4)
            out += '  '

        uptime = str(self.uptime[0]) + 'd ' +\
                 str(self.uptime[1]) + 'h ' +\
                 str(self.uptime[2]) + 'min'# +\
                 #str(self.uptime[3]) + 's'

        return self.start + out[:16] + '\n' + uptime.center(16)

if __name__ == "__main__":
    s = Stats()
    print(s.render())
