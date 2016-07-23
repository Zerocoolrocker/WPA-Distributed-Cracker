import termios, atexit, sys, os, time

OLD_SETTINGS = None

def init_anykey():
    global OLD_SETTINGS
    OLD_SETTINGS = termios.tcgetattr(sys.stdin)
    new_settings = termios.tcgetattr(sys.stdin)
    new_settings[3] = new_settings[3] & ~(termios.ECHO | termios.ICANON) # lflags
    new_settings[6][termios.VMIN] = 0  # cc
    new_settings[6][termios.VTIME] = 0 # cc
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, new_settings)

@atexit.register
def term_anykey():
    global OLD_SETTINGS
    if OLD_SETTINGS:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, OLD_SETTINGS)

def anykey():
    ch_set = []
    ch = os.read(sys.stdin.fileno(), 1)
    while ch != None and len(ch) > 0:
        ch_set.append( ord(ch[0]) )
        ch = os.read(sys.stdin.fileno(), 1)
    return ch_set;

def key_event_handler(target_key, callback, call_args=[], call_kwargs={}):
    init_anykey()
    try:
        while True:
            key = os.read(sys.stdin.fileno(), 1)
            if key == target_key:
                # print key, ord(key)
                callback(*call_args, **call_kwargs)
                break
        term_anykey()
    except:
        term_anykey()