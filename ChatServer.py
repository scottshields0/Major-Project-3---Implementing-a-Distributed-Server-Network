from ChatMessageParser import *
from socket import *
import os
import selectors
import logging

##############################################################################################################

class BaseConnectionData():
    """ ConnectionData is an abstract base class that other classes that encapsulate data associated with an 
    ongoing connection will be derived from. In this application, two classes will derive from ConnectionData,
    one representing data associated with a connected server and one representing data associated with a 
    connected client.         
    
    The fundamental responsibility of classes derived from ConnectionData is to store a write buffer 
    associated with a particular socket. This server will append messages to be sent to this write buffer and 
    will then send the messages at a later point when it is possible to do so (i.e. the next time select() is 
    called by the main loop). This functionality is defined in this base class. Other functionality will be 
    defined in derived subclasses.
    """    
    def __init__(self):
        self.write_buffer = b''

class ServerConnectionData(BaseConnectionData):
    """ ServerConnectionData encapsulates data associated with a connection to another server. It derives from 
    BaseConnectionData which means it contains a write buffer, in addition to additional properties defined 
    in this class that are specific to connections with other servers.
    """    
    def __init__(self, id, server_name, server_info):
        super(ServerConnectionData, self).__init__()
        self.id = id
        self.server_name = server_name     # Stores the name of the server
        self.server_info = server_info     # Stores a human-readable description of the server
        self.first_link_id = None          # The ID of the first host on the path to this server

class ClientConnectionData(BaseConnectionData):    
    """ ClientConnectionData encapsulates data associated with a connection to a client application. It 
    derives from BaseConnectionData which means it contains a write buffer, in addition to additional 
    properties defined in this class that are specific to connections with client applications.
    """
    def __init__(self, id, client_name, client_info):
        super(ClientConnectionData, self).__init__()
        self.id = id
        self.client_name = client_name      # Stores the name of the client
        self.client_info = client_info      # Stores a human-readable description of the client
        self.first_link_id = None           # The ID of the first host on the path to this client

##############################################################################################################

class CRCServer(object):
    def __init__(self, options, run_on_localhost=False):
        """ Initializes important values for CRCServer objects. Noteworthy variables include:
        
        * self.hosts_db (dictionary): this dictionary should be used to store information about all other 
            servers and clients that this server knows about. The key should be the remote machine's ID and 
            the value should be its corresponding ServerConnectionData or ClientConnectionData that you create
            when processing the remote machine's Registration Message.
        * self.adjacent_server_ids (list): this list should store the IDs of all adjacent servers. You can use
            this list to find the appropriate ServerConnectionData objects stored in self.hosts_db when needed
        * self.adjacent_client_ids (list): this list should store the IDs of all adjacent clients. It serves
            the same purpose as self.adjacent_server_ids except for client machines.
        * self.status_updates_log (list): the message of any status updates addressed to this server should be
            placed in this list. This is purely for the purpose of grading.
        * self.id (int): the ID of this server. It is initialized upon class instantiation.
        * self.server_name (string): the name of this server. It is initialized upon class instantiation.
        * self.server_info (string): a description of this server. It is initialized upon class instantiation.
        * self.port (int): the port this server's listening socket should listen on.
        * self.connect_to_host (string): the human-readable name of the remote server that this server should 
            connect to on startup. If this is empty then this server is the first server to come online and 
            does not need to connect to any other servers on startup. THIS IS ONLY USED FOR LOGGING.
        * self.connect_to_host_addr (string): the IP address of the remote server that this server should 
            connect to on startup.
        * self.connect_to_port (int): the port of the remote server that this server should connect to on
            startup. If this is empty then this server is the first server to come online and does not need to
            connect to any other servers on startup.
        * self.request_terminate (bool): a flag used by the testing application to indicate whether your code
            should continue running or shutdown. You should NOT change the value of this variable in your code
                
        Args:
            options (Options): an object containing various properties used to configure the server
            run_on_localhost (bool): a boolean indiciating whether this server should connected to 
                applications via localhost or an actual IP address
        Returns:
            None        
        """

        # Create selector for non-blocking I/O
        self.sel = selectors.DefaultSelector()

        # Network state tracking
        self.hosts_db = {}
        self.adjacent_server_ids = []
        self.adjacent_user_ids = []
        self.status_updates_log = []

        # Server configuration from options
        self.id = options.id
        self.server_name = options.servername
        self.server_info = options.info
        
        self.port = options.port
        self.connect_to_host = options.connect_to_host
        
        self.connect_to_host_addr = '127.0.0.1'
        self.connect_to_port = options.connect_to_port

        self.request_terminate = False

        # Message handlers mapping
        self.message_handlers = {
            0x00: self.handle_server_registration_message,
            0x01: self.handle_status_message,
            0x80: self.handle_client_registration_message,
            0x81: self.handle_client_chat_message,
            0x82: self.handle_client_quit_message,
        }

        self.log_file = options.log_file
        self.logger = None
        self.init_logging()

