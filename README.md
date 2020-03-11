# network_and_applications_CDHT_P2P
## Coursework project for Network and Applications -- P2P simulation using CDHT
### Instruction:
> cmd run `chmod +x ./setup.sh` to make it executable.
>
> cmd run `./setup.sh` to execute it
### Function Introduction:
> #### Classes:
> + `PingThread()`: The class for constantly listening and sending UDP Ping request and response in order to check the existence of current node's successors and predecessors
> + `TCPListenThread()`: The class for constantly listening TCP message for the file requests and sending response when needed.
> #### Functions:
> + `after_input()`: This function recognizes the input for polite quit or file request and parse them into related functions.
>                    When the input contains 'request', it calls `hash_nb()` and `ask_next_tcp()` for the file request.
>                    When the input contains 'quit', it calls `self_depart()` and informs other predecessors its leaving.
> + `ping()`: This function keeps pinging its successors and listening the ping request from predecessors.
>             It cooperate with `send_ping_udp()` and `receive_ping_udp()`.
>             If ping_seq_no is 5 units larger than the ACK_no, we consider that successor as killed and call the `kill_suc()` function to inform the rest successors the new update.
> + `TCP_listen()`: This function is responsible for all the messages from other nodes including the file request, polite departing, successor killing and new successor update.
> + `send_ping_udp()`: Simply sends Ping request to its two successors.
> + `receive_ping_udp()`: This function takes charge of two types of UDP messages, 1. Ping request message received from its predecessors. 2. Ping response message received from its successors.
> + `hash_func()`: This function takes filename as input and calculate the hash number and return it.
> + `file_loc()`: This function checks whether the file is contained in the current peer or not.
> + `ask_next_tcp()`: Takes request_id, filename and hash_nb as input and requests file to the successor of the current peer.
> + `receive_tcp()`: Takes the hash_nb and the requst_id as inputs, this function is called when the `file_loc()` returns `True`. And it establishes the TCP connection between current peer and the requesting peer to inform the start of file transfer.
> + `receive_file()`: This function allows the file receiver to start receiving the packages from the file sender. At the meantime, it will writes a requesting log file to record all the logs.
> + `transfer_file()`: In this function there are several steps. First we construct the UDP connection between sender and receiver, since the unreliability of UDP, there is drop rate and thus we need to set up a simple protocol called stop-and-wait to ensure the package transfer.
>                     We read the file into chunks with maximum size of MSS, then we pack up the chunks with our information to send it to the receiver, and then the sender begins waiting for the ACK message sent from the receiver to make sure it has receives the file and then it could send the next chunks.
>                     And if the package is lost, `rtx` will be `True` and the package will be resent. Same as `receive_file()`, this function also writes a responding log to record all the logs including `DROP` and `RTX`.
> + `self_depart()`: This function is called when the input is `Quit`, the current node will set up the connection between itself and its two successors and inform them its leaving.
> + `kill_suc()`: This function is called when current node notices the sudden kill of its successor or second successor, and after update, it should inform its new successor and to update its new second successor.

### Other information:
> In this project my sample file is ***2012.pdf***, the main program that implements the functions is ***CDHT.py***, more detailed specification is ***Assignment.pdf*** and there is a simple report ***CDHT Assignment Report.pdf***
