import time
turn_owner = None
current_last = None
deadline = None
used = set()
def reset():
    global turn_owner, current_last, deadline
    turn_owner = None
    current_last = None
    deadline = None
    used.clear()
def set_deadline(seconds):
    global deadline
    deadline = time.time() + seconds
def is_timeout():
    return deadline is not None and time.time() > deadline