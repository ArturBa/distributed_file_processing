import subprocess
import sys
from converter import Converter
from UserCLI import *

class Server:
    def __init__ (self, mainFile, toConvertFiles = None, workerList = None, fileData = None):
        self.mainFile = mainFile
        self.toConvertFiles = toConvertFiles
        self.workerList = workerList
        self.fileData = fileData

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
        conv = Converter(ffmpeg_path="C:\\Users\\HP\\Downloads\\ffmpeg\\bin\\ffmpeg.exe",
                         ffprobe_path="C:\\Users\\HP\\Downloads\\ffmpeg\\bin\\ffprobe.exe")
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
if server.splitFile():
    print("File successfully splitted")
else:
    print("Error while splitting file")
    sys.exit(-1)
server.convertFile()