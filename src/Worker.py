import os
import pickle
import queue
import socket
import threading
import time

from converter import Converter

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
    def __init__(self, pid=None, qsize=5, listener=None, client=None, tmp_directory='tmp'):
        self._conversion_files = queue.Queue(maxsize=qsize)
        self._converted_files = queue.Queue(maxsize=qsize)
        self._max_qsize = qsize
        self._free_qsize = qsize
        self.tmp_directory = tmp_directory
        if pid is None:
            self._pid = os.getpid()
        else:
            self._pid = pid
        if not os.path.exists(tmp_directory):
            os.makedirs(tmp_directory)

    def __eq__(self, other):
        return self._pid == other._pid

    def __str__(self):
        return "PID: {}, Free space: {}".format(self.get_pid(), self.get_free_qsize())

    def get_pid(self):
        return self._pid

    def get_qsize(self):
        return self._conversion_files.qsize()

    def get_free_qsize(self):
        return self._max_qsize - self._conversion_files.qsize()

    def set_free_qsize(self, free):
        self._free_qsize = free

    def get_join_msg(self):
        return {'type': 'join',
                'pid': self._pid,
                'qsize': self.get_qsize()}

    def parse_server_join_answer(self, msg):
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

    def parse_server_free_space_request(self, msg):
        if msg['type'] == 'free_space_request' \
                and msg['pid'] == self.get_pid():
            return True
        else:
            return False

    def parse_resp_file(self, msg):
        # TODO add filter
        return False

    def send_free_space_answer(self, timeout):
        start_time = time.time()
        while time.time() < start_time + timeout:
            msg = self._listener.recv()
            if self.parse_server_free_space_request(msg):
                self._client.send(self.get_free_space_msg())
                break

    def parse_convert_file(self, msg):
        if msg['type'] == 'covert_file' and msg['pid'] == self.get_pid():
            return True
        else:
            return False

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
                elif self.parse_resp_file(msg):
                    # Start a sending thread
                    thread = threading.Thread(target=self.send_file)
                    thread.daemon = True
                    thread.start()
                else:
                    print("No response from server")
            except EOFError as e:
                continue

    def append_new_file(self, msg):
        fileData = {'path': msg.get('path'),
                    'fileExtension': msg.get('fileExtension'),
                    'resolution': msg.get('resolution')}
        try:
            lock.acquire()
            self._conversion_files.put(fileData)
            lock.release()
        except Exception as e:
            print(e)
        return fileData

    def check_for_files_to_process(self):
        while True:
            try:
                if not self._conversion_files.empty():
                    # Lock threads for taking filedata from queue
                    lock.acquire()
                    fileData = self._conversion_files.get()
                    lock.release()

                    # pack data to send to a thread
                    filedata_packed = pickle.dumps(fileData, -1)

                    thread = threading.Thread(target=self.convertFile, args={filedata_packed})
                    thread.daemon = True
                    thread.start()
            except Exception as e:
                print(e)

    def convertFile(self, filedata_packed):
        # Unpack filedata
        fileData = pickle.loads(filedata_packed)

        print(f'filedata: {fileData}')
        fileName = os.path.basename(fileData.get('path')).split('.')[0]
        ffmpegPath = os.getenv('FFMPEG_PATH').split(';')
        newPath = self.tmp_directory + '\\' + fileName + "_converted video." + fileData.get('fileExtension')
        conv = Converter(ffmpeg_path=ffmpegPath[0],
                         ffprobe_path=ffmpegPath[1])
        convert = conv.convert(fileData.get('path'), newPath, {
            'format': fileData.get('fileExtension'),
            'audio': {
                'codec': 'aac',
                'samplerate': 11025,
                'channels': 2
            },
            'video': {
                'codec': 'h264',
                'width': fileData.get('resolution')[0],
                'height': fileData.get('resolution')[1],
                'fps': 25
            }})
        print("File conversion started")
        for timecode in convert:
            print(f'\rConverting ({timecode:.2f}) ...')
        lock.acquire()
        self._converted_files.put(newPath)
        lock.release()
        # TODO add data from received file

    def send_new_file(self, sendFile):
        pass

    def send_file(self):
        try:
            if not self._conversion_files.empty():
                lock.acquire()
                sendFile = self._converted_files.get()
                lock.release()
                thread = threading.Thread(target=self.send_new_file, args=sendFile)
                thread.daemon = True
                thread.start()
        except Exception as e:
            print(e)
        finally:
            lock.release()

    def start_listening(self):
        """Start listening thread for receiving new request from server"""
        self.listener_thread = threading.Thread(target=worker.listen)
        self.listener_thread.daemon = True
        self.listener_thread.start()

    def start_conversion(self):
        """Start conversion thread for converting files in conversion queue"""
        self.conversion_threat = threading.Thread(target=worker.check_for_files_to_process)
        self.conversion_threat.daemon = True
        self.conversion_threat.start()


if __name__ == '__main__':
    worker = Worker()
    time.sleep(5)
    worker.connect_to_server()
    worker.start_listening()
    worker.start_conversion()
