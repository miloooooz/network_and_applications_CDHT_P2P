# The version of my python is Python 3.7.0

import sys
import select
import socket
import time
import random
import threading


class PingThread(threading.Thread):
    def __init__(self):
        super(PingThread, self).__init__()
    def run(self):
        ping()


class TCPListenThread(threading.Thread):
    def __init__(self):
        super(TCPListenThread,self).__init__()

    def run(self):
        TCP_listen()


def main_func():
    # the knowledge about threading is from http://www.runoob.com/python/python-multithreading.html
    global current, suc, sec_suc, pred1, pred2, port, port_init, MSS, drop_rate, host, \
        ping_seq_no1, ping_seq_no2, ack_tracker1, ack_tracker2, received_, quitok1, quitok2, filename, start_time
    start_time = time.time()
    ping_seq_no1 = 0
    ping_seq_no2 = 0
    ack_tracker1 = 0
    ack_tracker2 = 0
    host = '127.0.0.1'
    filename = False
    quitok1 = False
    quitok2 = False
    port_init = 50000
    responding_log = open('responding_log.txt', 'w')
    responding_log.close()
    requesting_log = open('requesting_log.txt', 'w')
    requesting_log.close()
    received_ = []
    # Step1. Initialization
    try:
        current = int(sys.argv[1])
        suc = int(sys.argv[2])
        sec_suc = int(sys.argv[3])
        MSS = int(sys.argv[4])
        drop_rate = float(sys.argv[5])
        pred1 = False
        pred2 = False
        if suc < 0 or suc > 255 or \
                sec_suc < 0 or sec_suc > 255 or \
                current < 0 or current > 255 or \
                current == suc or current == sec_suc or sec_suc == suc:
            print('Wrong input.')
            sys.exit()
    except ValueError:
        print('Value Error, wrong input.')
        sys.exit()

    port = current + port_init

    global TCP, UDP
    UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    UDP.bind(('', port))
    TCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    TCP.bind(('', port))



    # Ping Successor
    thread1 = PingThread()
    thread1.daemon = True
    thread2 = TCPListenThread()
    thread2.daemon = True
    thread1.start()
    thread2.start()

    while True:
        try:
            after_input()
            if quitok1 == True and quitok2 == True:
                print ('===============   Quit   =================')
                sys.exit()
        except KeyboardInterrupt:
            print('===============   Keyboard Interruption   =================')
            sys.exit()


def after_input():          # prompt for input
    global filename
    if select.select([sys.stdin, ], [], [], 0.0)[0]:
        command = sys.stdin.readline()
        command.rstrip()
        if command != '':
            # requesting a file and receive it
            command_L = command.rstrip().split(' ')
            if command_L[0] == 'request':
                filename = command_L[1]
                hash_nb = hash_func(filename)
                ask_next_tcp(hash_nb, current, filename)
                print(f'File request message for {filename} has been sent to my successor.')

            # peer departure
            if command_L[0] == 'quit':
                self_depart()


def ping():
    global suc, sec_suc, pred1, pred2, ack_tracker1, ack_tracker2, ping_seq_no1, ping_seq_no2, UDP, quitok1, quitok2
    UDP.settimeout(1.0)
    # Step 2: Ping successors
    while not quitok1 and not quitok2:
        send_ping_udp('1', suc)
        send_ping_udp('2', sec_suc)
        receive_ping_udp()
        receive_ping_udp()
        time.sleep(6)
        if  ping_seq_no1 - ack_tracker1>= 5:
            print (f'Peer {suc} is no longer alive.')
            kill_suc(suc)
            ack_tracker1 = 0
            ping_seq_no1 = 0
        if ping_seq_no2 - ack_tracker2 >= 5:
            print (f'Peer {sec_suc} is no longer alive.')
            kill_suc(sec_suc)
            ack_tracker2 = 0
            ping_seq_no2 = 0
        receive_ping_udp()
        receive_ping_udp()


