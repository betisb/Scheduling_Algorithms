import time

import numpy as np
import sys
from enum import IntEnum
import json
from copy import deepcopy
from datetime import datetime, timedelta
import heapq
from math import ceil, sqrt
import re
import select
from threading import Event, Thread, Timer
import socket
from argparse import ArgumentParser


NUM_NODE = 9
INIT_PORT = 3000
NODE_PORT = [(INIT_PORT + i) for i in range(NUM_NODE)]
RECV_BUFFER = 4096

class STATE(IntEnum):
    """Enum class that represents node state"""
    INIT = 0
    REQUEST = 1
    HELD = 2
    RELEASE = 3


class MSG_TYPE(IntEnum):
    """Enum class that represents message type"""
    REQUEST = 0
    GRANT = 1
    RELEASE = 2
    FAIL = 3
    INQUIRE = 4
    YIELD = 5

    def __json__(self):
        return self

    def to_str(self):
        if self == 0:
            return 'REQUEST'
        elif self == 1:
            return 'GRANT'
        elif self == 2:
            return 'RELEASE'
        elif self == 3:
            return 'FAIL'
        elif self == 4:
            return 'INQUIRE'
        elif self == 5:
            return 'YIELD'
        else:
            return None


class MessageEncoder(json.JSONEncoder):
    def encode(self, obj):
        obj_dict = dict()
        obj_dict['msg_type'] = int(obj.msg_type)
        obj_dict['src'] = obj.src
        obj_dict['dest'] = obj.dest
        obj_dict['ts'] = obj.ts
        obj_dict['data'] = obj.data
        return super(MessageEncoder, self).encode(obj_dict)


class MessageDecoder(json.JSONDecoder):
    def decode(self, json_string):
        parsed_dict = super(MessageDecoder, self).decode(json_string)
        return Message(MSG_TYPE(parsed_dict['msg_type']),
                       parsed_dict['src'],
                       parsed_dict['dest'],
                       parsed_dict['ts'],
                       parsed_dict['data'])


class Message(object):
    """Class that implements the media of nodes communication.

    Attributes:
        msg_type (MSG_TYPE): type of message
        src (int): source of message
        dest (int): destination of message
        ts (int): Lamport timestamp of message
        data (str): other information of message

    """
    def __init__(self,
            msg_type=None,
            src=None,
            dest=None,
            ts=None,
            data=None,
            ):
        self.msg_type = msg_type
        self.src = src
        self.dest = dest
        self.ts = ts
        self.data = data

    def __json__(self):
        return dict(msg_type=self.msg_type,
            src=self.src,
            dest=self.dest,
            ts=self.ts,
            data=self.data)

    def __cmp__(self, other):
        if self.ts != other.ts:
            return cmp(self.ts, other.ts)
        else:
            return cmp(self.src, other.src)

    def set_type(self, msg_type):
        self.msg_type = msg_type

    def set_src(self, src):
        self.src = src

    def set_dest(self, dest):
        self.dest = dest

    def set_ts(self, ts):
        self.ts = ts

    def set_data(self, data):
        self.data = data

    def to_json(self):
        return json.dumps(self, cls=MessageEncoder)

    @staticmethod
    def to_message(json_str):
        return json.loads(json_str, cls=MessageDecoder)

def log_receive_message(msg):
	sys.stdout.write('{time} {thread_id} {src} {msg_type}\n'.format(
		time=datetime_to_str(datetime.now()),
		thread_id=msg.dest,
		src=msg.src,
		msg_type=msg.msg_type.to_str(),
		))

def log_enter_cs(ts, node_id, node_list):
	sys.stdout.write('{time} {thread_id} {node_list}\n'.format(
		time=datetime_to_str(ts),
        thread_id=node_id,
        node_list=node_list,
        ))

def log_receive_message_debug(msg, ts):
	sys.stdout.write("{time} {dest} {src} {msg_type} {msg_ts} {self_ts}\n".format(
		time=datetime_to_str(datetime.now()),
		dest=msg.dest,
        src=msg.src,
        msg_type=msg.msg_type.to_str(),
        msg_ts=msg.ts,
        self_ts=ts,
        ))



