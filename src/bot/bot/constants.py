from mcdreforged.api.rtext import RTextTranslation, RColor

CONFIG_FILE_NAME = 'config.json'
DATA_FILE_NAME = 'botList.json'


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
