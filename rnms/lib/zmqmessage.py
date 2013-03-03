
""" Messages for the IPC """

LOGGER_SERVER = 'tcp://*:5000'
LOGGER_CLIENT = 'tcp://localhost:5000'
RRD_ROUTER = 'tcp://*:5001'
RRD_WORKER = 'tcp://localhost:5001'

IPC_END     = "\x01" # Sent from main process, the sub-process will die
INIT        = "\x02" # Child init sent to parent
CONF        = "\x03" # Parent sending config to child
READY       = "\x04" # Config/job consumed



IPC_LOG     = "\x10" # Sent to logger, log this message
RRD_UPDATE  = "\x11" # Sent to rrdworker - rrd updates


# Common tasks
def init_and_config(socket):
    """
    Send the init message and block until we get the config message
    """
    socket.send(INIT)
    frames = socket.recv_multipart()
    print frames
    if frames[0] != CONF or len(frames) != 2:
        return None
    return frames[1]

