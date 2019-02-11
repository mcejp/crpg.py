from dataclasses import dataclass
from enum import Enum
from functools import wraps


class StateEnum(Enum):
    CREATING_CHARACTER = 1
    INWORLD = 2

# The game state
@dataclass
class State:
    state = StateEnum.CREATING_CHARACTER
    #pos = [0, 0]
    character = None
    character_map = None
    turn = 1
    messages = []

    def push_message(self, message):
        self.messages.append((self.turn, message))

single_player_state = None

def get_player_state():
    global single_player_state

    if single_player_state is None:
        single_player_state = State()

    return single_player_state

def requires_state(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #if g.user is None:
        #    return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs, state=get_player_state())

    return decorated_function
