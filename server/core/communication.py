from serial.serialutil import SerialException

class Comm(object):
    def __init__(self,comm,terminator='\0'):
        self.comm = comm
        self.terminator = terminator
        self.trys = 0
  
    def __enter__(self):
        try:
            self.comm.open()
        except SerialException:
            pass
        self.comm.setDTR(False)
        return self
  
    def __exit__(self, type, value, traceback):
        self.comm.close()
        
    def _checksum(self,st):
        s = 0
        for i in st:
            s += ord(i)
        s %= 256
        #return s.to_bytes(1,byteorder='little')
        return bytes([s])

    def send(self,msg):
        if self.trys > 8:
            return
        if not msg.startswith('T') and not msg.startswith('H'):
            msg = msg[:34].ljust(34)
        checksum = self._checksum(msg)
        tmp = msg.encode() + checksum # + self.terminator.encode()
        self.comm.write(tmp)
        resp = self.comm.readline().decode()[:-1]
        print("msg: ", end="")
        print(tmp)
        print("rsp: " + resp)
        if resp.startswith('FIN'):
            print('inv: ', end="")
            print(tmp)
        elif resp.startswith('ACK'):
            #print('msg sent')
            pass
        else: # RST or None
            self.trys += 1
            #print('Resending: "' + msg + '"')
            self.send(msg)