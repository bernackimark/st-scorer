from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum


@dataclass
class Player:
    name: str
    ledger: list[int | None] = field(default_factory=lambda: [None])

    @property
    def current_score(self) -> int:
        return sum([score for score in self.ledger if score is not None])


@dataclass
class GameModel(ABC):
    game_over_score: int
    has_game_started: bool = False
    move_history: list[tuple[int, int]] = field(default_factory=list)  # store (player_index, points)  # TODO: player_idx may be unreliable if someone leaves the game
    location: tuple[float, float] = None
    players: list[Player] = field(default_factory=list)

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def is_game_over(self) -> bool:
        pass

    @property
    @abstractmethod
    def winner_name_and_score(self) -> tuple[str, int] | None:
        pass

    @property
    def current_scores(self) -> list[int]:
        return [p.current_score for p in self.players]

    @property
    def ledgers(self) -> list[list[int]]:
        return [p.ledger for p in self.players]

    @property
    def max_ledger_length(self) -> int:
        return max(len(p.ledger) for p in self.players) if len(self.players) else 0

    @property
    def player_current_scores(self) -> dict[str: list[int]]:
        return {p.name: p.current_score for p in self.players}

    @property
    def player_ledger_dict(self) -> dict[str: list[int]]:
        return {p.name: p.ledger for p in self.players}

    @property
    def player_names(self) -> list[str]:
        return [p.name for p in self.players]

    def add_player(self, player_name: str) -> None:
        """Player name must not exist in current game, else error. In a new game, the ledger will be [None].
        If game is in-flight, ledger will be [None] * the number of rounds already transpired."""
        if player_name in {p.name for p in self.players}:
            raise ValueError(f"A player named {player_name} already exists")
        new_player_ledger = [None] * max(self.max_ledger_length, 1)
        new_player = Player(name=player_name, ledger=new_player_ledger)
        self.players.append(new_player)

    def remove_player(self, player_name: str) -> None:
        if len(self.players) == 1:
            raise ValueError("You can't remove the game's only player")
        if player_idx := next((idx for idx, p in enumerate(self.players) if p.name == player_name), None) is None:
            raise ValueError("That player doesn't exist in this game")
        del self.players[player_idx]
        print('Deleted player')

    @abstractmethod
    def add_score(self, *args, **kwargs) -> None:
        pass

    def rollback_move(self):
        if not self.move_history:
            return
        last_move_p_idx, _ = self.move_history.pop()
        self.players[last_move_p_idx].ledger.pop()


RULES = {
    'non_null': lambda ledgers: any(_ for _ in ledgers),
    # same indices of last non-None scores? [3, None] & [1] is True as their last rounds played is both idx 0
    'even_score_cnt': lambda ledgers: len(set([max([idx for idx, score in enumerate(ledger) if score is not None] or [-1])
                                               for ledger in ledgers])) == 1,
    'gte_thresh': lambda totals, game_over_score: any(current_score >= game_over_score for current_score in totals),
    'tie_max': lambda totals: sorted(totals, reverse=True)[0] == sorted(totals, reverse=True)[1] if len(totals) > 1 else False
}

class Setback(GameModel):
    name = 'Setback'

    @property
    def is_game_over(self) -> bool:
        return RULES['non_null'](self.current_scores) and RULES['even_score_cnt'](self.ledgers) and \
               RULES['gte_thresh'](self.current_scores, self.game_over_score) and not RULES['tie_max'](self.current_scores)

    @property
    def winner_name_and_score(self) -> tuple[str, int] | None:
        if not self.is_game_over:
            return None
        winner_name = max(self.player_current_scores, key=self.player_current_scores.get)
        winner_score = self.player_current_scores[winner_name]
        return winner_name, winner_score
        # TODO: this doesn't handle ties

    def add_score(self, player_idx: int, points: int):
        """Update score and record the move history."""
        self.players[player_idx].ledger.append(points)
        self.move_history.append((player_idx, points))  # Save move


class Skyjo(GameModel):
    name = 'Skyjo'

    @property
    def is_game_over(self) -> bool:
        return RULES['non_null'](self.current_scores) and RULES['even_score_cnt'](self.ledgers) and \
               RULES['gte_thresh'](self.current_scores, self.game_over_score)

    @property
    def winner_name_and_score(self) -> tuple[str, int] | None:
        if not self.is_game_over:
            return None
        winner_name = min(self.player_current_scores, key=self.player_current_scores.get)
        winner_score = self.player_current_scores[winner_name]
        return winner_name, winner_score
        # TODO: this doesn't handle ties

    def add_score(self, player_idx: int, points: int):
        """Update score and record the move history."""
        self.players[player_idx].ledger.append(points)
        self.move_history.append((player_idx, points))  # Save move


class GameLibrary(Enum):
    SETBACK = Setback
    SKYJO = Skyjo

    def __call__(self, *args, **kwargs):
        return self.value(*args, **kwargs)  # call the stored function/class object