def TCP_listen():
    global suc, sec_suc, pred1, pred2, TCP, quitok1, quitok2, filename
    while True:
        try:
            TCP.listen(1)
            conn, addr = TCP.accept()
            msg = conn.recv(1024)
            if msg:
                conn.close()
                data = msg.decode().split(',')

                # if quit ok, then finish, else re-send quit request
                if data[0] == 'quit ok' and data[1] == str(pred1):
                    quitok1 = True
                elif data[0] == 'quit ok' and data[1] == str(pred2):
                    quitok2 = True

                # when peer politely leave
                elif len(data) == 4 and data[0] == 'depart':
                    tcp_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    peer = int(data[1])
                    print (f'Peer {peer} will depart from the network.')
                    tcp_send.connect((host, port_init + peer))
                    response = 'quit ok,' + str(current)
                    tcp_send.send(response.encode('utf-8'))
                    suc = int(data[2])
                    sec_suc = int(data[3])
                    print (f'My first successor is now peer {suc}.')
                    print (f'My second successor is now peer {sec_suc}.')
                    tcp_send.close()

                # when peer killed
                elif len(data) == 2 and data[0] == 'my suc lost':
                    tcp_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    tcp_send.connect(('', port_init + int(data[1])))
                    response = 'my suc,' + str(suc)
                    tcp_send.send(response.encode('utf-8'))
                    tcp_send.close()
                elif len(data) == 3 and data[0] == 'my sec suc lost':
                    tcp_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    tcp_send.connect(('', port_init + int(data[1])))
                    if int(data[2]) == suc:
                        response = 'my suc,' + str(sec_suc)
                    else:
                        response = 'my suc,' + str(suc)
                    tcp_send.send(response.encode('utf-8'))
                    tcp_send.close()

                # when peer is killed and pred ask for sec suc
                elif len(data) == 2 and data[0] == 'my suc':
                    sec_suc = int(data[1])
                    print(f'My second successor is now peer {sec_suc}.')

                # others ask for file
                elif len(data) == 4 and data[3] == 'ask':
                    hash_nb = data[0]
                    req_id = data[1]
                    filename = data[2]
                    if file_loc(filename):      # find the final destination and let it return the message to req
                        receive_tcp(hash_nb, req_id)
                        transfer_file(filename, req_id)
                    else:
                        ask_next_tcp(hash_nb,req_id,filename)
                elif len(data) == 3 and data[2] == 'file':
                    peer = int(data[1])
                    print(f'Received a response message from peer {peer}, which has the file {filename}.')
                    receive_file(peer)
        except socket.error:
            pass


def send_ping_udp(one_or_two, successor):       # send ping constantly and every time after new nodes in
    global ping_seq_no1, ping_seq_no2         # ping_seq_no indicates the appearance of successors
    if one_or_two == '1':
        msg = 'ping,' + str(current) + ',' + one_or_two + ',' + str(ping_seq_no1)
        UDP.sendto(msg.encode('utf-8'), (host, successor + port_init))
        ping_seq_no1 += 1
    else:
        msg = 'ping,' + str(current) + ',' + one_or_two + ',' + str(ping_seq_no2)
        UDP.sendto(msg.encode('utf-8'), (host, successor + port_init))
        ping_seq_no2 += 1



def receive_ping_udp():         # receive the udp ping from predecessors and give response, might be request or response
    global pred1, pred2, ping_seq_no1, ping_seq_no2, ack_tracker1, ack_tracker2, suc, sec_suc
    try:
        msg = UDP.recv(1024)
        data_ = msg.decode()
        if data_ != '':
            data = data_.split(',')
            if len(data) == 4 and data[0] == 'ping':
                if data[2] == '1':
                    pred1 = int(data[1])
                elif data[2] == '2':
                    pred2 = int(data[1])
                print(f'A ping request message was received from Peer {data[1]}.')
                msg = 'ping,' + str(current) + ',' + data[3]
                UDP.sendto(msg.encode('utf-8'), (host, port_init + int(data[1])))

            elif len(data) == 3 and data[0] == 'ping':
                print(f'A ping response message was received from Peer {data[1]}.')
                if int(data[1]) == suc:
                    ack_tracker1 = int(data[2])
                elif int(data[1]) == sec_suc:
                    ack_tracker2 = int(data[2])
    except socket.error:
        pass


