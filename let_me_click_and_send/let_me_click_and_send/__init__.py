from typing import List

from mcdreforged.api.rtext import *
from mcdreforged.api.command import Literal, Requirements
from mcdreforged.api.types import PluginServerInterface, PlayerCommandSource

dismissed_players: List[str]


def get_message() -> RTextList:
    return RTextList(
        "-----------------------------------\n",
        RTextMCDRTranslation("let_me_click_and_send.message.main")
        .set_color(RColor.aqua),
        RTextMCDRTranslation("let_me_click_and_send.message.main.name")
        .set_color(RColor.gold)
        .set_styles(RStyle.underlined),
        "\n",
        RTextMCDRTranslation("let_me_click_and_send.download.github")
        .set_color(RColor.green)
        .set_click_event(
            RAction.open_url,
            "https://github.com/Fallen-Breath/LetMeClickAndSend"
        )
        .set_hover_text(
            RTextMCDRTranslation("let_me_click_and_send.download.hover")
        ),
        " ",
        RTextMCDRTranslation("let_me_click_and_send.download.curseforge")
        .set_color(RColor.green)
        .set_click_event(
            RAction.open_url,
            "https://www.curseforge.com/minecraft/"
            "mc-mods/let-me-click-and-send"
        )
        .set_hover_text(
            RTextMCDRTranslation("let_me_click_and_send.download.hover")
        ),
        " ",
        RTextMCDRTranslation("let_me_click_and_send.download.modrinth")
        .set_color(RColor.green)
        .set_click_event(
            RAction.open_url,
            "https://modrinth.com/mod/letmeclickandsend"
        )
        .set_hover_text(
            RTextMCDRTranslation("let_me_click_and_send.download.hover")
        ),
        "\n",
        RTextMCDRTranslation("let_me_click_and_send.message.dismiss")
        .set_color(RColor.green)
        .set_hover_text(
            RTextMCDRTranslation(
                "let_me_click_and_send.message.dismiss.hover",
            )
        )
        .set_click_event(RAction.run_command, "!!letmeclickandsend dismiss"),
        "\n",
        "-----------------------------------",
    )


def on_load(server: PluginServerInterface, old):
    global dismissed_players
    dismissed_players = server.load_config_simple(
        "dismiss.json",
        default_config={"players": []},
        echo_in_console=False
    )["players"]

    def command_dismiss(src: PlayerCommandSource):
        global dismissed_players
        if src.player not in dismissed_players:
            dismissed_players.append(src.player)
            server.save_config_simple(
                {"players": dismissed_players},
                "dismiss.json"
            )
            src.reply(
                RTextMCDRTranslation(
                    "let_me_click_and_send.message.dismiss.success"
                )
                .set_color(RColor.green)
            )
        else:
            src.reply(
                RTextMCDRTranslation(
                    "let_me_click_and_send.message.dismiss.failed"
                )
                .set_color(RColor.red)
            )

    server.register_command(
        Literal("!!letmeclickandsend")
        .requires(Requirements.is_player())
        .then(
            Literal("show")
            .runs(lambda src: src.reply(get_message()))
        ).then(
            Literal("dismiss")
            .runs(command_dismiss)
        )
    )


def on_player_joined(server: PluginServerInterface, player: str, info):
    if player not in dismissed_players:
        server.tell(player, get_message())
