# example usage that the frontend would need to extend

"""
from scorer.models import Player, GameLibrary, GameModel
from scorer.renderers import Renderer, ConsoleRenderer
from scorer.controllers import ConsoleController


if __name__ == "__main__":
    model = GameLibrary.SETBACK(5)
    model.add_player('Alice')
    model.add_player('Bob')
    renderer = ConsoleRenderer()
    controller = ConsoleController(model, renderer)
    controller.run()
"""