def hash_func(filename):
    if len(filename) != 4:
        print('Wrong file.')
        sys.exit()
    if int(filename) not in range(10000):
        print('Wrong file.')
        sys.exit()
    hashNB = int(filename) % 256
    return hashNB


def file_loc(filename):    # if return True, call receive_tcp(hashNB, req_ID)
    hashNB = hash_func(filename)
    if current == hashNB:
        print(f'File {filename} is here.')
        return True
    if current > hashNB > pred1:        # general
        print(f'File {filename} is here.')
        return True
    elif current < pred1 < hashNB:          # when current is smallest and hashNB is larger than largest
        print(f'File {filename} is here.')
        return True
    elif hashNB < current < pred1:       # when current is the smallest number and hashNB even smaller than current
        print(f'File {filename} is here.')
        return True
    print(f'File {filename} is not stored here.')
    return False


def ask_next_tcp(hashNB, req_ID, filename): # at this time we need to combine this func and receive_prev_tcp()
    try:
        tcps = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcps.connect(('', port_init + int(suc)))
        msg = str(hashNB) + ',' + str(req_ID) + ',' + filename + ',ask'
        tcps.send(msg.encode('utf-8'))
        if req_ID != current:
            print(f'File request message has been forwarded to my successor.')
        tcps.close()
    except socket.error:
        return False


def receive_tcp(hashNB, req_ID):    # tells the requesting ID that the host has the required file
    global req
    try:
        tcps = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcps.connect(('', port_init + int(req_ID)))
        msg = str(hashNB) + ',' + str(current) + ',file'
        tcps.send(msg.encode('utf-8'))
        print(f'A response message, destined for peer {req_ID}, has been sent.')
        tcps.close()
        req = req_ID
        return True
    except socket.error:
        return False


def receive_file(peer):     # if found_loc() == True, call this function
    global start_time
    print('We now start receiving the file ...')
    log = open('requesting_log.txt', 'a+')
    final = False
    ack = 0
    seq_no = 0
    udp_tsp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_tsp.bind((host, 60000 + current))
    while not final:
        packet = udp_tsp.recv(1024).decode('ISO-8859-1')
        if packet != 'FIN':
            if len(packet.split('|')) == 4:
                data = packet.split('|')
                res_seq_no = data[0]
                MSS = data[2]
                fragment = data[3]
                size = len(fragment.encode('ISO-8859-1'))
                res_ack = data[1]
                log.writelines(f'rcv                    	'
                               f'{str(time.time() - start_time)}                	'
                               f'{res_seq_no}                	'
                               f'{str(size)}                	'
                               f'{str(res_ack)}\n')

                received_.append(fragment)
                ack = size + int(res_seq_no)
                msg = str(ack) + ',' + str(seq_no) + ',' + str(size)
                udp_tsp.sendto(msg.encode('utf-8'), (host, 60000 + int(peer)))
                log.writelines(f'snd                    	'
                               f'{str(time.time() - start_time)}                	'
                               f'{str(seq_no)}                	'
                               f'{str(size)}                	'
                               f'{str(ack)}\n')
        else:
            print('The file is received.')
            with open('received_file.pdf', 'w') as file:
                for i in received_:
                    file.write(i)
            file.close()
            final = True
            udp_tsp.close()


