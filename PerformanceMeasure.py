
class PerformanceTracker:
    def __init__(self):
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

    #Prints the performance measures
    def report(self):
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