##############################################################################################################

    def run(self):
        """ This method is called to start the server. This function should NOT be called by an code you 
        write. It is being called by CRCTestManager. DO NOT EDIT THIS METHOD.
        
        Args:
            None
        Returns:
            None        
        """        
        self.print_info("Launching server %s..." % self.server_name)

        # Set up the server socket that will listen for new connections
        self.setup_server_socket()

        # If we are supposed to connect to another server on startup, then do so now
        if self.connect_to_host and self.connect_to_port:
            self.connect_to_server()
        
        # Begin listening for connections on the server socket
        self.check_IO_devices_for_messages()
        
##############################################################################################################

    def setup_server_socket(self):
        """ This function is responsible for setting up the server socket and registering it with your 
        selector.
        
        NOTE: Server sockets are read from, but never written to. This is important when registering the 
            socket with your selector
        NOTE: Later on, you will need to differentiate between the server socket (which accepts new 
            connections) and all other sockets that are passing messages back and forth between hosts. You can
            use what is stored in the data parameter that you provide when registering your socket with the  
            selector to accomplish this.
        
        Args:
            None
        Returns:
            None        
        """        
        self.print_info("Configuring the server socket...")

        # Create TCP server socket
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server_socket.bind(('', self.port))
        self.server_socket.listen()
        
        # Make socket non-blocking and register with selector
        self.server_socket.setblocking(False)
        # Use None as data to identify this as the server socket
        self.sel.register(self.server_socket, selectors.EVENT_READ, None)

    def connect_to_server(self):
        """ This function is responsible for connecting to a remote CRC server upon starting this server. Each
        new CRC Server (except for the first one) registers with an existing server on start up. That server 
        is its entry point into the existing CRC server network.

        NOTE: Even though you know this is a server, it's best to use a BaseConnectionData object for the data
            parameter to be consistent with how other connections are added. That will get modified when you 
            get a registration message from the server you just connected to.

        Args:
            None
        Returns:
            None        
        """
        self.print_info("Connecting to remote server %s:%i..." % (self.connect_to_host, self.connect_to_port))

        # Create TCP client socket and connect to remote server
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect((self.connect_to_host_addr, self.connect_to_port))
        
        # Make socket non-blocking and register with selector
        client_socket.setblocking(False)
        connection_data = BaseConnectionData()
        self.sel.register(client_socket, selectors.EVENT_READ | selectors.EVENT_WRITE, connection_data)
        
        # Send server registration message with last_hop_id=0 (initial registration)
        reg_msg = ServerRegistrationMessage.bytes(self.id, 0, self.server_name, self.server_info)
        connection_data.write_buffer += reg_msg
        
        self.print_info("Connected to another server")

    def check_IO_devices_for_messages(self):
        """ This function manages the main loop responsible for processing input and output on all sockets 
        this server is connected to. This is accomplished in a nonblocking manner using the selector created 
        in __init__.

        NOTE: All calls to select() MUST be inside the while loop. Select() is itself a blocking call and we 
            need to be able to terminate the server to test its functionality. The server may not be able to  
            shut down if calls to select() are made outside of the loop since those calls can block.
        NOTE: Pass a short timeout value into your select() call (e.g. 0.1 seconds) to prevent your code from 
            hanging when it is time to terminate it

        Args:
            None
        Returns:
            None        
        """
        self.print_info("Listening for new connections on port " + str(self.port))
        
        while not self.request_terminate:
            # Get ready sockets with timeout to allow termination
            events = self.sel.select(timeout=0.1)
            
            for key, mask in events:
                if key.data is None:
                    # This is the server socket (listening socket)
                    self.accept_new_connection(key)
                else:
                    # This is a client/server connection socket
                    self.handle_io_device_events(key, mask)
                    
        # Clean up when terminating
        self.cleanup()

    def cleanup(self):
        """ This function handles releasing all allocated resources associated with this server (i.e. our 
        selector and any sockets opened by this server).

        NOTE: You can get a list of all sockets registered with the selector by accessing a hidden dictionary 
            of the selector: _fd_to_keys. You can extract a list of io_devices from this using the command: 
            list(self.sel._fd_to_key.values())

        Args:
            None
        Returns:
            None        
        """
        self.print_info("Cleaning up the server")
        
        # Get all registered sockets and close them
        for key in list(self.sel.get_map().values()):
            try:
                # Close the socket if it has a close method
                if hasattr(key.fileobj, 'close'):
                    key.fileobj.close()
            except Exception:
                # Skip any sockets that have already been closed
                continue
            
        # Close the selector
        self.sel.close()

    def accept_new_connection(self, io_device):
        """ This function is responsible for handling new connection requests from other servers and from 
        clients. This function should be called from self.check_IO_devices_for_messages whenever the listening 
        socket has data that can be read.

        NOTE: You don't know at this point whether new connection requests are comming from a new server or a  
            new client (you'll find that out when processing the registration message sent over the connected  
            socket). As such you don't know whether to use a ServerConncetionData or a ClientConnectionData  
            object when registering the socket with the selector. Instead, use a BaseConnectionData object so 
            you have access to a write_buffer. We'll replace this with the appropriate object later when 
            handling the registration message.

        Args:
            io_device (SelectorKey): 
        Returns:
            None        
        """
        # Accept the connection
        conn, addr = io_device.fileobj.accept()
        conn.setblocking(False)
        
        # Register with selector using BaseConnectionData (we don't know if it's server or client yet)
        connection_data = BaseConnectionData()
        self.sel.register(conn, selectors.EVENT_READ | selectors.EVENT_WRITE, connection_data)

    def handle_io_device_events(self, io_device, event_mask):
        """ This function is responsible for handling READ and WRITE events for a given IO device. Incomming  
        messages will be read and passed to the appropriate message handler here and the write buffer  
        associated with this socket will be sent over the socket here.

        Args:
            io_device (SelectorKey):
            event_mask (int): 
        Returns:
            None        
        """
        # Handle READ events
        if event_mask & selectors.EVENT_READ:
            try:
                recv_data = io_device.fileobj.recv(4096)
                if recv_data:
                    # We received data, handle it
                    self.handle_messages(io_device, recv_data)
                else:
                    # No data means connection was closed by peer
                    self.sel.unregister(io_device.fileobj)
                    io_device.fileobj.close()
                    return
            except ConnectionResetError:
                # Handle connection reset
                self.sel.unregister(io_device.fileobj)
                io_device.fileobj.close()
                return
                
        # Handle WRITE events
        if event_mask & selectors.EVENT_WRITE:
            if io_device.data.write_buffer:
                # We have data to send
                try:
                    sent = io_device.fileobj.send(io_device.data.write_buffer)
                    # Clear the sent portion of the write buffer
                    io_device.data.write_buffer = io_device.data.write_buffer[sent:]
                except ConnectionResetError:
                    # Handle connection reset
                    self.sel.unregister(io_device.fileobj)
                    io_device.fileobj.close()
                    return

    def handle_messages(self, io_device, recv_data):
        """ This function is responsible for parsing the received bytes into separate messages and then 
        passing each of the received messages to the appropriate message handler. Message parsing is offloaded
        to the MessageParser class. Messages are passed to the appropriate message handler using the 
        self.message_handlers dictionary which associates the appropriate message handler function with each
        valid message type value.

        You do not need to make any changes to this method.        

        Args:
            io_device (SelectorKey):
            recv_data (bytes): 
        Returns:
            None        
        """
        messages = MessageParser.parse_messages(recv_data)

        for message in messages:
             # If we recognize the command, then process it using the assigned message handler
            if message.message_type in self.message_handlers:
                self.print_info("Received msg from Host ID #%s \"%s\"" % (message.source_id, message.bytes))
                self.message_handlers[message.message_type](io_device, message)
            else:
                raise Exception("Unrecognized command: " + str(message))

