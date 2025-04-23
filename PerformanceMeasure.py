
class PerformanceTracker:
    """
    Tracks and reports performance statistics for various game modes in a domino game.

    This class maintains statistics such as the number of games played, win counts,
    tie counts, and average scores for individual players or teams across multiple game
    modes. The report method prints a formatted performance summary based on the
    current mode.

    Supported Game Modes:
        - "1v1": One human vs one AI.
        - "2v2": Two humans vs two AIs. Human and AI positions may vary across games.
        - "3v1": Three humans vs one AI.
        - "1v3": One human vs three AIs.
        - Other (not listed in the report but handled internally):
            * "AI vs AI": Two AIs playing against each other.
            * "4 AI": All four players are AIs competing against each other.

    Attributes:
        games_played (int): Total number of games tracked.
        TeamMode (bool): Whether the current game is using team-based scoring.
        player1_wins (int): Wins for player 1.
        player2_wins (int): Wins for player 2.
        player3_wins (int): Wins for player 3.
        player4_wins (int): Wins for player 4.
        team1_wins (int): Wins for team 1 (players 0 & 2).
        team2_wins (int): Wins for team 2 (players 1 & 3).
        ties (int): Number of tied games.
        player1_scores (list[int]): Score history for player 1.
        player2_scores (list[int]): Score history for player 2.
        player3_scores (list[int]): Score history for player 3.
        player4_scores (list[int]): Score history for player 4.
        team1_scores (list[int]): Score history for team 1.
        team2_scores (list[int]): Score history for team 2.
        four_players (bool): Whether the game involves four players.
        game_mode (str | None): Current game mode identifier.
    """

    def __init__(self):
        """
        Initializes the PerformanceTracker with default values for all statistics.
        """
        self.games_played = 0
        self.TeamMode = False
        self.player1_wins = 0
        self.player2_wins = 0
        self.player3_wins = 0
        self.player4_wins = 0
        self.team1_wins = 0
        self.team2_wins = 0        
        self.ties = 0
        self.player1_scores = []
        self.player2_scores = []
        self.player3_scores = []
        self.player4_scores = []
        self.team1_scores = []
        self.team2_scores = []
        self.four_players = False
        self.game_mode = None     

    def update_tracker_2_player(self, winner, player1_score, player2_score, game_mode):
        """
        Updates the tracker for a 2-player (1v1) game.

        Args:
            winner (int): The index of the winning player (0 for player 1, 1 for player 2, -1 for tie).
            player1_score (int): Final score for player 1.
            player2_score (int): Final score for player 2.
            game_mode (str): The current game mode
        """
        self.games_played += 1
        self.game_mode = game_mode

        if winner == 0:
            self.player1_wins +=1
        if winner == 1:
            self.player2_wins +=1
        if winner == -1:
            self.ties +=1 

        # Adds all the scores
        self.player1_scores.append(player1_score)
        self.player2_scores.append(player2_score)

    def update_tracker_team_mode(self, winner, TeamMode, Team1_score, Team2_score):
        """
        Updates the tracker for a team-based game.

        Args:
            winner (str | int): The winning team ("Team 1", "Team 2", or -1 for a tie).
            TeamMode (bool): True if the game is in team mode.
            Team1_score (int): Final score for team 1.
            Team2_score (int): Final score for team 2.
        """
        self.TeamMode = TeamMode        

        if self.TeamMode:
            self.games_played += 1

            if winner == "Team 1":
                self.team1_wins +=1
            if winner == "Team 2":
                self.team2_wins +=1
            if winner == -1:
                self.ties +=1 

            self.team1_scores.append(Team1_score)
            self.team2_scores.append(Team2_score)

    def update_tracker_4_player(self, winner, player1_score, player2_score, player3_score, player4_score, game_mode):
        """
        Updates the tracker for a 4-player game (2v2, 3v1, or 1v3).

        Args:
            winner (int): Index of the winning player (0–3) or -1 for tie.
            player1_score (int): Score for player 1.
            player2_score (int): Score for player 2.
            player3_score (int): Score for player 3.
            player4_score (int): Score for player 4.
            game_mode (str): The current game mode
        """

        self.games_played += 1
        self.four_players = True
        self.game_mode = game_mode

        if winner == 0:
            self.player1_wins +=1
        if winner == 1:
            self.player2_wins +=1
        if winner == 2:
            self.player3_wins +=1
        if winner == 3:
            self.player4_wins +=1
        if winner == -1:
            self.ties +=1 

        # Adds all the scores
        self.player1_scores.append(player1_score)
        self.player2_scores.append(player2_score)
        self.player3_scores.append(player3_score)
        self.player4_scores.append(player4_score)
    
    def report(self):
        """
        Prints a performance summary based on the current game mode.

        Includes stats like win counts, win percentages, average scores,
        and ties. Adapts to team mode or free-for-all formats.

        Game modes:
            - 1v1: 1 Human vs 1 AI
            - 2v2: 2 Humans vs 2 AIs (team configuration varies)
            - 3v1: 3 Humans vs 1 AI
            - 1v3: 1 Human vs 3 AIs
            - Others (not listed): 2 AIs vs each other, or 4 AIs free-for-all
        """
        if self.TeamMode:
            print("\n--- Performance Report ---")
            print(f"Games Played: {self.games_played}")
            print(f"Team 1 Wins: {self.team1_wins}")
            print(f"Team 2 Wins: {self.team2_wins}")
            print(f"Ties: {self.ties}")
            print(f"Win percentage for Team 1: {self.team1_wins/self.games_played * 100:.2f}%")
            print(f"Win percentage for Team 2: {self.team2_wins/self.games_played * 100:.2f}%")
            print(f"Average Team 1 Score: {sum(self.team1_scores)/len(self.team1_scores):.2f}")
            print(f"Average Team 2 Score: {sum(self.team2_scores)/len(self.team2_scores):.2f}")
        else:
            if self.four_players:
                print("\n--- Performance Report ---") 
                print(f"Games Played: {self.games_played}")
                if self.game_mode == "2v2":     
                    print(f"Player 1 Wins: {self.player1_wins}")
                    print(f"AI 1 Wins: {self.player2_wins}")
                    print(f"Player 2 Wins: {self.player3_wins}")
                    print(f"AI 2 Wins: {self.player4_wins}")
                    print(f"Ties: {self.ties}")
                    print(f"Win percentage for Player 1: {(self.player1_wins / self.games_played) * 100:.2f}%")
                    print(f"Win percentage for AI 1: {(self.player2_wins / self.games_played) * 100:.2f}%")
                    print(f"Win percentage for Player 2: {(self.player3_wins / self.games_played) * 100:.2f}%")
                    print(f"Win percentage for AI 2: {(self.player4_wins / self.games_played) * 100:.2f}%")
                    print(f"Average Player 1 Score: {sum(self.player1_scores)/len(self.player1_scores):.2f}")
                    print(f"Average AI 1 Score: {sum(self.player2_scores)/len(self.player2_scores):.2f}")
                    print(f"Average Player 2 Score: {sum(self.player3_scores)/len(self.player3_scores):.2f}")
                    print(f"Average AI 2 Score: {sum(self.player4_scores)/len(self.player4_scores):.2f}")
                    print(f"Win percentage for Human players: {((self.player1_wins + self.player3_wins) / self.games_played) * 100:.2f}%")
                    print(f"Win percentage for AI: {((self.player2_wins + self.player4_wins) / self.games_played) * 100:.2f}%")
                elif self.game_mode == "3v1":
                    print(f"Player 1 Wins: {self.player1_wins}")
                    print(f"Player 2 Wins: {self.player2_wins}")
                    print(f"Player 3 Wins: {self.player3_wins}")
                    print(f"AI 1 Wins: {self.player4_wins}")
                    print(f"Ties: {self.ties}")
                    print(f"Win percentage for Player 1: {(self.player1_wins / self.games_played) * 100:.2f}%")
                    print(f"Win percentage for Player 2: {(self.player2_wins / self.games_played) * 100:.2f}%")
                    print(f"Win percentage for Player 3: {(self.player3_wins / self.games_played) * 100:.2f}%")
                    print(f"Win percentage for AI 1: {(self.player4_wins / self.games_played) * 100:.2f}%")
                    print(f"Average Player 1 Score: {sum(self.player1_scores)/len(self.player1_scores):.2f}")
                    print(f"Average Player 2 Score: {sum(self.player2_scores)/len(self.player2_scores):.2f}")
                    print(f"Average Player 3 Score: {sum(self.player3_scores)/len(self.player3_scores):.2f}")
                    print(f"Average AI 1 Score: {sum(self.player4_scores)/len(self.player4_scores):.2f}")
                    print(f"Win percentage for Human players: {((self.player1_wins + self.player2_wins + self.player3_wins) / self.games_played) * 100:.2f}%")
                    print(f"Win percentage for AI: {(self.player4_wins / self.games_played) * 100:.2f}%")
                elif self.game_mode == "1v3":
                    print(f"Player 1 Wins: {self.player1_wins}")
                    print(f"AI 1 Wins: {self.player2_wins}")
                    print(f"AI 2 Wins: {self.player3_wins}")
                    print(f"AI 3 Wins: {self.player4_wins}")
                    print(f"Ties: {self.ties}")
                    print(f"Win percentage for Player 1: {(self.player1_wins / self.games_played) * 100:.2f}%")
                    print(f"Win percentage for AI 1: {(self.player2_wins / self.games_played) * 100:.2f}%")
                    print(f"Win percentage for AI 2: {(self.player3_wins / self.games_played) * 100:.2f}%")
                    print(f"Win percentage for AI 3: {(self.player4_wins / self.games_played) * 100:.2f}%")
                    print(f"Average Player 1 Score: {sum(self.player1_scores)/len(self.player1_scores):.2f}")
                    print(f"Average AI 1 Score: {sum(self.player2_scores)/len(self.player2_scores):.2f}")
                    print(f"Average AI 2 Score: {sum(self.player3_scores)/len(self.player3_scores):.2f}")
                    print(f"Average AI 3 Score: {sum(self.player4_scores)/len(self.player4_scores):.2f}")
                    print(f"Win percentage for Human players: {((self.player1_wins / self.games_played)) * 100:.2f}%")
                    print(f"Win percentage for AI: {((self.player2_wins + self.player3_wins + self.player4_wins) / self.games_played) * 100:.2f}%")
                else:
                    print(f"AI 1 Wins: {self.player1_wins}")
                    print(f"AI 2 Wins: {self.player2_wins}")
                    print(f"AI 3 Wins: {self.player3_wins}")
                    print(f"AI 4 Wins: {self.player4_wins}")
                    print(f"Ties: {self.ties}")
                    print(f"Win percentage for AI 1: {(self.player1_wins / self.games_played) * 100:.2f}%")
                    print(f"Win percentage for AI 2: {(self.player2_wins / self.games_played) * 100:.2f}%")
                    print(f"Win percentage for AI 3: {(self.player3_wins / self.games_played) * 100:.2f}%")
                    print(f"Win percentage for AI 4: {(self.player4_wins / self.games_played) * 100:.2f}%")
                    print(f"Average AI 1 Score: {sum(self.player1_scores)/len(self.player1_scores):.2f}")
                    print(f"Average AI 2 Score: {sum(self.player2_scores)/len(self.player2_scores):.2f}")
                    print(f"Average AI 3 Score: {sum(self.player3_scores)/len(self.player3_scores):.2f}")
                    print(f"Average AI 4 Score: {sum(self.player4_scores)/len(self.player4_scores):.2f}")  
            else:
                print("\n--- Performance Report ---")
                print(f"Games Played: {self.games_played}")
                if self.game_mode == "1v1":
                    print(f"Human Wins: {self.player1_wins}")
                    print(f"AI Wins: {self.player2_wins}")
                    print(f"Ties: {self.ties}")
                    print(f"Win percentage for Humans: {(self.player1_wins / self.games_played) * 100:.2f}%")
                    print(f"Win percentage for AI: {(self.player2_wins / self.games_played) * 100:.2f}%")
                    print(f"Average Human Score: {sum(self.player1_scores)/len(self.player1_scores):.2f}")
                    print(f"Average AI Score: {sum(self.player2_scores)/len(self.player2_scores):.2f}")
                else:
                    print(f"AI 1 Wins: {self.player1_wins}")
                    print(f"AI 2 Wins: {self.player2_wins}")
                    print(f"Ties: {self.ties}")
                    print(f"Win percentage for AI 1: {(self.player1_wins / self.games_played) * 100:.2f}%")
                    print(f"Win percentage for AI 2: {(self.player2_wins / self.games_played) * 100:.2f}%")
                    print(f"Average AI 1 Score: {sum(self.player1_scores)/len(self.player1_scores):.2f}")
                    print(f"Average AI 2 Score: {sum(self.player2_scores)/len(self.player2_scores):.2f}")


