# handles user input
from abc import ABC, abstractmethod
from dataclasses import dataclass

from scorer.models import GameModel
from scorer.renderers import Renderer


@dataclass
class Controller(ABC):
    model: GameModel
    renderer: Renderer

    @abstractmethod
    def run(self):
        """Runs the game loop"""


@dataclass
class ConsoleController(Controller):
    def run(self):
        """Runs the game loop with manual score input."""
        if not self.model.players:
            print('You must add players to play')

        self.model.has_game_started = True
        print("Starting the game...\n")
        while not self.model.is_game_over:
            self.renderer.render(self.model)
            player_id = input("Select a player id (or 'x' to undo last entry): ")
            if player_id == 'x':
                self.model.rollback_move()
            else:
                player_id = int(player_id)
                points = int(input(f"Enter points: "))
                self.model.add_score(player_idx=player_id, points=points)
                # self.engine.process_input(player_id=player_id, points=points)

        print("\nFinal Scores:")
        self.renderer.render(self.model)
