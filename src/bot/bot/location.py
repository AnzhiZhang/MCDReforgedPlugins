from typing import List, Dict, Any

from mcdreforged.api.rtext import RTextTranslation

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
        return DIMENSION.USING_TRANSLATION[self.dimension]

    @property
    def display_dimension(self) -> RTextTranslation:
        """
        Get RTextTranslation dimension to display.
        :return: RTextTranslation.
        """
        return DIMENSION.DISPLAY_TRANSLATION[self.dimension]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Location':
        return Location(data['position'], data['facing'], data['dimension'])

    def __str__(self):
        return self.__class__.__name__ + {
            'position': self.position,
            'facing': self.facing,
            'dimension': self.dimension
        }.__str__()
