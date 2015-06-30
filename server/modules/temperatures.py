import sensors
import socket
import time

class Temperatures(object):
    aliases = { 'temp1' : 'SYS: ',
                'temp2' : 'CPU: ',
                'temp3' : 'CASE:',
                'sdc'   : 'HDDC:'}
    order = ('SYS: ','CPU: ','CASE:','HDDC:')

    def __init__(self,inits=('$','%'),aliases=None,order=None):
        self.inits = inits
        sensors.init()
        self.readings = {}
        self.prev_readings = {}
        if aliases is not None:
            self.aliases = aliases
        self.update()

    def __exit__(self):
        self.cleanup()

    def cleanup(self):
        sensors.cleanup()
    
    def updateLmSensors(self):
        for chip in sensors.iter_detected_chips():
            if chip.prefix == b'w83627dhg':
                for f in chip:
                    if f.label.startswith('temp'): 
                        #    print(f.label)
                        self.readings[self.aliases[f.label]] = f.get_value()

    def _fetchDisk(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('localhost',7634))
        data = s.recv(4096)
        s.close()
        return data.decode('utf-8')

    def _parseDisk(self,data):
        parts = data.split('|')
        if len(parts) < 4:
            # err?
            #data = self._fetchDisk()
            #time.sleep(100)
            #return _parseDisk(data)
            return None
            
        i = 1
        ret = {}
        while i < len(parts)-1:
            #try: 
            ret[parts[i].split('/dev/')[1]] = int(parts[i+2])
            #except ValueError:
            #    ret[parts[i].split('/dev/')[1]] = -99

            i = i + 5
        return ret
        
    def updateDiskData(self):
        disks = []
        for key in self.aliases.keys():
            if key.startswith('sd') and len(key) == 3:
                disks.append(key)

        disks.sort()
        
        if len(disks) == 0: 
            disks.append('sda')
            self.aliases['sda'] = 'HDDA:'
        
        for disk in disks:
            try:
                val = self._parseDisk(self._fetchDisk())[disk]
            except (KeyError, TypeError):
                try:
                    val = self.prev_readings[self.aliases[disk]]
                except KeyError:
                    val = 'n/disk'
            except ConnectionRefusedError:
                val = 'n/disk'

            self.readings[self.aliases[disk]] = val

    def update(self):
        self.prev_readings = dict(self.readings)
        self.updateLmSensors()
        self.updateDiskData()
        self.data = self.get()

    def get(self):
        ret = []
        trend = '--'
        # sort readings
        for key in self.order:
            try:
                if self.readings[key] > self.prev_readings[key]:
                    trend = "/\\"
                elif self.readings[key] < self.prev_readings[key]:
                    trend = "\\/"
                else:
                    trend = '--'
            except KeyError:
                trend = '--'
            #ret.append((self.aliases[key],self.readings[self.aliases[key]]))
            try:
                ret.append((key,self.readings[key],trend))
            except KeyError:
                ret.append((key,'n/sensor',trend))
        return ret

    def render(self):
        out = ''
        for line in self.data:
            out += line[0][:7].ljust(8)
            try:
                out += str(float(line[1])).rjust(5)
                out += ' ' + line[2]
            except ValueError:
                out += str(line[1]).rjust(8)
            out += '\n'
            
        return [self.inits[0]+out[:33],self.inits[1]+out[34:67]]

if __name__ == "__main__":
    t = Temperatures()
    print(t.render())

