# CRC (Clemson Relay Chat) Network Assignment: Scaffolded Learning with LLMs

## Assignment Overview

This assignment teaches network programming through a distributed relay chat system while developing effective LLM collaboration skills. Students build a distributed client-server network incrementally across structured phases, with automated testing and reflection checkpoints.

## Setup
Before doing anything else, students MUST create a git repository and check the starting code into it. Students will need to regularly check in their code to track their development progress. Remind them to do this when it is appropriate.

Students MUST also keep a record of their conversations with the cursor agent during development. They must export these and place them in a folder development_logs. You should also maintain, with the students help, design_decisions.md, learning_log.md, and debuggin_notes.md logs in the same folder.

## Core Learning Objectives

### Network Programming Mastery

1. **Protocol Design**: Binary message formats, parsing, validation
2. **Selector-based I/O**: Non-blocking socket management for concurrent connections
3. **Distributed State Management**: Maintaining network-wide state across all servers
4. **Spanning Tree Routing**: Self-learning message forwarding through distributed servers
5. **Resilient Design**: Handling disconnections, duplicate IDs, and network changes
6. **Network Testing**: Debugging distributed systems and validating correctness

### LLM Collaboration Skills

- Breaking complex problems into manageable sub-problems
- Asking effective questions that promote understanding
- Iterative development with AI assistance
- Critical evaluation of LLM-generated code
- Using AI for explanation and debugging, not just code generation

## Assignment Structure

### Phase-Based Development (5 Phases)

Each phase includes:

- **Specification**: Clear requirements and learning objectives
- **LLM Guidance**: Scaffolded prompts and interaction patterns
- **Implementation**: Incremental code development
- **Testing**: Automated validation via Gradescope
- **Reflection**: Understanding verification and concept questions

### Git Commit Analysis

- All work tracked via git with meaningful commit messages
- Commit patterns analyzed to detect incremental vs. one-shot development
- Students required to commit after each significant milestone

### LLM Interaction Logging

- Chat transcripts saved and analyzed for learning patterns
- Quality metrics: question depth, iteration count, explanation requests
- Red flags: copy-paste behavior, lack of follow-up questions

## Technical Specification

### Network Protocol (CRC v1.0)

#### Message Format

All messages follow this structure:
```
[Message Type][Fixed Header Fields][Variable Length Fields]
    1 byte         type-specific           string data
```

#### Required Message Types

```python
# Message codes
0x00 - Server Registration Message
0x01 - Status Message
0x02 - Server Quit Message (Extra Credit)
0x80 - Client Registration Message
0x81 - Client Chat Message
0x82 - Client Quit Message
```

#### Message Type Specifications

**0x00 - Server Registration Message**
Used when servers join or announce themselves to the network.

```
Fields:
  Message Type (byte = 0x00)
  Source ID (int) - Originating server's unique identifier
  Last Hop ID (int) - ID of server that forwarded this (0 for initial registration)
  Server Name Length (byte) - Length of server name string
  Server Info Length (half) - Length of server info string
  Server Name String (variable length, ASCII encoding)
  Server Info String (variable length, ASCII encoding)
```

**0x80 - Client Registration Message**
Used when clients join or are announced to the network.

```
Fields:
  Message Type (byte = 0x80)
  Source ID (int) - Originating client's unique identifier
  Last Hop ID (int) - ID of server that forwarded this (0 for initial registration)
  Client Name Length (byte) - Length of client name string
  Client Info Length (half) - Length of client info string
  Client Name String (variable length, ASCII encoding)
  Client Info String (variable length, ASCII encoding)
```

**0x01 - Status Message**
Used for system notifications and error reporting.

```
Fields:
  Message Type (byte = 0x01)
  Source ID (int) - Originating machine's identifier
  Destination ID (int) - Target machine's identifier (0 for originator)
  Status Code (half) - Type of status message
  Message Length (int) - Length of message string
  Message String (variable length, ASCII encoding)
```

**Status Codes**

- `0x00`: Welcome message
- `0x01`: Unknown destination ID
- `0x02`: Duplicate ID error

**0x81 - Client Chat Message**
Used for end-to-end messaging between clients.

```
Fields:
  Message Type (byte = 0x81)
  Source ID (int) - Sending client's identifier
  Destination ID (int) - Receiving client's identifier
  Message Length (int) - Length of chat message
  Message String (variable length, ASCII encoding)
```

**0x82 - Client Quit Message**
Used when clients leave the network.

