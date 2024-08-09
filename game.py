from objects.team import Team
from objects.shop import Shop
from battle import battle

from utils.team_file_io import import_team, export_team
from utils.helpers import debug, error, warning, success, get_random_id

class Game:
    TURN: int = 1
    TEAM: Team = None
    SHOP: Shop = None
    export: bool = False

    def __init__(self, name: str, export: bool = False):
        self.TEAM = Team(name)
        self.SHOP = Shop(self.TURN, self.TEAM)
        self.export = export

    def play(self):
        team_id = -1
        while self.TEAM.num_wins < 10 and self.TEAM.num_lives > 0:
            # shop phase
            self.SHOP.update(self.TURN)
            self.SHOP.user_turn()

            self.TEAM.full_info()
            if self.export: 
                team_id = export_team(self.TEAM, self.TURN, team_id)

            # battle phase
            # comment out the next three lines to skip battle phase
            temp_team = import_team("opponent", get_random_id(), self.TURN)
            winner = battle(self.TEAM, temp_team)
            self.handle_winner(winner)
            # uncomment this line if skipping battle phase
            # self.TEAM.reset()           # TODO: remove this when testing is over

            self.TURN += 1

        if self.TEAM.num_wins == 10:
            success("You won!")
        else:
            error("You lost!")

        self.TEAM.full_info()

    def handle_winner(self, winner: str):
        if winner == self.TEAM.name:        # team won
            self.TEAM.num_wins += 1
            print(f"  You have {self.TEAM.num_wins} win(s)!")

        elif winner == "":                  # draw
            pass

        else:                               # team lost
            self.TEAM.num_lives -= 1
            print(f"  You have {self.TEAM.num_lives} lives remaining!")
