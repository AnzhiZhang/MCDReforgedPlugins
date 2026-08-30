CONFIG_FILE_NAME = 'config.json'
DATA_FILE_NAME = 'botList.json'
BIN_FILE_NAME = 'botBin.json'


# Carpet ``/player`` action roots that can safely be forwarded to an online
# fake player.  Lifecycle operations (spawn / kill) keep using the dedicated
# Bot manager commands so its online state and auto-update behaviour stay in
# sync.
CARPET_ACTIONS = {
    'stop': (),
    'use': ('once', 'continuous', 'interval 20'),
    'jump': ('once', 'continuous', 'interval 20'),
    'attack': ('once', 'continuous', 'interval 20'),
    'drop': (
        'once', 'continuous', 'interval 20',
        'all', 'mainhand', 'offhand', '0'
    ),
    'dropStack': (
        'once', 'continuous', 'interval 20',
        'all', 'mainhand', 'offhand', '0'
    ),
    'swapHands': ('once', 'continuous', 'interval 20'),
    'hotbar': ('1', '2', '3', '4', '5', '6', '7', '8', '9'),
    'mount': ('anything',),
    'dismount': (),
    'sneak': (),
    'unsneak': (),
    'sprint': (),
    'unsprint': (),
    'look': (
        'north', 'south', 'east', 'west', 'up', 'down',
        'at ~ ~ ~', '~ ~'
    ),
    'turn': ('left', 'right', 'back', '~ ~'),
    'move': ('forward', 'backward', 'left', 'right'),
}

# These actions are valid without an additional argument in Carpet v26.2.
CARPET_ACTIONS_WITHOUT_ARGUMENTS = {
    'stop', 'use', 'jump', 'attack', 'drop', 'dropStack', 'swapHands',
    'mount', 'dismount', 'sneak', 'unsneak', 'sprint', 'unsprint', 'move'
}


class DIMENSION:
    OVERWORLD = 0
    THE_NETHER = -1
    THE_END = 1

    STR_TRANSLATION = {
        0: 'minecraft:overworld',
        -1: 'minecraft:the_nether',
        1: 'minecraft:the_end'
    }
    INT_TRANSLATION = {
        '0': OVERWORLD,
        '-1': THE_NETHER,
        '1': THE_END,
        'overworld': OVERWORLD,
        'the_nether': THE_NETHER,
        'the_end': THE_END,
        'minecraft:overworld': OVERWORLD,
        'minecraft:the_nether': THE_NETHER,
        'minecraft:the_end': THE_END,
        'nether': THE_NETHER,
        'end': THE_END
    }
