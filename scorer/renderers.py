# displays game state
from abc import ABC, abstractmethod
from itertools import zip_longest

from scorer.models import GameModel
from tabulate import tabulate

class Renderer(ABC):
    @staticmethod
    @abstractmethod
    def render(model: GameModel):
        """Must be implemented by concrete class"""


class ConsoleRenderer(Renderer):
    @staticmethod
    def render(model: GameModel):
        ledger_rows = list(zip_longest(*model.ledgers, fillvalue=None))
        line_separator = ['-' * len(p.name) for p in model.players] if ledger_rows else []
        totals_rows = [p.current_score for p in model.players]
        display_table = [*ledger_rows, line_separator, totals_rows]
        player_names = [p.name for p in model.players]
        print(tabulate(display_table, player_names, tablefmt="orgtbl"))

