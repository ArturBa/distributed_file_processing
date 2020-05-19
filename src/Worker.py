import queue
from multiprocessing.connection import Client, Listener
from os import getpid
import time

address = ('localhost' ,8080)
class Worker:
    def __init__(self, pid = None, qsize = 0, listener = None, client = None):
        self._conversion_files = queue.Queue(maxsize = qsize)
        self._max_qsize = qsize
        if listener is not None:
            self._client = client
        else:
            self._client = Client(address)
        if client is not None:
            self._listener = listener
        else:
            self._listener = Listener(address)
        if pid = None:
            self._pid = getpid()
        else:
            self._pid = pid

    def __eq__(self,other):
        return self._pid == other._pid

    def get_pid(self):
        return self._pid

    def get_qsize(self):
        return self._conversion_files.qsize()

    def get_free_qsize(self):
        return self._max_qsize - self._conversion_files.qsize()

    def set_free_qsize(self, free):
        self._free_qsize = free

    def get_join_msg(self):
        return {'type':'join_server',
                'id':self._pid,
                'qsize':self.get_qsize()}

    def parse_server_join_answer(self,msg):
        if msg['type'] == 'join' \
                and msg['pid'] == self.get_pid() \
                and msg['result'] == 'accepted':
            return True
        else:
            return False

    def get_free_space_msg(self):
        return {'type': 'free_space_answer',
                'pid': self.get_pid(),
                'free_space': self.get_free_qsize()}

    def parse_server_free_space_request(self,msg):
        if msg['type'] == 'free_space_request' \
                and msg['pid'] == self.get_pid():
            return True
        else:
            return False

    def send_free_space_answer(self, timeout):
        start_time = time.time()
        while time.time() < start_time + timeout:
            msg = self._listener.recv()
            if self.parse_server_free_space_request(msg):
                self._client.send(self.get_free_space_msg())
                break

    def connect_to_server(self, timeout=0):
        start_time = time.time()
        #self._client = Client(address)
        self._client.send(self.get_join_msg())
        while time.time() < start_time + timeout:
            msg = self._listener.recv()
            if self.parse_server_join_answer(msg):
                self._connected = True
                break
                

if __name__ == '__main__':
    worker = Worker()
    #worker.connect_to_server()
    #print(worker._pid)    
        
