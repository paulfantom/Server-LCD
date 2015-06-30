import socket
import re

class MPD(object):
    def __init__(self,host='localhost',port=6600,start='&'):
        self.host = host
        self.port = port
        self.start = '&'
        self.data = None

    def update(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        res = s.recv(1024).decode()
        if not res.startswith('OK MPD'):
            s.close()
            self.data = {'status' : None}
            return

        s.send('status\n'.encode('utf8'))
        res = s.recv(1024).decode()
        pattern = re.compile('state: ([a-z]+)')
        status = pattern.search(res).group()[7:]
        ret = {'status' : status,
               'artist' : None,
               'title'  : None }
        if status != 'play' and status != 'pause':
            self.data = ret
            return

        s.send('currentsong\n'.encode('utf8'))
        res = s.recv(1024).decode()
        pattern = re.compile('Title: (.*?)\n')
        ret['title'] = pattern.search(res).group()[7:-1]
        pattern = re.compile('Artist: (.*?)\n')
        ret['artist'] = pattern.search(res).group()[8:-1]
        s.close()
        self.data = ret
        return
      
    def render(self):
        if self.data['status'] is None:
            return self.start + \
                   'no connection'.center(16) + \
                   '\n' + \
                   'to MPD'.center(16)
        elif self.data['artist'] is None:
            return self.start + \
                   'playback'.center(16) + \
                   '\n' + \
                   'STOPPED'.center(16)
        else:
            artist = self.data['artist'][:16].center(16)
            title  = self.data['title'][:16].center(16)
            return self.start + artist + '\n' + title

if __name__ == '__main__':
    client = MPD('192.168.10.2')
    client.update()
    print(client.data)
    print(client.render())
