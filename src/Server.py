import math
import subprocess
import sys
import datetime
import shutil

from UserCLI import *
from Worker import *

client = socket.socket()
host = '127.0.0.1'
port = 8080
try:
    client.bind((host, port))
except socket.error as e:
    print(str(e))

print('Waiting for a Connection..')
client.listen(5)

def parse_raw_input(msg):
    """De-serializing raw socket message to python object format"""
    return pickle.loads(msg)


def parse_raw_output(msg):
    """Serializing python object to raw socket message"""
    return pickle.dumps(msg)


class Server:
    def __init__(self, mainFile, toConvertFiles=None, workerList=[], fileData=None):
        self.mainFile = mainFile
        self.toConvertFiles = queue.Queue(maxsize = 100)
        self.workerList = workerList
        self.fileData = fileData

    def addNewWorker(self, worker=None):
        if worker is not None:
            if not self.checkIfWorkerAlreadyAdded(worker):
                self.workerList.append(worker)

    def new_worker_connection(self, connection):
        #TODO: add breaks and exceptions
        # receive new connection
        while True:
            msg = connection.recv(1024)
            msg = parse_raw_input(msg)
            if self.parseJoinMessage(msg):
                worker = Worker(pid=msg['pid'], qsize=msg['qsize'])
                if not self.checkIfWorkerAlreadyAdded(worker):
                    self.addNewWorker(worker)
                    print("successfully added new worker")
                    msg = self.getJoinAcceptMsg(msg)
                    msg = parse_raw_output(msg)
                    print("sending join accept message")
                    connection.send(msg)
        # request update from workers
        while True:
            self.parseFreeQSizeRequest(msg)
            # get msg from a worker
            msg = connection.recv(1024)
            worker.set_free_qsize(msg['free_space'])
            print("got queue size answer from worker")

            found = self.checkForFilesToSend(worker)
            if found:
                print("Found splitted file to send")
                msg = self.getConvFileToSend(found, worker)
                msg = parse_raw_output(msg)
                connection.send(msg)

            # Check if are converted files
            self.parseConvFileMsg(msg)
            print("Got converted file from {}", msg['pid'])
            connection.send(msg)
            msg = connection.receive(1024)
            if msg['converted']
                self.addConverted(msg)
                if self.concatenateConvertedFiles(msg):
                    os.exit(0)

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
            new_thread = threading.Thread(target=self.new_worker_connection, args=(_client,))
            new_thread.start()

    def parseJoinMessage(self, msg):
        return msg['type'] == 'join'

    def getJoinAcceptMsg(self, worker_request):
        return {'type': 'join',
                'pid': worker_request['pid'],
                'result': 'accepted'}

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
        
    def parseConvFileMsg(self, msg):
        return msg['type'] == 'convert_file'

    def manageFile(self):
        dirName = '{}_conversion_{}'.format(os.path.basename(self.mainFile.location).split('.')[0], datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        dirName = dirName.replace(':', '_')
        dirName = dirName.replace('/', '_')
        if os.name == 'nt':
            os.mkdir('.\\' + dirName)
            shutil.copy(self.mainFile.location, "{}\\{}".format(dirName, os.path.basename(self.mainFile.location)))
            self.mainFile.location = os.getcwd() + '\\' + dirName + '\\' + os.path.basename(self.mainFile.location)
        else:
            os.mkdir('./' + dirName)
            shutil.copy(self.mainFile.location, "{}/{}".format(dirName, os.path.basename(self.mainFile.location)))
            self.mainFile.location = os.getcwd() + '/' + dirName + '/' + os.path.basename(self.mainFile.location)
        if self.splitFile(self.getPartsDuration()):
            print("File successfully splitted")
        else:
            print("Error while splitting file")
        files = self.manageSplitedFiles()
        messages = self.getConvertMsg(files)
        print(messages)
        for message in messages:
            self.toConvertFiles.put(message)

    def getPartsDuration(self):
        fileName = os.path.basename(self.mainFile.location)
        try:
            result = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                                     "default=noprint_wrappers=1:nokey=1", fileName],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
            filmDuration = float(result.stdout)
        except Exception:
            print("Error while obtaining the duration of your file.")
            sys.exit(-1)
        if len(self.workerList) > 0:
            numberOfParts = 0
            for worker in self.workerList:
                numberOfParts += worker.get_free_qsize()
            if numberOfParts > 0:
                partDuration = math.ceil(filmDuration / numberOfParts)
                if partDuration > 10:
                    return partDuration
                else:
                    return 10
            else:
                return 0
        else:
            raise Exception("No workers detected")

    def splitFile(self, partsDuration):
        cmd = ['python', 'videoSplit.py', '-f', self.mainFile.location, '-s', str(partsDuration)]
        p = subprocess.Popen(cmd, stderr=subprocess.STDOUT)
        while p.poll() is None:
            continue
        if p.poll() == 0:
            return True
        else:
            return False

    def manageSplitedFiles(self):
        fileName = os.path.basename(self.mainFile.location)
        fileNameBare = fileName.split('.')[0]
        filesNamesList = []
        allFilesList = os.listdir(os.path.dirname(self.mainFile.location))
        for file in allFilesList:
            if fileNameBare in file and file != fileName:
                filesNamesList.append(os.path.dirname(self.mainFile.location) + '\\' + file)
        return filesNamesList

    def getConvertMsg(self, filesNamesList):
        messages = []
        for file in filesNamesList:
            messages.append({'type': 'convert_file',
                             'pid': 0,
                             'path': file,
                             'format': self.mainFile.fileExtension,
                             'resolution': self.mainFile.resolution,
                             'saveLocation': self.mainFile.saveLocation,
                             'parts': len(filesNamesList)})
        return messages

    def getNewWorkers(self):
        self.listener_thread = threading.Thread(target=self.checkWorkers)
        self.listener_thread.start()

    def checkForFilesToSend(self, worker):
        if worker.get_free_qsize() > 0:
            if not self.toConvertFiles.empty():
                return self.toConvertFiles.get()
            else:
                return False
        else:
            return False
    
    def getConvFileToSend(self, fileMessage, worker):
        fileMessage['pid'] = worker.get_pid()
        return fileMessage
    
    def concatenateConvertedFiles(self, msg):
        try:
            tmpLocation = self.mainFile.location
            saveLocation = msg['saveLocation']
            extension = msg['fileExtension']
        except Exception as e:
            print(e)
        allFilesList = os.listdir(os.path.dirname(tmpLocation))
        inputs = ""
        for i in range(len(allFilesList) - 1):
            if not allFilesList[i].endswith(extension):
                pass
            else:
                new_pipe = allFilesList[i] + "|"
                inputs += new_pipe
        inputs += allFilesList[-1]
        print("inputs: ", inputs)
        saveLocation += '/output.mp4'
        print("save location: ", saveLocation)
        cmd = "ffmpeg -i   \"concat:" +  inputs + "\" -c copy " + saveLocation
        result = subprocess.Popen(cmd, shell=True)
        while result.poll() is None:
            continue
        if result.poll() == 0:
            print("Files succesfully concatenated")
            return True
        else:
            print("Error while concatenating files")
            return False

user = UserCLI()
user.setFileData()
server = Server(user.fileData)
server.getNewWorkers()
#server.splitFile(partsDuration=server.manageFile())
server.convertFiles()
