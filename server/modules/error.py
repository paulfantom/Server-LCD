from time import strftime

class Error(object):
    def __init__(self,msg,start='~'):
        self.data = msg
        self.start = start

    def update(self):
        pass

    def render(self):
        dow = ('Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat')
        date = dow(int(strftime('%w'))) + '  ' + strftime('%m.%d %H:%M')
        return self.start + date + '\n' + str(self.data)[:16].center(16)