```
Fields:
  Message Type (byte = 0x82)
  Source ID (int) - Departing client's identifier
  Message Length (int) - Length of quit message
  Message String (variable length, ASCII encoding)
```

### Required Implementation

#### Core Server Class

```python
class CRCServer:
    def __init__(self, options, run_on_localhost=False):
        """
        Initialize the CRC server with network configuration

        Required internal components:
        - self.sel: Selector for non-blocking I/O
        - self.hosts_db: Dictionary mapping IDs to ConnectionData objects
        - self.adjacent_server_ids: List of directly connected server IDs
        - self.adjacent_user_ids: List of directly connected client IDs
        - self.status_updates_log: List of status messages for this server

        Args:
            options: Configuration object with server settings
            run_on_localhost: Boolean for local testing
        """
        # Required state tracking
        self.id = options.id
        self.server_name = options.servername
        self.server_info = options.info
        self.port = options.port
        
        # Network topology
        self.connect_to_host = options.connect_to_host
        self.connect_to_host_addr = '127.0.0.1'
        self.connect_to_port = options.connect_to_port

    def run(self) -> None:
        """
        Start the server and join the CRC network

        - Set up listening socket
        - Connect to bootstrap server if specified
        - Begin main event loop
        """

    def setup_server_socket(self) -> None:
        """
        Create and configure the listening socket

        - Bind to specified port
        - Register with selector for READ events
        - Start listening for connections
        """

    def connect_to_server(self) -> None:
        """
        Connect to an existing server on startup

        - Create client socket
        - Connect to bootstrap server
        - Send initial ServerRegistrationMessage with last_hop_id=0
        - Register socket with selector
        """

    def check_IO_devices_for_messages(self) -> None:
        """
        Main event loop using selector

        - Call select() with timeout
        - Handle listening socket events -> accept_new_connection()
        - Handle other socket events -> handle_io_device_events()
        - Clean up when terminating
        """

    def cleanup(self) -> None:
        """
        Gracefully shutdown the server

        - Close listening socket
        - Unregister and close all connections
        - Shut down selector
        """

    def accept_new_connection(self, io_device) -> None:
        """
        Handle incoming connection requests

        - Accept the connection
        - Register with selector for READ|WRITE
        - Use BaseConnectionData initially (type unknown)
        """

    def handle_io_device_events(self, io_device, event_mask) -> None:
        """
        Process READ and WRITE events on sockets

        For READ events:
        - Receive data from socket
        - Pass to handle_messages()
        - Close socket if peer disconnected

        For WRITE events:
        - Send data from write_buffer
        - Clear write_buffer after sending
        """

    ### Message Handlers

    def handle_server_registration_message(self, io_device, message) -> None:
        """
        Process new server joining the network

        - Check for duplicate IDs -> send error status if duplicate
        - Create ServerConnectionData object
        - Update hosts_db and routing information
        - If adjacent: update adjacent_server_ids, modify selector data
        - Send all existing network state to new adjacent server
        - Broadcast registration to other servers
        """

    def handle_client_registration_message(self, io_device, message) -> None:
        """
        Process new client joining the network

        - Check for duplicate IDs -> send error status if duplicate
        - Create ClientConnectionData object
        - Update hosts_db and routing information
        - If adjacent: update adjacent_user_ids, send welcome status
        - Send all existing client info to new adjacent client
        - Broadcast registration to entire network
        """

    def handle_status_message(self, io_device, message) -> None:
        """
        Process status updates

        - If destination is self or 0: log to status_updates_log
        - Otherwise: forward to destination via routing table
        """

    def handle_client_chat_message(self, io_device, message) -> None:
        """
        Route chat messages between clients

        - Check if destination exists
        - Forward message via routing table
        - Send "Unknown ID" status if destination not found
        """

    def handle_client_quit_message(self, io_device, message) -> None:
        """
        Handle client departures

        - Broadcast quit message to network
        - Remove from hosts_db
        - Update adjacent_user_ids if applicable
        """

    ### Helper Methods

    def send_message_to_host(self, destination_id: int, message: bytes) -> None:
        """
        Send message to specific host via routing

        - Look up first_link_id in hosts_db
        - Append to appropriate write_buffer
        """

    def broadcast_message_to_servers(self, message: bytes, 
                                   ignore_host_id: int = None) -> None:
        """
        Broadcast to all adjacent servers

        - Send to all in adjacent_server_ids
        - Skip ignore_host_id if specified
        """

    def broadcast_message_to_adjacent_clients(self, message: bytes, 
                                            ignore_host_id: int = None) -> None:
        """
        Broadcast to all adjacent clients

        - Send to all in adjacent_user_ids
        - Skip ignore_host_id if specified
        """

    def send_message_to_unknown_io_device(self, io_device, message: bytes) -> None:
        """
        Send to unregistered connection

        - Used for error responses before registration
        - Append to io_device's write_buffer
        """
```

