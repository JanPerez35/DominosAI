import random
from collections import deque
import tkinter as tk
from tkinter import messagebox
from PerformanceMeasure import PerformanceTracker #importing the performance tracker
import copy
import pygame
import sys


'''
Okay so this mode is under construction. 4 Players 4AI against each other.

'''

class DominoGame:
    def __init__(self,team_mode):
        self.tiles = [(i, j) for i in range(7) for j in range(i, 7)]
        random.shuffle(self.tiles)
        self.players = [self.tiles[i*7:(i+1)*7] for i in range(4)]
        self.stock = self.tiles[28:]
        self.board = deque()
        self.board_owners = deque()  # To track who placed each tile
        self.current_player = 0
        self.passes = 0
        self.team_mode = team_mode
        for i, hand in enumerate(self.players):
            if (6, 6) in hand:
                self.current_player = (i + 1) % 4
                hand.remove((6, 6))  # Remove from hand
                self.board.append((6, 6))  # Place it on the board
                self.board_owners.append(i)  # Track who played it
                break


    def is_valid_move(self, tile, end):
        return end in tile

    def get_valid_moves(self, hand):
        if not self.board:
            return hand
        left, right = self.board[0][0], self.board[-1][1]
        return [t for t in hand if self.is_valid_move(t, left) or self.is_valid_move(t, right)]

    def draw_from_stock(self, player):
        if self.stock:
            drawn_tile = self.stock.pop()
            self.players[player].append(drawn_tile)
            return drawn_tile
        return None

    def play_tile(self, player, tile):
        if not self.board:
            self.board.append(tile)
            self.board_owners.append(player)
        else:
            left, right = self.board[0][0], self.board[-1][1]
            if self.is_valid_move(tile, left):
                self.board.appendleft(tile if tile[1] == left else (tile[1], tile[0]))
                self.board_owners.appendleft(player)
            elif self.is_valid_move(tile, right):
                self.board.append(tile if tile[0] == right else (tile[1], tile[0]))
                self.board_owners.append(player)
            else:
                raise ValueError("Invalid move")
        self.players[player].remove(tile)
        self.passes = 0

    def pass_turn(self):
        self.passes += 1

    def is_game_over(self):
        return any(len(p) == 0 for p in self.players) or self.passes >= 4

    def get_winner(self):
        if not self.team_mode:
            # Free-for-all winner: lowest pip count
            player_scores = [(i, sum(tile[0] + tile[1] for tile in hand)) for i, hand in enumerate(self.players)]
            player_scores.sort(key=lambda x: x[1])
            lowest_score = player_scores[0][1]
            tied_players = [i for i, score in player_scores if score == lowest_score]
            return -1 if len(tied_players) > 1 else player_scores[0][0]
        else:
            # Team mode: teams are (0,2) vs (1,3)
            team0 = sum(a + b for i in (0, 2) for a, b in self.players[i])
            team1 = sum(a + b for i in (1, 3) for a, b in self.players[i])
            if team0 < team1:
                return "Team 1"
            elif team1 < team0:
                return "Team 2"
            else:
                return -1

# ------------ GUI ------------

