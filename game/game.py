from flask import app, render_template, Blueprint, abort, request, url_for, redirect

from game import data
from game.data import Character, Item
from game.state import requires_state, StateEnum

bp = Blueprint('game', __name__, url_prefix='/game')


def teleport(state, character, map_filename, pos):
    map = data.maps[map_filename]
    character.pos = pos

    if character == state.character:
        state.push_message(f'You now find yourself in {map.name}')


@bp.route('/', methods=['POST', 'GET'])
@requires_state
def index(state):
    if state.state == StateEnum.CREATING_CHARACTER:
        ###
        state.character_map = data.DEFAULT_MAP
        state.character = Character(name='Unk_Player', level=1, items=[])
        state.character.items.append(Item(name='a key', icon=('key', 'gold')))
        state.character.items.append(Item(name='a dagger', icon=('plain-dagger', 'grey')))
        teleport(state, state.character, state.character_map, data.maps[state.character_map].entry)
        state.state = StateEnum.INWORLD
        return redirect(url_for('game.index'))
        ###

        if request.method != 'POST':
            return render_template('creating_character.html', state=state)
        else:
            state.character_map = make_test_map()
            state.character = Character(name=request.form['charactername'], level=1, items=[], pos=state.character_map.entry)
            state.character.items.append(Item(name='a key', icon=('key', 'gold')))
            state.character.items.append(Item(name='a dagger', icon=('plain-dagger', 'grey')))
            state.state = StateEnum.INWORLD
            return redirect(url_for('game.index'))
    elif state.state == StateEnum.INWORLD:
        if request.method != 'POST':
            return render_template('inworld.html',
                                   biomes=data.biomes,
                                   map=data.maps[state.character_map],
                                   state=state,
                                   tiletypes=data.tiletypes)
    else:
        abort(500)

@bp.route('/reload-data')
def reload_data():
    data.reload_data()
    return redirect(url_for('game.index'))

@bp.route('/restart')
@requires_state
def restart(state):
    state.state = StateEnum.CREATING_CHARACTER
    return redirect(url_for('game.index'))
