import select

from cell.serializers import Deserialize
from connection.node import Node
from connection.skt import Skt
import threading

from router.process_cell import ProcessCell


class Circuit:

    def __init__(self, circ_id: int, node: Node, conn, session_key=None):
        self.circ_id = circ_id
        self.node = node
        self.conn = conn
        self.skt = Skt(node.host, 12345)
        self.session_key = session_key
        self.routing_table = {}

    def main(self):
        sockets_list = [self.conn, self.skt]
        while True:
            read_sockets, write_socket, error_socket = select.select(sockets_list, [], [])
            for socket in read_sockets:
                try:
                    cell = str(socket.recv(1024).decode())
                    cell_dict = Deserialize.json_to_dict(cell)
                    if cell_dict:
                        threading.Thread(target=self.process_cell(), args=(cell_dict, socket,), daemon=True)
                except:
                    print("Error")

    def process_cell(self, cell, socket):
        processcell = ProcessCell(cell, self.conn, self.skt, socket, self.node, self.circ_id)
        processcell.cmd_to_func[cell['CMD']]()
        return None