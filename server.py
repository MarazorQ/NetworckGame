import asyncore
import pickle
import socket
from random import randint

BUFFER_SIZE = 512

outgoing = []
score = [0, 0]


class Player:
    def __init__(self, x, y, user_id):
        self.x = x
        self.y = y
        self.id = user_id
        self.shoot = False
        self.score = 0

    def __del__(self):
        return 'Delete'


def update_world(msg):
    arr = pickle.loads(msg)
    user_id = arr[3]
    player_dict[user_id].x = arr[1]
    player_dict[user_id].y = arr[2]
    player_dict[user_id].shoot = arr[4]
    player_dict[user_id].score = arr[5]
    update = None
    for i in outgoing:
        if arr[0] == 'position update':
            update = ['player locations']
            for key, value in player_dict.items():
                update.append([value.x, value.y, key, value.shoot, value.score])
        if arr[0] == 'close':
            for key, value in list(player_dict.items()):
                player_dict[key].score = 0
                if user_id == value.id:
                    del player_dict[key]

        remove = []

        try:
            i.send(pickle.dumps(update))
        except socket.error:
            remove.append(i)

        for r in remove:
            outgoing.remove(r)


player_dict = {}


class MainServer(asyncore.dispatcher):
    WIDTH = 500
    HEIGHT = 500

    def __init__(self, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(('', port))
        self.listen(20)
        self.id = 0

    def handle_accept(self):
        conn, addr = self.accept()
        outgoing.append(conn)
        self.id = 2 if self.id == 1 else 1
        height = randint(0, self.HEIGHT)
        player = Player(0, height, self.id)
        conn.send(pickle.dumps(['create connection', self.id]))
        player_dict[self.id] = player
        SecondaryServer(conn)


class SecondaryServer(asyncore.dispatcher_with_send):
    def handle_read(self):
        received_data = self.recv(BUFFER_SIZE)
        if received_data:
            update_world(received_data)
        else:
            self.close()


MainServer(4323)
asyncore.loop()
