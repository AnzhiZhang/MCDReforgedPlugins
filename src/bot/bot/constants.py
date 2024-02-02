from mcdreforged.api.rtext import RTextTranslation, RColor

CONFIG_FILE_NAME = 'config.json'
DATA_FILE_NAME = 'botList.json'


class DIMENSION:
    OVERWORLD = 0
    THE_NETHER = -1
    THE_END = 1

    DISPLAY_TRANSLATION = {
        0: RTextTranslation(
            'createWorld.customize.preset.overworld',
            color=RColor.green
        ),
        -1: RTextTranslation(
            'advancements.nether.root.title',
            color=RColor.dark_red
        ),
        1: RTextTranslation(
            'advancements.end.root.title',
            color=RColor.light_purple
        )
    }
    USING_TRANSLATION = {
        0: 'minecraft:overworld',
        -1: 'minecraft:the_nether',
        1: 'minecraft:the_end'
    }
    COMMAND_TRANSLATION = {
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