##############################################################################################################

    def send_message_to_host(self, destination_id, message):
        """ This is a helper function meant to encapsulate the code needed to send a message to a specific 
        host machine, identified based on the machine's unique ID number.

        Args:
            destination_id (int): the ID of the destination machine
            message (bytes): the packed message to be delivered 
        Returns:
            None        
        """
        if destination_id in self.hosts_db:
            self.print_info("Sending message to Host ID #%s \"%s\"" % (destination_id, message))
            # Get the connection data for the destination host
            dest_connection = self.hosts_db[destination_id]
            
            # Get the ID of the first server we need to send through
            first_link_id = dest_connection.first_link_id
            
            # If first_link_id is our ID, this is an adjacent host - send directly to it
            if first_link_id == self.id:
                # Find the socket for the destination host itself
                for key in self.sel.get_map().values():
                    if (key.data and hasattr(key.data, 'id') and 
                        key.data.id == destination_id):
                        # Found the socket, add message to its write buffer
                        key.data.write_buffer += message
                        break
            else:
                # This is a non-adjacent host - route through the first link
                for key in self.sel.get_map().values():
                    if (key.data and hasattr(key.data, 'id') and 
                        key.data.id == first_link_id):
                        # Found the socket, add message to its write buffer
                        key.data.write_buffer += message
                        break

    def broadcast_message_to_servers(self, message, ignore_host_id=None):
        """ This is a helper function meant to encapsulate the code needed to broadcast a message to the 
        entire network of connected servers. You may call self.send_message_to_host() in this function. 
        Remember that it is only possible to send messages to servers that are adjacent to you. Those adjacent 
        servers can then continue to broadcast this message to futher away machines after they receive it. 
        This function should NOT broadcast messages to adjacent clients.

        You will sometimes need to exclude a host from the broadcast (e.g. you don't want to broadcast a 
        message back to the machine that originally sent you this message). You should use the ignore_host_id 
        parameter to help with this. If the ID is None than the message should be broadcast to all adjacent 
        servers. Alternatively, if it is not None you should not broadcast the message to any adjacent 
        servers with the ID value included in the parameter.

        Args:
            message (bytes): the packed message to be delivered
            ignore_host_id (int): the ID of a host that this message should not be delievered to 
        Returns:
            None        
        """
        # Loop through all adjacent server IDs
        for server_id in self.adjacent_server_ids:
            # Skip the server we want to ignore (if any)
            if server_id != ignore_host_id:
                # Find the socket for this server and add message to write buffer
                for key in self.sel.get_map().values():
                    if (key.data and hasattr(key.data, 'id') and 
                        key.data.id == server_id):
                        key.data.write_buffer += message
                        break

    def broadcast_message_to_adjacent_clients(self, message, ignore_host_id=None):
        """ This is a helper function meant to encapsulate the code needed to broadcast a message to all 
        adjacent clients. Its functionality is similar to self.broadcast_message_to_servers(). The two 
        functions are separated from each other as some messages should only be broadcast to other servers, 
        not both servers and clients. If you need to broadcast a message to both servers and clients than you 
        can simply call both functions. The ignore_host_id parameter serves the same purpose as the parameter
        with the same name in the self.broadcast_message_to_servers() function.

        Args:
            message (bytes): the packed message to be delivered
            ignore_host_id (int): the ID of a host that this message should not be delievered to 
        Returns:
            None        
        """
        for client_id in self.adjacent_user_ids:
            if client_id != ignore_host_id:
                # Find the socket for this client and add message to write buffer
                for key in self.sel.get_map().values():
                    if (key.data and hasattr(key.data, 'id') and 
                        key.data.id == client_id):
                        key.data.write_buffer += message
                        break

    def send_message_to_unknown_io_device(self, io_device, message):
        """ The ID of a machine becomes known once it successfully registers with the network. In the event 
        that an error occurs during registration, status messages cannot be sent to the new machine based on
        the machine's ID as this isn't yet known. In this case status messages must be sent based on the 
        socket the registration message was received over. This method should encapsulate the code needed to 
        send a message across the io_device that was provided to the registration message handler when the 
        error occured.

        Args:
            io_device (SelectorKey): An object containing a reference to the socket that the message should be
                delievered to (see io_device.fileobj).
            message (bytes): the packed message to be delievered 
        Returns:
            None        
        """
        self.print_info("Sending message to an unknown IO device \"%s\"" % (message))
        io_device.data.write_buffer += message

