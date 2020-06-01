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
    """De-serializing raw socket message to python object format"""
    return pickle.loads(msg)


def parse_raw_output(msg):
    """Serializing python object to raw socket message"""
    return pickle.dumps(msg)


class Worker:
    def __init__(self, pid=None, qsize=5, tmp_directory='tmp'):
        self._conversion_files = queue.Queue(maxsize=qsize)
        self.send_file = queue.Queue(maxsize=qsize)
        self._max_qsize = qsize
        self.tmp_directory = tmp_directory
        self._connected = False
        if pid is None:
            self._pid = os.getpid()
        else:
            self._pid = pid

    def __eq__(self, other):
        return self._pid == other._pid

    def __str__(self):
        return "PID: {}, Free space: {}".format(self.get_pid(), self.get_free_qsize())

    def get_pid(self):
        return self._pid

    def get_qsize(self):
        return self._conversion_files.qsize()

    def get_free_qsize(self):
        return self._max_qsize - self.get_qsize()

    def connect_to_server(self):
        while not self._connected:
            try:
                msg = self.get_join_msg()
                msg = parse_raw_output(msg)
                client.send(msg)
                self._connected = True
            except Exception as e:
                print('Unable to connect to server. Trying again in 5s')
                print(e)
                time.sleep(5)

    def get_join_msg(self):
        return {'type': 'join',
                'pid': self._pid,
                'qsize': self._max_qsize}

    def parse_server_join_answer(self, msg):
        return msg['type'] == 'join' \
               and msg['pid'] == self.get_pid() \
               and msg['result'] == 'accepted'

    def parse_server_free_space_request(self, msg):
        return msg['type'] == 'free_space_request' \
               and msg['pid'] == self.get_pid()

    def parse_convert_file(self, msg):
        return msg['type'] == 'covert_file' and msg['pid'] == self.get_pid()

    def parse_resp_file(self, msg):
        return msg['type'] == 'send_file' and msg['pid'] == self.get_pid()

    def get_free_space_msg(self):
        return {'type': 'free_space_answer',
                'pid': self.get_pid(),
                'free_space': self.get_free_qsize()}

    def get_converted_file_msg(self):
        # TODO add arguments
        return {'type': 'converted_file',
                'pid': self.get_pid()}

    def listen(self):
        """
        Listen to a server connection
        Returns:

        """
        while True:
            try:
                msg = client.recv(1024)
                msg = parse_raw_input(msg)
                if self.parse_server_join_answer(msg):
                    # Get join message from server
                    client.send(parse_raw_output(self.get_free_space_msg()))
                    print("Connection from server established")
                elif self.parse_convert_file(msg):
                    # Add new file to convertion queue
                    self.append_new_file(msg)
                    print('Received a new file')
                    # TODO does server require a response
                elif self.parse_server_free_space_request(msg):
                    # Send free queue response
                    client.send(parse_raw_output(self.get_free_space_msg()))
                    print('Responded with free queue size')
                elif self.parse_resp_file(msg):
                    # Start a sending thread
                    if self.send_file.qsize() > 0:
                        client.send(parse_raw_output(self.get_converted_file_msg()))
                else:
                    print("No response from server")
            except EOFError as e:
                continue

    def append_new_file(self, msg):
        """
        Append a new file to a convertion queue
        Args:
            msg: msg with data about a new file

        Returns: none
        """
        file_data = {'path': msg.get('path'),
                     'fileExtension': msg.get('format'),
                     'resolution': msg.get('resolution')}
        print(f'new file: {file_data}')
        self._conversion_files.put(file_data)

    def check_for_files_to_process(self):
        """
        Check for files ready to be converted
        Returns:

        """
        while True:
            try:
                if not self._conversion_files.empty():
                    # Take a filedata from a conversion queue
                    file_data = self._conversion_files.get()

                    # pack data to send to a thread
                    filedata_packed = pickle.dumps(file_data, -1)

                    # Start a new thread with processing this data
                    thread = threading.Thread(target=self.convertFile, args={filedata_packed})
                    thread.daemon = True
                    thread.start()
            except Exception as e:
                # In case of no files await 2 sec
                time.sleep(2)
                print(e)

    def convertFile(self, filedata_packed):
        """
        Convert a file
        Args:
            filedata_packed: file data packed in pickle.dumps(file_data, -1)

        Returns:

        """
        # Unpack filedata
        file_data = pickle.loads(filedata_packed)

        file_name = os.path.basename(file_data.get('path')).split('.')[0]
        dir_name = os.path.dirname(file_data.get('path'))
        ffmpeg_path = os.getenv('FFMPEG_PATH').split(';')
        if os.name == 'nt':
            new_path = dir_name + '\\' + file_name + "_converted video." + file_data.get('fileExtension')
        else:
            new_path = dir_name + '/' + file_name + "_converted video." + file_data.get(
                'fileExtension')
        conv = Converter(ffmpeg_path=ffmpeg_path[0],
                         ffprobe_path=ffmpeg_path[1])
        convert = conv.convert(file_data.get('path'), new_path, {
            'format': file_data.get('fileExtension'),
            'audio': {
                'codec': 'aac',
                'samplerate': 11025,
                'channels': 2
            },
            'video': {
                'codec': 'h264',
                'width': file_data.get('resolution')[0],
                'height': file_data.get('resolution')[1],
                'fps': 25
            }})
        print("File conversion started")
        for timecode in convert:
            print(f'\rConverting ({timecode:.2f}) ...')
        self.send_file.put(new_path)

    def start_listening(self):
        """Start listening thread for receiving new request from server"""
        self.listener_thread = threading.Thread(target=worker.listen)
        self.listener_thread.daemon = True
        self.listener_thread.start()

    def start_conversion(self):
        """Start conversion thread for converting files in conversion queue"""
        self.conversion_threat = threading.Thread(target=worker.check_for_files_to_process)
        self.conversion_threat.start()


if __name__ == '__main__':
    worker = Worker()
    worker.connect_to_server()
    worker.start_listening()
    worker.start_conversion()