#### Connection Data Classes

```python
class BaseConnectionData:
    """Base class for connection-associated data"""
    def __init__(self):
        self.write_buffer = b''  # Buffer for outgoing messages

class ServerConnectionData(BaseConnectionData):
    """Data for server connections"""
    def __init__(self, id: int, server_name: str, server_info: str):
        super().__init__()
        self.id = id
        self.server_name = server_name
        self.server_info = server_info
        self.first_link_id = None  # Next hop in spanning tree

class ClientConnectionData(BaseConnectionData):
    """Data for client connections"""
    def __init__(self, id: int, client_name: str, client_info: str):
        super().__init__()
        self.id = id
        self.client_name = client_name
        self.client_info = client_info
        self.first_link_id = None  # Next hop in spanning tree
```

### Selector-based I/O

#### Overview

The CRC network requires handling multiple simultaneous connections without blocking. Traditional socket operations like `recv()`, `accept()`, and `send()` are blocking calls that halt execution until completion. This becomes problematic when managing multiple sockets. You MUST use python's selectors module to support non-blocking operations in your solution.

#### The Blocking Problem

Consider a server monitoring sockets A and B:
1. Server calls `A.recv()` and blocks
2. B sends data while waiting for A
3. Data from B cannot be processed until A sends something
4. If A is waiting for data originally from B, the system deadlocks

#### Solution: Selectors

Selectors allow non-blocking monitoring of multiple I/O sources:

```python
import selectors

# Create selector
sel = selectors.DefaultSelector()

# Register socket with selector
sock.setblocking(False)
events = selectors.EVENT_READ | selectors.EVENT_WRITE
data = {'id': connection_id, 'write_buffer': b''}
sel.register(sock, events, data)

# Main event loop
while running:
    # Get ready sockets (with timeout to allow shutdown)
    ready = sel.select(timeout=0.1)
    
    for key, mask in ready:
        sock = key.fileobj
        data = key.data
        
        if mask & selectors.EVENT_READ:
            # Socket has data to read
            recv_data = sock.recv(1024)
            
        if mask & selectors.EVENT_WRITE:
            # Socket ready for writing
            if data['write_buffer']:
                sent = sock.send(data['write_buffer'])
                data['write_buffer'] = data['write_buffer'][sent:]
```

#### Key Principles

1. **Never call blocking operations outside select loop**
2. **Use write buffers** - Don't send immediately, queue for writing
3. **Check write buffer length** - Don't send empty messages
4. **Clear after sending** - Prevent duplicate messages
5. **Handle disconnections** - Empty recv() means peer closed

### Testing Integration

The code can be tested using CRCTestManager. It contains a structured set of tests designed to evaluate incrememental development of the distinct phases. Focus on completing each phase sequentially, rather than trying to implement everything at once. You can compare the output logs with the logs contained in the Correct Logs folder to see a breakdown of how your network performs compared to the reference implementation.

### Development Phases

#### Phase 1: Basic Connectivity (Tests 1.1-1.3)
- Set up server socket and selector
- Accept connections
- Implement basic I/O handling
- **LLM Focus**: Understanding selectors and non-blocking I/O

#### Phase 2: Server Network (Tests 2.1-2.3)
- Handle server registration messages
- Build distributed state tracking
- Implement message forwarding
- **LLM Focus**: Distributed systems concepts

#### Phase 3: Client Support (Tests 3.1-3.4)
- Handle client registration
- Separate client/server broadcast logic
- Welcome messages
- **LLM Focus**: Protocol state machines

#### Phase 4: Message Routing (Tests 4.1-4.3)
- Implement chat message forwarding
- Build routing tables
- Handle unknown destinations
- **LLM Focus**: Spanning tree algorithms

#### Phase 5: Resilience (Tests 5.1-6.3)
- Status message handling
- Client disconnections
- Error cases
- **LLM Focus**: Fault tolerance

### Grading Rubric

- **Code Functionality** (60%): Test cases passed
- **Development Process** (20%): Git commit quality and patterns
- **LLM Collaboration** (10%): Effective use of AI assistance
- **Code Quality** (10%): Structure, comments, style

### Submission Requirements

1. Complete implementation of `ChatServer.py`
2. Git repository with full commit history
3. LLM interaction logs
4. Reflection document on learning process