##############################################################################################################

    def handle_server_registration_message(self, io_device, message):
        """ This function handles the initial registration process for new servers. 

        Upon receiving a server registration message, check to make sure a machine with that ID does not 
        already exist in the network. If the ID does already exist, send a StatusUpdateMessage with the 
        message code 0x02 and the message string "A machine has already registered with ID [X]", where [X] is 
        replaced with the ID in the registration message, and then return from this function. Since you don't 
        know the ID of the new server, use a destination_ID of 0 when making this StatusUpdateMessage.

        If the new server's ID is unique, create a new ServerConnectionData object containing the server's 
        information (e.g. server name, server_info) and store the ServerConnectionData object in 
        self.hosts_db. You will need to determine what the first_link_id value should be when creating the 
        ServerConnectionData object.

        You will need to determine if this new server is adjacent to the server processing this message. If 
        the new server is adjacent, add its ID to self.adjacent_server_ids and modify the assocated io_device 
        to replace the associated data object with your new ServerConnectionData object. You can do this by
        calling: self.sel.modify(io_device.fileobj, 
                                 selectors.EVENT_READ | selectors.EVENT_WRITE, 
                                 my_new_server_connection_data_obj)

        If this registration message came from a brand new adjacent server then it is the responsibility of 
        the server processing this message to inform the new server of all other connected servers and 
        clients. You can accomplish this by creating ServerRegistationMessages and ClientRegistrationMessages 
        for each of the existing servers and clients and sending them to the brand new adjacent machine. These
        messages will then be processed by the new adjacent server's handle_server_registration_message() 
        function. You can check if a host stored in self.hosts_db is a Server or a Client using python's 
        isinstance() command (e.g. isinstance(self.hosts_db[0], ServerConnectionData) returns True or False 
        depending on the type of the object stored in self.hosts_db[0])

        Finally, a message should be broadcast to the rest of the network informing it about this new server. 
        This message should not be broadcast back to the new machine.

        Args:
            io_device (SelectorKey): This object contains references to the socket (io_device.fileobj) and to 
                the data associated with the socket on registering with the selector (io_device.data).
            message (ServerRegistrationMessage): The new server registration message to be processed
        Returns:
            None        
        """
        # Check for duplicate ID
        if message.source_id in self.hosts_db:
            error_msg = StatusUpdateMessage.bytes(
                self.id, 0, 0x02,
                f"A machine has already registered with ID {message.source_id}"
            )
            self.send_message_to_unknown_io_device(io_device, error_msg)
            return

        # Create new server connection data
        new_server_connection = ServerConnectionData(
            message.source_id, 
            message.server_name, 
            message.server_info
        )

        # Determine if this is an adjacent server
        # If last_hop_id is 0, this server connected directly to us
        is_adjacent = (message.last_hop_id == 0)
        
        if is_adjacent:
            # For adjacent servers, we are their first link
            new_server_connection.first_link_id = self.id
            # Add to adjacent servers list
            self.adjacent_server_ids.append(message.source_id)
            # Update the socket's associated data
            self.sel.modify(io_device.fileobj, 
                           selectors.EVENT_READ | selectors.EVENT_WRITE, 
                           new_server_connection)
        else:
            # For non-adjacent servers, we route through the last_hop_id
            new_server_connection.first_link_id = message.last_hop_id

        # Add the new server to our database
        self.hosts_db[message.source_id] = new_server_connection

        # If this is an adjacent server, send it information about all existing hosts
        if is_adjacent:
            # First, send our own registration to the new server
            reg_msg = ServerRegistrationMessage.bytes(
                self.id,
                0,  # we are the source, so last_hop is 0
                self.server_name,
                self.server_info
            )
            new_server_connection.write_buffer += reg_msg

            # Then send info about all other hosts
            for host_id, host_data in self.hosts_db.items():
                # Don't send info about the new server back to itself
                if host_id != message.source_id:
                    if isinstance(host_data, ServerConnectionData):
                        # Create server registration message
                        reg_msg = ServerRegistrationMessage.bytes(
                            host_data.id,
                            self.id,  # we are forwarding, so we are the last hop
                            host_data.server_name,
                            host_data.server_info
                        )
                        new_server_connection.write_buffer += reg_msg
                    elif isinstance(host_data, ClientConnectionData):
                        # Create client registration message
                        reg_msg = ClientRegistrationMessage.bytes(
                            host_data.id,
                            self.id,  # we are forwarding, so we are the last hop
                            host_data.client_name,
                            host_data.client_info
                        )
                        new_server_connection.write_buffer += reg_msg

        # Broadcast this new server to all other servers (except the one that just registered)
        broadcast_msg = ServerRegistrationMessage.bytes(
            message.source_id,
            self.id,  # we are forwarding, so we are the last hop
            message.server_name,
            message.server_info
        )
        self.broadcast_message_to_servers(broadcast_msg, ignore_host_id=message.source_id)