class DominoGUI:
    def __init__(self, root,team_mode, tracker):
        self.root = root
        self.root.title("Domino - 4 AI Players")
        self.game = DominoGame(team_mode)
        self.tracker = PerformanceTracker() #tracker added

        if team_mode:
            self.player_colors = ['blue', 'red', 'blue', 'red']
        else:
            self.player_colors = ['blue', 'red', 'green', 'purple']
        self.game_over = False

        # Layout
        self.board_frame = tk.Frame(root)
        self.board_frame.pack(pady=10)

        self.canvas_width = 1000
        self.canvas_height = 300

        self.canvas_scrollbar = tk.Scrollbar(self.board_frame, orient=tk.HORIZONTAL)
        self.canvas_scrollbar.pack(fill=tk.X)

        self.board_canvas = tk.Canvas(self.board_frame, width=self.canvas_width, height=self.canvas_height,
                                      bg='light gray',xscrollcommand=self.canvas_scrollbar.set,
    scrollregion=(0, 0, 5000, 300)
                                      )
        self.board_canvas.pack(side=tk.TOP, fill=tk.X)
        self.canvas_scrollbar.config(command=self.board_canvas.xview)
        self.scroll_button_frame = tk.Frame(self.board_frame)
        self.scroll_button_frame.pack(pady=5)

        self.scroll_left_btn = tk.Button(self.scroll_button_frame, text=" Scroll Left", command=self.scroll_left)
        self.scroll_left_btn.pack(side=tk.LEFT, padx=5)

        self.scroll_right_btn = tk.Button(self.scroll_button_frame, text="Scroll Right ", command=self.scroll_right)
        self.scroll_right_btn.pack(side=tk.LEFT, padx=5)

        self.hand_frame = tk.Frame(root)
        self.hand_frame.pack(pady=10)

        self.info_frame = tk.Frame(root)
        self.info_frame.pack()

        self.controls_frame = tk.Frame(root)
        self.controls_frame.pack(pady=10)

        #Leyend
        self.legend_frame = tk.Frame(root)
        self.legend_frame.pack(pady=5)

        self.legend_label = tk.Label(self.legend_frame, text="Legend:")
        self.legend_label.pack(side=tk.LEFT)

        if team_mode:
            legend_info = [
                ("AI 0 (Team 0)" if team_mode else "AI 0", self.player_colors[0]),
                ("AI 1 (Team 1)" if team_mode else "AI 1", self.player_colors[1]),
                ("AI 2 (Team 0)" if team_mode else "AI 2", self.player_colors[2]),
                ("AI 3 (Team 1)" if team_mode else "AI 3", self.player_colors[3]),
            ]
        else:
            legend_info = [
                ("AI 0", 'blue'),
                ("AI 1", 'red'),
                ("AI 2", 'green'),
                ("AI 3", 'purple'),
            ]

        for name, color in legend_info:
            label = tk.Label(self.legend_frame, text=f"{name}", fg=color, font=("Arial", 10, 'bold'))
            label.pack(side=tk.LEFT, padx=5)

        # Buttons

        self.music_on = True
        self.music_button = tk.Button(self.controls_frame, text="Mute Music", command=self.toggle_music)
        self.music_button.pack(side=tk.LEFT, padx=5)

        # Labels
        self.status_label = tk.Label(self.info_frame, text="")
        self.status_label.pack(side=tk.LEFT, padx=10)

        self.ai_labels = [tk.Label(self.info_frame, text=f"AI {i} has 7 tiles") for i in range(1, 4)]
        for label in self.ai_labels:
            label.pack(side=tk.RIGHT, padx=5)

        self.draw_board()
        self.status_label.config(
                text=f"AI {self.game.current_player} starts with (6|6)"
            )
        self.root.after(1000, self.ai_turn)



    def scroll_left(self):
        current_x = self.board_canvas.canvasx(0)
        self.board_canvas.xview_scroll(-1, "units")  # Scroll left by one unit

    def scroll_right(self):
        current_x = self.board_canvas.canvasx(0)
        self.board_canvas.xview_scroll(1, "units")  # Scroll right by one unit


    def toggle_music(self):
        if self.music_on:
            pygame.mixer.music.pause()
            self.music_button.config(text="Play Music")
        else:
            pygame.mixer.music.unpause()
            self.music_button.config(text="Mute Music")
        self.music_on = not self.music_on

    def draw_board(self):
        self.board_canvas.delete("all")
        x, y = 500, 150  # Start position
        tile_positions = []

        for i, tile in enumerate(self.game.board):
            owner = self.game.board_owners[i]
            if self.game.team_mode:
                team_colors = {0: 'blue', 1: 'red', 2: 'blue', 3: 'red'}
                color = team_colors[owner]
            else:
                color = self.player_colors[owner]
            is_double = tile[0] == tile[1]

            if is_double:
                # Vertical tile
                self.board_canvas.create_rectangle(x, y, x + 30, y + 60, fill='white', outline=color, width=2)
                self.board_canvas.create_text(x + 15, y + 30, text=f"{tile[0]}\n|\n{tile[1]}", fill=color,
                                              font=('Courier', 10, 'bold'))
                tile_positions.append((x, 60))
                x += 40
            else:
                # Horizontal tile
                self.board_canvas.create_rectangle(x, y, x + 60, y + 30, fill='white', outline=color, width=2)
                self.board_canvas.create_text(x + 30, y + 15, text=f"{tile[0]}|{tile[1]}", fill=color,
                                              font=('Courier', 12, 'bold'))
                tile_positions.append((x, 60))
                x += 70

            self.board_canvas.config(scrollregion=(0,0, max(x+100,1000), 300))
            if tile_positions:
                latest_x = tile_positions[-1][0]
                canvas_view_x = max(latest_x - self.canvas_width // 2, 0)
                self.board_canvas.xview_moveto(canvas_view_x / (max(x + 100, 1000)))

    def after_move(self):
        self.draw_board()
        self.update_ai_tile_counts()

        if self.game.is_game_over():
            self.end_game()

    def ai_turn(self):
        # end immediately if the game’s done
        if self.game.is_game_over():
            self.end_game()
            return

        ai_index = self.game.current_player
        hand = self.game.players[ai_index]
        valid = self.game.get_valid_moves(hand)

        # draw until we have a move or run out
        while not valid and self.game.stock:
            self.game.draw_from_stock(ai_index)
            valid = self.game.get_valid_moves(self.game.players[ai_index])

        # play or pass
        if valid:
            move = self.monte_carlo_ai_move(ai_index)
            self.game.play_tile(ai_index, move)
            self.status_label.config(text=f"AI {ai_index} played {move}")
        else:
            self.game.pass_turn()
            self.status_label.config(text=f"AI {ai_index} passed")

        # advance turn, redraw
        self.game.current_player = (ai_index + 1) % 4
        self.draw_board()
        self.update_ai_tile_counts()

        # schedule **only** one next call, after 2 s
        if self.game.is_game_over():
            self.end_game()
        else:
            self.root.after(500, self.ai_turn)

    def monte_carlo_ai_move(self, player_index, simulations=25):
        hand = self.game.players[player_index]
        valid_moves = self.game.get_valid_moves(hand)
        if not valid_moves:
            return None

        move_scores = {}
        for move in valid_moves:
            total_score = 0
            for _ in range(simulations):
                sim_game = copy.deepcopy(self.game)
                try:
                    sim_game.play_tile(player_index, move)
                except:
                    continue
                winner = self.simulate_random_playout(sim_game)
                total_score += 1 if winner == player_index else 0
            move_scores[move] = total_score / simulations

        best_move = max(move_scores, key=move_scores.get)
        return best_move

    def simulate_random_playout(self, sim_game):
        current = sim_game.current_player
        while not sim_game.is_game_over():
            hand = sim_game.players[current]
            valid = sim_game.get_valid_moves(hand)
            if valid:
                sim_game.play_tile(current, random.choice(valid))
            elif sim_game.stock:
                sim_game.draw_from_stock(current)
            else:
                sim_game.pass_turn()
            current = (current + 1) % 4
        return sim_game.get_winner()

    def update_ai_tile_counts(self):
        for i in range(1, 4):
            self.ai_labels[i - 1].config(text=f"AI {i} has {len(self.game.players[i])} tiles")
    
    '''
    Starts a new game.
    '''

    def start_new_game(self,teamMode):
        # Re-initialize game state
        self.game = DominoGame(self.game.team_mode)
        self.game_over = False

        # Clear and redraw board
        self.board_canvas.delete("all")
        self.draw_board()

        # Reset AI tile count labels
        self.update_ai_tile_counts()

        # Update status label
        self.status_label.config(text=f"AI {self.game.current_player} starts with (6|6)!")

        # Start the first AI turn after a short delay
        self.root.after(1000, self.ai_turn)

    def end_game(self):
        if self.game_over:
            return

        self.game_over = True
        winner = self.game.get_winner()

        player_scores = [
            (i, sum(t[0] + t[1] for t in hand), hand)
            for i, hand in enumerate(self.game.players)
        ]

        if self.game.team_mode:
            team_0_score = sum(score for i, score, _ in player_scores if i in [0, 2])
            team_1_score = sum(score for i, score, _ in player_scores if i in [1, 3])

            #team_names = ["Team 0 (Players 0 & 2)", "Team 1 (Players 1 & 3)"]
            if winner == -1:
                msg = "🤝 It's a tie between both teams!"
            else:
                msg = f"🏆 {winner} wins!"

            messagebox.showinfo("Game Over", msg)
            #Performance Tracking 
            self.tracker.update_tracker_team_mode(winner, True, team_0_score, team_1_score)
            self.tracker.report()
        else:
            if winner == -1:
                msg = "🤝 It's a tie!"
            else:
                msg = f"🤖 AI {winner} wins!"
                # build final scores
                scores = [sum(a + b for a, b in hand) for hand in self.game.players]
                if self.game.team_mode:
                    # show both teams' pip totals
                    t0 = scores[0] + scores[2]
                    t1 = scores[1] + scores[3]
                    msg += f"\n\nTeam 0 total: {t0}\nTeam 1 total: {t1}"
                else:
                    # list each AI’s score
                    lines = "\n".join(f"AI {i}: {s} pips" for i, s in enumerate(scores))
                    msg += "\n\nFinal Scores:\n" + lines

            messagebox.showinfo("Game Over", msg)

            tracker_scores = [score for i, score, hand in player_scores]
            #Performance Tracking 
            self.tracker.update_tracker_4_player(winner, tracker_scores[0], tracker_scores[1], tracker_scores[2], tracker_scores[3], "4ai")
            self.tracker.report()

        #Play again option
        play_again = messagebox.askyesno(
            title="Play again?",
            message="Would you like to play again?"
        )
        if play_again:
            self.start_new_game(team_mode)
        else:
            self.root.quit()

# ------------ Run the App ------------

if __name__ == "__main__":
    team_mode = "--team" in sys.argv
    pygame.mixer.init()
    pygame.mixer.music.load("BGM.mp3")
    pygame.mixer.music.play(-1)

    tracker = PerformanceTracker() #tracker added   
    root = tk.Tk()
   
    app = DominoGUI(root, team_mode, tracker)
    root.mainloop()
