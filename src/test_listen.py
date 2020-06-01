from multiprocessing.connection import Listener

address = ('localhost', 8080)
listener = Listener(address)
conn = listener.accept()
#print('Connection accepted from', conn.last_accepted)
while True:
    msg = conn.recv()
    if msg['key'] == 0:
        conn.close()
        print(msg['key'])
        break
listener.close()