##############################################################################################################

    def handle_client_registration_message(self, io_device, message):
        """ This function handles the initial registration process for new clients. 

        Upon receiving a client registration message, check to make sure a machine with that ID does not 
        already exist in the network. If the ID does already exist, send a StatusUpdateMessage with the 
        message code 0x02 and the message string "A machine has already registered with ID [X]", where [X] is 
        replaced with the ID in the registration message, and then return from this function. Since you don't 
        know the ID of the new client, use a destination_ID of 0 when making this StatusUpdateMessage.

        If the new client's ID is unique, create a new ClientConnectionData object containing the client's 
        information (e.g. client name, client info) and store the ClientConnectionData object in
        self.hosts_db. You will need to determine what the first_link_id value should be when creating the 
        ClientConnectionData object.

        You will need to determine if this new client is adjacent to the server processing this message. If 
        the new client is adjacent, add its ID to self.adjacent_client_ids and modify the assocated io_device 
        to replace the associated data object with your new ClientConnectionData object. You can do this by
        calling: self.sel.modify(io_device.fileobj, 
                                 selectors.EVENT_READ | selectors.EVENT_WRITE, 
                                 my_new_client_connection_data_obj)
        You should also send a Welcome status update to the newly connected adjacent client. The message code 
        should be 0x00 and the message content should be "Welcome to the Clemson Relay Chat network [X]", 
        where [X] is the client's name. 

        If this registration message came from a brand new adjacent client then it is the responsibility of 
        the server processing this message to inform the new client of all other connected clients. You can 
        accomplish this by creating ClientRegistrationMessages for each of the existing clients and sending 
        them to the brand new adjacent machine. You can check if a host stored in self.hosts_db is a Server 
        or a Client using python's isinstance() command 
        (e.g. isinstance(self.hosts_db[0], ServerConnectionData) returns True or False depending on the type 
        of the object stored in self.hosts_db[0])

        Finally, a message should be broadcast to the rest of the network informing it about this new client. 
        This message should not be broadcast back to the new machine.

        Args:
            io_device (SelectorKey): This object contains references to the socket (io_device.fileobj) and to 
                the data associated with the socket on registering with the selector (io_device.data).
            message (ClientRegistrationMessage): The new client registration message to be processed
        Returns:
            None        
        """
        # 1. Check for duplicate ID
        if message.source_id in self.hosts_db:
            error_msg = StatusUpdateMessage.bytes(
                self.id,  # from this server
                0,        # to unknown client (use 0)
                0x02,     # duplicate ID error code
                f"Someone has already registered with ID {message.source_id}"
            )
            self.send_message_to_unknown_io_device(io_device, error_msg)
            return

        # 2. Create new client connection data
        new_client_connection = ClientConnectionData(
            message.source_id,
            message.client_name,
            message.client_info
        )

        # 3. Determine if this is an adjacent client
        is_adjacent = (message.last_hop_id == 0)
        
        if is_adjacent:
            # This client connected directly to us
            new_client_connection.first_link_id = self.id
            self.adjacent_user_ids.append(message.source_id)
            # Update socket's associated data
            self.sel.modify(io_device.fileobj, 
                           selectors.EVENT_READ | selectors.EVENT_WRITE, 
                           new_client_connection)
            
            # Send welcome message to new adjacent client
            welcome_msg = StatusUpdateMessage.bytes(
                self.id,
                message.source_id,
                0x00,  # welcome status code
                f"Welcome to the Clemson Relay Chat network {message.client_name}"
            )
            new_client_connection.write_buffer += welcome_msg
        else:
            # Non-adjacent client, route through last_hop_id
            new_client_connection.first_link_id = message.last_hop_id

        # 4. Add to hosts database
        self.hosts_db[message.source_id] = new_client_connection

        # 5. If adjacent, send information about existing clients
        if is_adjacent:
            for host_id, host_data in self.hosts_db.items():
                if host_id != message.source_id:  # Don't send info about the new client to itself
                    if isinstance(host_data, ClientConnectionData):
                        # Create client registration message
                        reg_msg = ClientRegistrationMessage.bytes(
                            host_data.id,
                            self.id,  # we are forwarding, so we are the last hop
                            host_data.client_name,
                            host_data.client_info
                        )
                        new_client_connection.write_buffer += reg_msg

        # 6. Broadcast new client to network (except back to source)
        broadcast_msg = ClientRegistrationMessage.bytes(
            message.source_id,
            self.id,  # we are forwarding, so we are the last hop
            message.client_name,
            message.client_info
        )
        self.broadcast_message_to_servers(broadcast_msg, ignore_host_id=message.last_hop_id)
        self.broadcast_message_to_adjacent_clients(broadcast_msg, ignore_host_id=message.source_id)

