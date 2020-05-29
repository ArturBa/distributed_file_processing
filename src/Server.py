import subprocess
import sys
import os
import math
from UserCLI import *
from Worker import *
import time
import socket
import threading
import select

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
read_list = [client]

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
                break
         
    def checkIfWorkerAlreadyAdded(self, worker):
        for i in self.workerList:
            if i == worker:
                return True
        return False
        
    def checkWorkers(self, timeout=10):
        start = time.time()
        while time.time() < start+ timeout:
            readable, writable, errored = select.select(read_list, [], [])
            for s in readable:
                if s is client:
                    print("Checking workers")
                    _client, address = client.accept()
                    read_list.append(_client)
                    print("Connected to {} on address {}".format(_client, address))
                    #new_thread = threading.Thread(target = self.new_worker_connection, args = (_client, ))
                    #new_thread.daemon = True
                    #new_thread.start()
                else:
                    data = s.recv(1024)
                    if data:
                        msg = parse_raw_input(data)
                        if self.parseJoinMessage(msg):
                            worker = Worker(pid = msg['pid'], qsize = msg['qsize'])
                            if not self.checkIfWorkerAlreadyAdded(worker):
                                self.addNewWorker(worker)
                                print("succesfully added new worker")
                                msg = self.getJoinAcceptMsg(msg)
                                msg = parse_raw_output(msg)
                                print("sending join accept message")
                                s.send(msg)
                            elif self.parseFreeQSizeRequest(msg):
                                print("got queue size answer from worker")
                                return
                        else:
                            s.close()
                            read_list.remove(s)
                        
        return

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

    def manageFile (self):
        partsDuration = self.getPartsDuration()
        if server.splitFile(server.getPartsDuration()):
            print("File successfully splitted")
        else:
            print("Error while splitting file")
        files = self.manageSplitedFiles()
        messages = self.getConvertMsg(files)
        print(messages)
        return messages

    def getPartsDuration (self):
        fileName = os.path.basename(self.mainFile.location)
        result = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                                 "default=noprint_wrappers=1:nokey=1", fileName],
                                stdout = subprocess.PIPE,
                                stderr = subprocess.STDOUT)
        filmDuration = float(result.stdout)
        if len(self.workerList) > 0:
            numberOfParts = 0
            for worker in self.workerList:
                numberOfParts += worker._free_qsize
            if numberOfParts > 0:
                partDuration = math.ceil(filmDuration / numberOfParts)
                if partDuration > 10:
                    return partDuration
                else:
                    return 10
            else:
                return 0
        else:
            return 0

    def splitFile (self, partsDuration):
        cmd = ['python', 'videoSplit.py', '-f', self.mainFile.location, '-s', str(partsDuration)]
        p = subprocess.Popen(cmd, stderr=subprocess.STDOUT)
        while p.poll() is None:
            continue
        if p.poll() == 0:
            return True
        else:
            return False

    def manageSplitedFiles (self):
        fileName = os.path.basename(self.mainFile.location)
        fileNameBare = fileName.split('.')[0]
        filesNamesList = []
        if '\\' in self.mainFile.location or '/' in self.mainFile.location:
            allFilesList = os.listdir(os.path.dirname(self.mainFile.location))
        else:
            allFilesList = os.listdir(os.getcwd())
        for file in allFilesList:
            if fileNameBare in file and file != fileName:
                if '\\' in self.mainFile.location or '/' in self.mainFile.location:
                    filesNamesList.append(os.path.dirname(self.mainFile.location + '\\\\' + file))
                else:
                    filesNamesList.append(os.getcwd() + '\\' + file)
        return filesNamesList

    def getConvertMsg (self, filesNamesList):
        messages = []
        for file in filesNamesList:
            messages.append({'type': 'convert_file',
                             'pid': 0,
                             'path': file,
                             'format': self.mainFile.fileExtension,
                             'resolution': self.mainFile.resolution,
                             'saveLocation': self.mainFile.saveLocation})
        return messages


user = UserCLI()
user.setFileData()
server = Server(user.fileData)
server.checkWorkers(10)
print("Got control")
server.workerList[0].set_free_qsize(3)
for worker in server.workerList:
    print(worker._free_qsize)
print(server.getPartsDuration())
msg = server.manageFile()[0]
server.workerList[0].append_new_file(msg)
server.workerList[0].check_for_files_to_process()
#     sys.exit(-1)
# server.convertFile()
