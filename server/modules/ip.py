import socket # used for old getInternal
from urllib.request import urlopen
from urllib.error import URLError
import json
import subprocess
import re

class Addresses(object):
    def __init__(self,inits=('^','/')):
        self.inits = inits
        self.ips = {'internal' : '',
                    'external' : '' }
        self.update()

    def getExternal(self):
        url = 'http://api.hostip.info/get_json.php'
        try:
            info = json.loads(urlopen(url,timeout=15).read().decode('utf-8'))
        except URLError:
            return None
        return info['ip']
    
    def getInternal(self):
        tmp = subprocess.Popen(['/bin/ip','addr','show','up'],stdout=subprocess.PIPE)
        out = tmp.communicate()[0].decode('utf-8')
        p = re.compile('inet (\d+(?:\.\d+){3})')
        tmp = p.findall(out)
        for i in tmp:
            if not i.startswith('127'):
                return i
        return None

#    def getInternal2(self):
#        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#        try:
#            s.connect(("8.8.8.8",80))
#            ip = s.getsockname()[0]
#        except socket.error:
#            return None
#        finally:
#            s.close()
#        return ip
    
    def update(self,int=True,ext=True):
        self.ips = {'internal':'','external':''}
        internal = None
        external = None
        if ext:
            external = self.getExternal()
        if int:
            internal = self.getInternal()
        self.ips = {'internal' : internal,
                    'external' : external }

    def render(self):
        start = self.inits[0]
        out = ''
        for which in ('external','internal'):
            ip = self.ips[which]
            if ip is '':
                start = self.inits[1]
                err = 'no ' + which + ' ip'
                out += err.center(16)
            else:
                out += ip.center(16)
            out += '\n'
        return start + out[:33]

if __name__ == "__main__":
    a = Addresses()
    print(a.render())