##############################################################################################################

    def handle_status_message(self, io_device, message):
        """ This function handles status messages. 

        Upon receiving a stauts message, check is if the destination ID is your ID or if it is 0. If either of
        these are true, then the status message is addressed to you. Append the content of the message to 
        self.status_updates_log (this is just for grading purposes). Otherwise, if it is not addressed to you
        and a machine with the desintation_id of the status message exists then forward it on to its intended 
        destination. This should be a very short function.

        Args:
            io_device (SelectorKey): This object contains references to the socket (io_device.fileobj) and to 
                the data associated with the socket on registering with the selector (io_device.data).
            message (StatusUpdateMessage): The status update message that needs to be processed
        Returns:
            None        
        """
        # Check if message is for us (our ID or broadcast 0)
        if message.destination_id == self.id or message.destination_id == 0:
            # Log the status message
            self.status_updates_log.append(message.content)
        # If not for us and destination exists, forward it
        elif message.destination_id in self.hosts_db:
            self.send_message_to_host(message.destination_id, message.bytes)

##############################################################################################################

    def handle_client_chat_message(self, io_device, message):
        """ This function handles client chat messages. 

        Upon receiving a chat message, check to see if the intended destination_id exists. If so, forward the 
        chat message on to the intended destination. If the intended destination_id does not exist then send
        a StatusUpdateMessage back to the machine that sent you this chat message with an UnknownID message 
        code of 0x01 with the message content "Unknown ID [X]", where [X] is replaced with the Unknown ID. 
        This should be a short function.
       
        Args:
            io_device (SelectorKey): This object contains references to the socket (io_device.fileobj) and to 
                the data associated with the socket on registering with the selector (io_device.data).
            message (ClientChatMessage): The client chat message that needs to be processed
        Returns:
            None        
        """
        # Check if destination exists and is a client
        if (message.destination_id in self.hosts_db and 
            isinstance(self.hosts_db[message.destination_id], ClientConnectionData)):
            # Forward the message to destination
            self.send_message_to_host(message.destination_id, message.bytes)
        else:
            # Send Unknown ID status message back to source
            error_msg = StatusUpdateMessage.bytes(
                self.id,
                message.source_id,
                0x01,  # Unknown ID status code
                f"Unknown ID {message.destination_id}"
            )
            self.send_message_to_host(message.source_id, error_msg)