def transfer_file(filename, req):    # if file_loc() == True, call this function
    # drop_rate is input
    global MSS, drop_rate, start_time
    udp_tsp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_tsp.bind((host, 60000 + current))
    udp_tsp.settimeout(1.0)
    seqNo = 1
    f = open(str(filename) + '.pdf', 'rb')                # file not yet defined
    log = open('responding_log.txt', 'a+')
    print('We now start sending the file ...')
    while True:
        rtx = False
        packet = f.read(MSS)
        if packet.decode('ISO-8859-1') == '':
            chunk = 'FIN'                           # when received chunk is FIN, means that receiver could stop
            print('The file is sent.')
            udp_tsp.sendto(chunk.encode('utf-8'), (host, 60000 + int(req)))
            udp_tsp.close()
            break
        else:
            chunk = str(seqNo) + '|' + str(0) + '|' + str(MSS) + '|'          # use '|' to separate each element
        length = len(packet)
        log.writelines(f'snd                    	'
                       f'{str(time.time() - start_time)}                	'
                       f'{str(seqNo)}                	'
                       f'{str(length)}                	'
                       f'0\n')
        if random.uniform(0, 1) >= drop_rate:                               # if larger than drop rate, then it will send
            udp_tsp.sendto(chunk.encode('ISO-8859-1') + packet, (host, 60000 + int(req)))
        while True:
            try:
                if not rtx:                             # while not receiving ACK, this while loop will always continue
                    msg = udp_tsp.recv(1024)
                    if len(msg.decode().split(',')) == 3:
                        received_msg = msg.decode().split(',')
                        req_ack = received_msg[0]
                        req_seq_no = received_msg[1]
                        receive_length = received_msg[2]
                        log.writelines(f'rcv                    	'
                                       f'{str(time.time() - start_time)}                	'
                                       f'{req_seq_no}                	'
                                       f'{receive_length}                	'
                                       f'{req_ack}\n')
                        break
                else:                                   # when rtx is True, means that socket was timeout before
                    log.writelines(f'RTX                    	'
                        f'{str(time.time() - start_time)}                	'
                        f'{str(seqNo)}                	'
                        f'{str(length)}                	'
                        f'0\n')
                    if random.uniform(0, 1) >= drop_rate:
                        udp_tsp.sendto(chunk.encode('ISO-8859-1') + packet, (host, 60000 + int(req)))
                        rtx = False
            except socket.timeout:                      # when not receiving ACK for long, rtx is True and start rtx
                log.writelines(f'Drop                    	'
                               f'{str(time.time() - start_time)}                	'
                               f'{str(seqNo)}                	'
                               f'{str(length)}                	'
                               f'0\n')
                rtx = True
        seqNo += length

def self_depart():    # quit decently and notify others its quit
    global host, pred1, pred2, suc, sec_suc
    try:
        # inform its pred1 that it will depart
        tcps = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcps.connect((host, port_init + pred1))
        msg = 'depart,' + str(current) + ',' + str(suc) + ',' + str(sec_suc)
        tcps.send(msg.encode('utf-8'))
        tcps.close()
        # inform its pred2 that it will depart
        tcps = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcps.connect((host, port_init + pred2))
        msg = 'depart,' + str(current) + ',' + str(pred1) + ',' + str(suc)
        tcps.send(msg.encode('utf-8'))
        tcps.close()
    except socket.error:
        return False


def kill_suc(depart_peer):  # after update, we should ping the new successor
    global suc, sec_suc, host, ping_seq_no1, ack_tracker1
    if depart_peer == suc:
        tcps = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        suc = sec_suc
        print(f'My first successor is now peer {suc}.')
        dest = port_init + suc
        tcps.connect((host, dest))
        msg = 'my suc lost,' + str(current)
        tcps.send(msg.encode('utf-8'))
        tcps.close()

    if depart_peer == sec_suc:
        tcps = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        suc = suc
        print(f'My first successor is now peer {suc}.')
        dest = port_init + suc
        tcps.connect((host, dest))
        msg = 'my sec suc lost,' + str(current) + ',' + str(sec_suc)
        tcps.send(msg.encode('utf-8'))
        tcps.close()


if __name__ == '__main__':
    main_func()
