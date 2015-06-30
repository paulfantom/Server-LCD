from time import strftime
try:
    from modules.monit import Monit
except ImportError:
    from monit import Monit
import requests.exceptions

class Services(object):
    def __init__(self,inits=('@','!'),**kw):
        self.kw = kw
        self.inits = inits
        self._connect()
        self.failed = ["no MONIT daemon!"]

    def _connect(self):
        try:
            self.instance = Monit(**self.kw)
            self.rebuild()
        except requests.exceptions.ConnectionError:
            self.instance = None

    def update(self):
        try:
            self.instance.update()
            self.check()
        except AttributeError:
            self._connect()

    def rebuild(self):
        srv = []
        for key in self.instance.keys():
            if self.instance[key].type == 'process':
                srv.append(key)
        self.monitored = srv

    def check(self):
        failed = []
        for proc in self.monitored:
            if not self.instance[proc].running:
                failed.append(proc)
        self.failed = failed

    def render(self):
        start = self.inits[0]
        out = strftime('%H:%M')
        if len(self.failed) == 0:
            out += 'OK'.rjust(11)
            out += '\n'
            out += 'services running'
        else:
            start = self.inits[1]
            out += 'SERVICE'.rjust(11)
            out += '\n'
            out += self.failed[0][:16].center(16)
        return start + out

if __name__ == "__main__":
    m = Services(username='guest',password='N5BY3VhZPFh7qp8uS7fc',https=False)
    #print(m.monitored)
    #m.check()
    #print(m.failed)
    print(m.render())
