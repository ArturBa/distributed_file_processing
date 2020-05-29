import subprocess
import sys
from converter import Converter
from UserCLI import *
from Worker import *
import time
import socket
import threading

client = socket.socket()
host = '127.0.0.1'
port = 8080
ThreadCount = 0
try:
    client.bind((host, port))
except socket.error as e:
    print(str(e))

print('Waitiing for a Connection..')
client.listen(5)

def parse_raw_input(msg):
	'''De-serializing raw socket message to python object format'''
	return pickle.loads(msg)
    
def parse_raw_output(msg):
	'''Serializing python object to raw socket message'''
	return pickle.dumps(msg)
	
class Server:
    def __init__ (self, mainFile, toConvertFiles = None, workerList = [], fileData = None):
        self.mainFile = mainFile
        self.toConvertFiles = toConvertFiles
        self.workerList = workerList
        self.fileData = fileData

    #def connect(self):
        #try:
            #client.accept()
        #except socket.error as e:
            #print(str(e))
            
    def addNewWorker(self, worker = None):
        if worker is not None:
            if not self.checkIfWorkerAlreadyAdded(worker):
                self.workerList.append(worker)
                
    def new_worker_connection(self, connection):
        while True:
            msg = connection.recv(1024)
            msg = parse_raw_input(msg)
            print(msg)
            if self.parseJoinMessage(msg):
                worker = Worker(pid = msg['pid'], qsize = msg['qsize'])
                if not self.checkIfWorkerAlreadyAdded(worker):
                    self.addNewWorker(worker)
                    print("succesfully added new worker")
                    msg = self.getJoinAcceptMsg(msg)
                    msg = parse_raw_output(msg)
                    print("sending join accept message")
                    connection.send(msg)
                    #msg = self.getWorkerQSizeRequest(worker)
                    #msg = parse_raw_output(msg)
                    #connection.send(msg)
                    #print("sending worker queue size message")
            elif self.parseFreeQSizeRequest(msg):
                print("got queue size answer from worker")
         
    def checkIfWorkerAlreadyAdded(self, worker):
        for i in self.workerList:
            if i == worker:
                return True
        return False
        
    def checkWorkers(self):
        while True:
            print("Checking workers")
            _client, address = client.accept()
            print("Connected to {} on address {}".format(_client, address))
            new_thread = threading.Thread(target = self.new_worker_connection, args = (_client, ))
            new_thread.daemon = True
            new_thread.start()

    def parseJoinMessage(self,msg):
        return msg['type'] == 'join'

    def getJoinAcceptMsg(self, worker_request):
        return {'type':'join',
                'pid': worker_request['pid'],
                'result':'accepted'}
    
    def getWorkerQSizeRequest(self, worker):
        return {'type': 'free_space_request',
                'pid': worker.get_pid()}

    def sendFreeQSizeRequest(self):
        for worker in self.workerList:
            msg = self.getWorkerQSizeRequest(worker)
            self._client.send()

    def parseFreeQSizeRequest(self, msg):
        if msg['type'] == 'free_space_answer':
            for worker in self.workerList:
                if msg['pid'] == worker.get_pid():
                    worker.set_free_qsize(msg['free_space'])
                    return True
        else:
            return False

    def getFreeSize(self, timeout=0):
        start_time = time.time()
        workers_served = 0
        while time.time() < start_time + timeout or workers_served > len(self.workerList):
            msg = client.recv(1024)
            if self.parseFreeQsizeRequest:
                workers_served += 1
        #return len(any[(worker._free_qsize > 0) for worker in self.workerList])
        return 1

    def splitFile (self):
        cmd = ['python', 'videoSplit.py', '-f', self.mainFile.location, '-s', '10', '-v', 'h264']
        p = subprocess.Popen(cmd, stderr=subprocess.STDOUT)
        while p.poll() is None:
            continue
        if p.poll() == 0:
            return True
        else:
            return False

    def convertFile (self):
        fileName = os.path.basename(self.mainFile.location).split('.')[0]
        conv = Converter(ffmpeg_path="/usr/bin/ffmpeg",
                         ffprobe_path="/usr/bin/ffprobe")
        convert = conv.convert(self.mainFile.location, self.mainFile.saveLocation + '\\' + fileName + "_converted video." + self.mainFile.fileExtension, {
            'format': self.mainFile.fileExtension,
            'audio': {
                'codec': 'aac',
                'samplerate': 11025,
                'channels': 2
            },
            'video': {
                'codec': 'h264',
                'width': self.mainFile.resolution[0],
                'height': self.mainFile.resolution[1],
                'fps': 25
            }})
        print("File conversion started")
        for timecode in convert:
            print(f'\rConverting ({timecode:.2f}) ...')

user = UserCLI()
user.setFileData()
server = Server(user.fileData)
listener_thread = threading.Thread(server.checkWorkers())
listener_thread.daemon = True
listener_thread.start()
server.new_worker_connection(client)
print("Got control")
if server.splitFile():
    print("File successfully splitted")
else:
    print("Error while splitting file")
    sys.exit(-1)
server.convertFile()