##############################################################################################################

    def handle_client_quit_message(self, io_device, message):
        """ This function handles when a client quits the network. 

        Upon receiving a client quit message, check to make sure a client with this ID exists. If so, 
        broadcast the quit message to all over adjacent servers and clients that this client is quitting. Make 
        sure you don't send the message back to the client that is quitting. You should then delete the client
        and its ClientConnectionData from self.hosts_db and (if it is adjacent to this server) from the 
        adjacent_user_ids list.
               
        Args:
            io_device (SelectorKey): This object contains references to the socket (io_device.fileobj) and to 
                the data associated with the socket on registering with the selector (io_device.data).
            message (ClientQuitMessage): The client quit message that needs to be processed
        Returns:
            None        
        """
        # Check if client exists
        if message.source_id in self.hosts_db:
            # Get the client's first_link_id to avoid sending back to the source path
            client_data = self.hosts_db[message.source_id]
            ignore_server_id = client_data.first_link_id
            
            # Broadcast quit message to network (except back to quitting client's path)
            self.broadcast_message_to_servers(message.bytes, ignore_host_id=ignore_server_id)
            self.broadcast_message_to_adjacent_clients(message.bytes, ignore_host_id=message.source_id)
            
            # Remove from adjacent_user_ids if it was adjacent
            if message.source_id in self.adjacent_user_ids:
                self.adjacent_user_ids.remove(message.source_id)
            
            # Remove from hosts database
            del self.hosts_db[message.source_id]
    
