import queue
import socket, pickle
from os import getpid
import time
import threading

lock = threading.Lock()

host = '127.0.0.1'
port = 8080
client = socket.socket()
try:
    client.connect((host, port))
except socket.error as e:
    print(str(e))
    
def parse_raw_input(msg):
	'''De-serializing raw socket message to python object format'''
	return pickle.loads(msg)
	
def parse_raw_output(msg):
	'''Serializing python object to raw socket message'''
	return pickle.dumps(msg)

class Worker:
    def __init__(self, pid = None, qsize = 0, listener = None, client = None):
        self._conversion_files = queue.Queue(maxsize = qsize)
        self._max_qsize = qsize
        if pid is None:
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
        return {'type':'join',
                'pid':self._pid,
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

    def connect_to_server(self):
    	msg = self.get_join_msg()
    	msg = parse_raw_output(msg)
    	client.send(msg)
        
    def listen(self):
    	while True:
            try:
                msg = client.recv(1024)
                msg = parse_raw_input(msg)
                if self.parse_server_join_answer(msg):
                    self._connected = True
                    print("Connection from server established")
                    msg = self.get_free_space_msg()
                    msg = parse_raw_output(msg)
                    client.send(msg)
                    print("Free space free_space_request received and answer sent")
                elif self.parse_file_data(msg):
                    self.append_new_file(msg)
                else:
                    print("No response from server")
            except EOFError as e:
                continue
            
    def append_new_file(self, msg):
    	try:
    		lock.acquire()
    		self._conversion_files.put(msg['filedata'])
    		lock.release()
    	except Exception as e:
    		print(e)
    	finally:
    		lock.release()
    		
    def check_for_files_to_process(self,msg):
    	while True:
    		try:
    			if not self._confersion_files.empty():
    				lock.acquire()
    				fileData = self._conversion_files.get()
    				lock.release()
    				thread = threading.Thread(target = self.process_new_file, args = (fileData))
    		except Exception as e:
    			print(e)
    		finally:
    			lock.release()

if __name__ == '__main__':
    worker = Worker()
    time.sleep(5)
    worker.connect_to_server()
    listener_thread = threading.Thread(target = worker.listen())
    listener_thread.daemon= True
    listener_thread.start()  
        
