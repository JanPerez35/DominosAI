class PerformanceTracker:
    def __init__(self):
        self.games_played = 0
        self.TeamMode = False
        self.human_wins = 0
        self.team1_wins = 0
        self.team2_wins = 0
        self.ai_wins = 0
        self.ties = 0
        self.human_scores = []
        self.ai_scores = []
        self.team1_scores = []
        self.team2_scores = []

    def update_tracker(self, winner, human_score, ai_score, TeamMode, Team1_score, Team2_score):
        self.TeamMode = TeamMode

        if self.TeamMode:
            self.games_played += 1

            if winner in [0,2]:
                self.team1_wins +=1
            if winner == 1:
                self.team2_wins +=1
            if winner == -1:
                self.ties +=1 

            self.team1_scores.append(Team1_score)
            self.team2_scores.append(Team2_score)
        else:            
            self.games_played += 1

            if winner == 0:
                self.human_wins +=1
            if winner == 1:
                self.ai_wins +=1
            if winner == -1:
                self.ties +=1 

            # Adds all the scores
            self.human_scores.append(human_score)
            self.ai_scores.append(ai_score)

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
            print(f"Average Team 1 Score: {sum(self.human_scores)/len(self.human_scores):.2f}")
            print(f"Average Team 2 Score: {sum(self.ai_scores)/len(self.ai_scores):.2f}")
        else:
            print("\n--- Performance Report ---")
            print(f"Games Played: {self.games_played}")
            print(f"Human Wins: {self.human_wins}")
            print(f"AI Wins: {self.ai_wins}")
            print(f"Ties: {self.ties}")
            print(f"Win percentage for Humans: {(self.human_wins / self.games_played) * 100:.2f}%")
            print(f"Win percentage for AI: {(self.ai_wins / self.games_played) * 100:.2f}%")
            print(f"Average Human Score: {sum(self.human_scores)/len(self.human_scores):.2f}")
            print(f"Average AI Score: {sum(self.ai_scores)/len(self.ai_scores):.2f}")