##############################################################################################################    
    

    # DO NOT EDIT ANY OF THE FUNCTIONS BELOW THIS LINE
    # These are helper functions to assist with logging and list management
    # ----------------------------------------------------------------------


    ######################################################################
    # This block of functions enables logging of info, debug, and error messages
    # Do not edit these functions. init_logging() is already called by the template code
    # You are encouraged to use print_info, print_debug, and print_error to log
    # messages useful to you in development

    def init_logging(self):
        # If we don't include a log file name, then don't log
        if not self.log_file:
            return

        # Get a reference to the logger for this program
        self.logger = logging.getLogger("IRCServer")
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

        # Create a file handler to store the log files
        fh = logging.FileHandler(os.path.join(__location__, 'Logs', '%s' % self.log_file), mode='w')

        # Set up the logging level. It defaults to INFO
        log_level = logging.INFO
        
        # Define a formatter that will be used to format each line in the log
        formatter = logging.Formatter(
            ("%(asctime)s - %(name)s[%(process)d] - "
             "%(levelname)s - %(message)s"))

        # Assign all of the necessary parameters
        fh.setLevel(log_level)
        fh.setFormatter(formatter)
        self.logger.setLevel(log_level)
        self.logger.addHandler(fh)

    def print_info(self, msg):
        print("[%s] \t%s" % (self.server_name,msg))
        if self.logger:
            self.logger.info(msg)

    # This function takes two lists and returns the union of the lists. If an object appears in both lists,
    # it will only be in the returned union once.
    def union(self, lst1, lst2): 
        final_list = list(set(lst1) | set(lst2)) 
        return final_list

    # This function takes two lists and returns the intersection of the lists.
    def intersect(self, lst1, lst2): 
        final_list = list(set(lst1) & set(lst2)) 
        return final_list

    # This function takes two lists and returns the objects that are present in list1 but are NOT
    # present in list2. This function is NOT commutative
    def diff(self, list1, list2):
        return (list(set(list1) - set(list2)))