def datetime_to_str(time):
    """convert python datetime object to a
    {hour}:{min}:{second}:{millisecond} string format

    """
    return '{hour}:{min}:{second}:{millisecond}'.format(
        hour=time.hour,
        min=time.minute,
        second=time.second,
        millisecond=str(int(round(time.microsecond / 1000.0))),
        )

def create_server_socket(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', port))
    s.listen(5)
    return s

def create_client_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    return s

class ServerThread(Thread):
    """Server thread in charge of receiving and processing message.

    Attributes:
        _node (reference): reference to the owner node

    """

    def __init__(self, node):
        Thread.__init__(self)
        self._node = node

    def run(self):
        self._update()

    def _update(self):
        """Receive messages with non-blocking socket."""
        self._connection_list = []
        self._server_socket = create_server_socket(
            NODE_PORT[self._node.node_id])
        self._connection_list.append(self._server_socket)
        while True:
            (read_sockets, write_sockets, error_sockets) = select.select(
                self._connection_list, [], [])
            for read_socket in read_sockets:
                if read_socket == self._server_socket:
                    (conn, addr) = read_socket.accept()
                    self._connection_list.append(conn)
                else:
                    try:
                        msg_stream = read_socket.recv(RECV_BUFFER)
                        msgs = re.findall(r'\{(.*?)\}', msg_stream)
                        for msg in msgs:
                            self._process_message(
                                Message.to_message('{{{msg_body}}}'.format(msg_body=msg)))
                    except:
                        read_socket.close()
                        self._connection_list.remove(read_socket)
                        continue
        self._server_socket.close()

    def _process_message(self, msg):
        """Process message received from the socket.

        Args:
            msg (Message): message received by server socket

        """
        if self._node.OPTION == 1:
            log_receive_message(msg)
        # logging.log_receive_message_debug(msg, self._node.lamport_ts)

        self._node.lamport_ts = max(self._node.lamport_ts + 1, msg.ts)

        if msg.msg_type == MSG_TYPE.REQUEST:
            self._on_request(msg)
        elif msg.msg_type == MSG_TYPE.GRANT:
            self._on_grant(msg)
        elif msg.msg_type == MSG_TYPE.RELEASE:
            self._on_release(msg)
        elif msg.msg_type == MSG_TYPE.FAIL:
            self._on_fail(msg)
        elif msg.msg_type == MSG_TYPE.INQUIRE:
            self._on_inquire(msg)
        elif msg.msg_type == MSG_TYPE.YIELD:
            self._on_yield(msg)

    def _on_request(self, request_msg):
        """Handle REQUEST type message

        a. Cache the request if the node is in the critical section currently.
        b. Otherwise, check if the node has voted for a request or not.
                i. If it has, either send an INQUIRE message to the previous
                   voted requesting node or send a FAIL message to the current
                   requesting node. (depending on the timestamp and node id order
                   of the requests)
                ii. Otherwise, vote for current request directly.

        Args:
            request_msg (Message): REQUEST type message object

        """
        if self._node.state == STATE.HELD:
            heapq.heappush(self._node.request_queue, request_msg)
        else:
            if self._node.has_voted:
                heapq.heappush(self._node.request_queue, request_msg)
                response_msg = Message(src=self._node.node_id)
                if (request_msg < self._node.voted_request and
                        not self._node.has_inquired):
                    response_msg.set_type(MSG_TYPE.INQUIRE)
                    response_msg.set_dest(self._node.voted_request.src)
                    self._node.has_inquired = True
                else:
                    response_msg.set_type(MSG_TYPE.FAIL)
                    response_msg.set_dest(request_msg.src)
                self._node.client.send_message(response_msg, response_msg.dest)
            else:
                self._grant_request(request_msg)

    def _on_release(self, release_msg=None):
        """Handle RELEASE type message

        a. If request priority queue is not empty, pop out the request with
           the highest priority and handle that request.
        b. Otherwise, reset corresponding flags.

        Args:
            release_msg (Message): RELEASE type message object

        """
        self._node.has_inquired = False
        if self._node.request_queue:
            next_request = heapq.heappop(self._node.request_queue)
            self._grant_request(next_request)
        else:
            self._node.has_voted = False
            self._node.voted_request = None

    def _grant_request(self, request_msg):
        """Vote for a request

        Args:
            request_msg (Message): REQUEST type message object

        """
        grant_msg = Message(msg_type=MSG_TYPE.GRANT,
                            src=self._node.node_id,
                            dest=request_msg.src,
                            )
        self._node.client.send_message(grant_msg, grant_msg.dest)
        self._node.has_voted = True
        self._node.voted_request = request_msg

    def _on_grant(self, grant_msg):
        """Handle GRANT type message

        Increase the counter of received votes.

        Args:
            grant_msg (Message): GRANT type message object

        """
        # self._node.voting_set[grant_msg.src] = grant_msg
        self._node.num_votes_received += 1

    def _on_fail(self, fail_msg):
        """Handle FAIL type message

        Args:
            fail_msg (Message): FAIL type message object

        """
        # self._node.voting_set[fail_msg.src] = fail_msg
        pass

    def _on_inquire(self, inquire_msg):
        """Handle INQUIRE type message

        If current node is not in the critical section, send a
        YIELD message to the inquiring node, indicating it
        would like the inquiring node to revoke the vote.

        Args:
            inquire_msg (Message): INQUIRE type message object

        """
        if self._node.state != STATE.HELD:
            # self._node.voting_set[inquire_msg.src] = None
            self._node.num_votes_received -= 1
            yield_msg = Message(msg_type=MSG_TYPE.YIELD,
                                src=self._node.node_id,
                                dest=inquire_msg.src)
            self._node.client.send_message(yield_msg, yield_msg.dest)

    def _on_yield(self, yield_msg):
        """Handle YIELD type message

        Put the latest voted request back to request queue.
        Then behaves just like receiving a RELEASE message.

        Args:
            yield_msg (Message): YIELD type message object

        """
        heapq.heappush(self._node.request_queue,
                       self._node.voted_request)
        self._on_release()


class ClientThread(Thread):
    """Client thread in charge of sending requests.

    Attributes:
        _node (reference): reference to the owner node
        _client_sockets (socket list): a list of sockets
                used as communication channels among nodes.

    """

    def __init__(self, node):
        Thread.__init__(self)
        self._node = node
        self._client_sockets = [create_client_socket() for i in
                                range(NUM_NODE)]

    def run(self):
        self._update()

    def _update(self):
        """Run Request-Enter-Exit circle

        Request: requests for entering the critical section either at the
                 beginning or NEXT_REQ seconds after exiting the critical section.

        Enter: enters into the critical section when it receives enough
               votes from the its voting set.

        Exit: exits the critical section after CS_INT seconds after entering
              the critical section.

        """
        while True:
            self._node.signal_request_cs.wait()
            self._node.request_cs(datetime.now())
            self._node.signal_enter_cs.wait()
            self._node.enter_cs(datetime.now())
            self._node.signal_exit_cs.wait()
            self._node.exit_cs(datetime.now())

    def send_message(self, msg, dest, multicast=False):
        """Send message to another node

        Args:
            msg (Message): message object to be sent
            dest (int): node id of the destination node
            multicast (boolean): indicates whether the message is sent by
                                 unicast or multicast.

        """
        if not multicast:
            self._node.lamport_ts += 1
            msg.set_ts(self._node.lamport_ts)
        assert dest == msg.dest
        self._client_sockets[dest].sendall(msg.to_json())
        # self._node.MessageBuffer[dest].append([msg, datetime.now() + timedelta(0, config.DELAY[self._node.node_id][dest])])

    def multicast(self, msg, group):
        """Multicast message to a group

        Args:
            msg (Message): message object to be multicasted
            group: a list of destination node ids

        """
        self._node.lamport_ts += 1
        msg.set_ts(self._node.lamport_ts)
        for dest in group:
            new_msg = deepcopy(msg)
            new_msg.set_dest(dest)
            assert new_msg.dest == dest
            assert new_msg.ts == msg.ts
            self.send_message(new_msg, dest, True)

    def build_connection(self, num_node):
        for i in range(num_node):
            self._client_sockets[i].connect(('localhost',
                                             NODE_PORT[i]))


class DelayThread(Thread):
    """Delay thread used for simulating channel delay.

    This thread is optional, only used for debugging.

    Attributes:
        _node (reference): reference to the owner node

    """

    def __init__(self, node):
        Thread.__init__(self)
        self._node = node

    def run(self):
        self._update()

    def _update(self):
        while True:
            curr_time = datetime.now()
            for i in range(NUM_NODE):
                while (self._node.MessageBuffer[i] and
                       self._node.MessageBuffer[i][0][1] <= curr_time):
                    curr_msg = self._node.MessageBuffer[i][0][0]
                    assert curr_msg.src == self._node.node_id
                    assert curr_msg.dest == i
                    self._node.client._client_sockets[curr_msg.dest].sendall(
                        curr_msg.to_json())
                    self._node.MessageBuffer[i].pop(0)
            time.sleep(0.1)


class Node(object):
    """Class that implements a node (simulating a thread which competes for
       entering the critical section during mutual exclusion process.

    Static attributes:
        CS_INT (int): time a node spends in the critical section
        NEXT_REQ (int): time a node waits after exiting the critical section
                        before it requests another critical section entrance
        OPTION (boolean): display message log on screen or not

    Instance attributes:
        node_id (int): a unique id used for identifying the node
        state (STATE): the current state of the node regarded to critical section
                       (INIT/REQUEST/HELD/RELEASE)
        lamport_ts (int): Lamport timestamp used for ensuring total ordering of
                          request, important to resolve deadlock issue.

        has_voted (boolean): has the node voted for a request or not
        voted_request (Message): the latest request the node voted for
        request_queue (priority queue): cache the requests that have not been
                                        handled by the node

        voting_set (dictionary): a list of nodes that the node needs to get votes
                                 from in order to enter the critical section.
        num_votes_received (int): the number of votes the node has received
        has_inquired (boolean): whether the node has inquired other nodes or not

        server (Thread): thread simulating server functionality
        client (Thread): thread simulating client functionality

        signal_request_cs (Event): signal indicating the node could request
        signal_enter_cs (Event): signal indicating the node could enter
        signal_exit_cs (Event): signal indicating the node could exit

        time_request_cs (datetime): timestamp that the node sends the request
        time_exit_cs (datetime): timestamp that the node enters the critical section

    """
    CS_INT = None
    NEXT_REQ = None
    OPTION = None

    def __init__(self, node_id):
        self.node_id = node_id
        self.state = STATE.INIT

        self.lamport_ts = 0

        # for simulating delay channel debug use
        # self.Delay = DelayThread(self)
        # self.MessageBuffer = [[] for i in xrange(config.NUM_NODE)]

        # attributes as a voter (receive & process request)
        self.has_voted = False
        self.voted_request = None
        self.request_queue = []  # a priority queue (key = lamportTS, value = request)

        # attributess as a proposer (propose & send request)
        self.voting_set = self._create_voting_set()
        self.num_votes_received = 0
        self.has_inquired = False

        # threads
        self.server = ServerThread(self)
        self.server.daemon = True
        self.server.start()
        self.client = ClientThread(self)
        self.client.daemon = True

        # Event signals
        self.signal_request_cs = Event()
        self.signal_request_cs.set()
        self.signal_enter_cs = Event()
        self.signal_exit_cs = Event()

        # Timestamp for next expected request/exit
        self.time_request_cs = None
        self.time_exit_cs = None

    def _create_voting_set(self):
        voting_set = dict()
        mat_k = int(ceil(sqrt(NUM_NODE)))
        (row_id, col_id) = (int(self.node_id / mat_k),
                            int(self.node_id % mat_k))
        for i in range(mat_k):
            voting_set[mat_k * row_id + i] = None
            voting_set[col_id + mat_k * i] = None
        return voting_set

    def _reset_voting_set(self):
        for voter in self.voting_set:
            self.voting_set[voter] = None

    def request_cs(self, ts):
        """Node requests to enter critical section.

        Set state to REQEUST.
        Increase lamport timestamp by 1.
        Multicast the request to its voting set.

        """
        self.state = STATE.REQUEST
        self.lamport_ts += 1
        request_msg = Message(msg_type=MSG_TYPE.REQUEST,
                              src=self.node_id)
        self.client.multicast(request_msg, self.voting_set.keys())
        self.signal_request_cs.clear()

    def enter_cs(self, ts):
        """Node enters the critical section.

        Set state to HELD.
        Increase lamport timestamp by 1.
        Calculate the timestamp that it should exit.

        """
        self.time_exit_cs = ts + timedelta(milliseconds=Node.CS_INT)
        self.state = STATE.HELD
        self.lamport_ts += 1
        log_enter_cs(ts, self.node_id, self.voting_set.keys())
        self.signal_enter_cs.clear()

    def exit_cs(self, ts):
        """Node exits the critical section.

        Set state to RELEASE.
        Increase lamport timestamp by 1 and reset corresponding variables.
        Multicast the release message to its voting set.

        """
        self.time_request_cs = ts + timedelta(milliseconds=Node.NEXT_REQ)
        self.state = STATE.RELEASE
        self.lamport_ts += 1
        self.num_votes_received = 0
        # self._reset_voting_set()
        release_msg = Message(msg_type=MSG_TYPE.RELEASE,
                              src=self.node_id)
        self.client.multicast(release_msg, self.voting_set.keys())
        self.signal_exit_cs.clear()

    def build_connection(self, num_node):
        self.client.build_connection(num_node)

    def _check(self):
        """Run state machine.

        Check and change the node state periodically with 1 millisecond
        time granularity.

        """
        timer = Timer(0.001, self._check)
        timer.start()
        curr_time = datetime.now()
        if (self.state == STATE.RELEASE and
                self.time_request_cs <= curr_time):
            if not self.signal_request_cs.is_set():
                self.signal_request_cs.set()
        elif (self.state == STATE.REQUEST and
              self.num_votes_received == len(self.voting_set)):
            if not self.signal_enter_cs.is_set():
                self.signal_enter_cs.set()
        elif (self.state == STATE.HELD and
              self.time_exit_cs <= curr_time):
            if not self.signal_exit_cs.is_set():
                self.signal_exit_cs.set()

    def run(self):
        self.client.start()
        self._check()
        # self.Delay.start()
class MaekawaMutex(object):
    """Class that implements and runs Maekawa mutual exclusion algorithm"""
    def __init__(self, cs_int, next_req, option):
        Node.CS_INT = cs_int
        Node.NEXT_REQ = next_req
        Node.OPTION = option
        self._nodes = [Node(i) for i in range(NUM_NODE)]

    def _build_connection(self):
        for node in self._nodes:
            node.build_connection(NUM_NODE)

    def run(self):
        self._build_connection()
        for node in self._nodes:
            node.run()

def create_arg_parser():
    parser = ArgumentParser(
        description='A distributed mutual exclusion program '
        'implemented with Maekawa algorithm',
        )
    parser.add_argument(
        '-cs_int',
        action='store',
        dest='cs_int',
        help='time a node spends in the critical section',
        type=int,
        default=5,
        required=False,
        )
    parser.add_argument(
        '-next_req',
        action='store',
        dest='next_req',
        help='time a node waits after exiting the critical section '
        'before it requests another critical section entrance',
        type=int,
        default=7,
        required=False,
        )
    parser.add_argument(
        '-tot_exec_time',
        action='store',
        dest='tot_exec_time',
        help='total execution time for a node',
        type=int,
        default=7,
        required=False,
        )
    parser.add_argument(
        '-option',
        action='store',
        dest='option',
        help='display message log on screen',
        type=int,
        default=0,
        required=False,
        )
    return parser

def run_mutex(cs_int, next_req, option):
    maekawa_mutex = MaekawaMutex(cs_int, next_req, option)
    maekawa_mutex.run()

if __name__ == '__main__':
    parser = create_arg_parser()
    args = parser.parse_args()
    mutex_thread = Thread(
        target=run_mutex,
        args=(args.cs_int, args.next_req, args.option),
        )
    mutex_thread.daemon = True
    mutex_thread.start()
    time.sleep(args.tot_exec_time)
