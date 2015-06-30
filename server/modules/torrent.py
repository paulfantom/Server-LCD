import transmissionrpc
from operator import itemgetter
from unicodedata import normalize

class Torrents(object):
    def __init__(self,host='localhost',port='9091',inits=('*','?')):
        self.inits = inits
        self.tc = transmissionrpc.Client(host,port=port)
        self.update()

    def _norm(self,st):
        return normalize('NFKD',st).encode('ascii','ignore').decode()

    def _getTorrentInfo(self,torrent_id):
        t = self.tc.get_torrent(torrent_id)
        return {'percent'  : int(t.percentDone*100),
                'name'     : self._norm(t.name),
                'status'   : t.status,
                'position' : t.id}

    def getAllTorrents(self):
        all = []
        i = 1
        while True:
            try:
                all.append(self._getTorrentInfo(i))
            except KeyError:
                break
            i = i + 1
        overall = len(all)
        for pos in range(overall):
            all[pos]['position'] = str(all[pos]['position']) + '/' + str(overall)
        return all

    def update(self):
        self.data = sorted(self.getAllTorrents(), 
                           key=itemgetter('percent'), 
                           reverse=True)[:len(self.inits)]

    def render(self):
        screens = []
        for i in range(len(self.inits)):
            try:
                title = self.data[i]['name'][:16].center(16)
                pos   = self.data[i]['position']
                progress = str(self.data[i]['percent']) + '%'
                out = title + '\n'
                if (len(pos) + len(progress)) > 15:
                    screens.append(self.inits[i] + out + progress.center(16))
                else:
                    screens.append(self.inits[i] + out + pos + progress.rjust(16-len(pos)))
            except IndexError:
                if i == 0:
                    return [self.inits[0] + \
                            'No torrents'.center(16) +\
                            'added to queue'.center(16)]
                else:
                    screens.append(self.inits[i]+'--'.center(16)+'\n'+'--'.center(16))
        return screens


if __name__ == '__main__':
    t = Torrents('192.168.10.2',8112)
    print(t.data)
    print(t.render())
