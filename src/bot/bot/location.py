from typing import List, Dict, Any

import minecraft_data_api as api
from mcdreforged.api.rtext import RText, RColor

from bot.constants import DIMENSION


class Location:
    def __init__(
            self,
            position: List[float],
            facing: List[float],
            dimension: int
    ):
        self.position = position
        self.facing = facing
        self.dimension = dimension

    @property
    def rounded_position(self) -> List[float]:
        return [round(i, 2) for i in self.position]

    @property
    def rounded_facing(self) -> List[float]:
        return [round(i, 2) for i in self.facing]

    @property
    def str_dimension(self) -> str:
        """
        Get minecraft dimension string.
        :return: str.
        """
        return DIMENSION.STR_TRANSLATION[self.dimension]

    @property
    def display_dimension(self) -> RText:
        """
        Get dimension RText to display.
        :return: RText.
        """
        # get translation
        translation: RText = api.get_dimension_translation_text(self.dimension)

        # set color
        if self.dimension == DIMENSION.OVERWORLD:
            translation.set_color(RColor.green)
        elif self.dimension == DIMENSION.THE_NETHER:
            translation.set_color(RColor.dark_red)
        elif self.dimension == DIMENSION.THE_END:
            translation.set_color(RColor.light_purple)

        # return
        return translation

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Location':
        return Location(data['position'], data['facing'], data['dimension'])

    def __str__(self):
        return self.__class__.__name__ + {
            'position': self.position,
            'facing': self.facing,
            'dimension': self.dimension
        }.__str__()
