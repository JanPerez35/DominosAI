import random
from collections import deque
import tkinter as tk
from tkinter import messagebox
import copy
import pygame
import sys

'''
Okay so this mode is under construction. It currently has 3 AI against a player but
the order is not clear of who goes when. There is not a feature to have teams or have multiple
human players yet. Also the window is kinda hard to view when there are this many players

'''

class DominoGame:
    def __init__(self, team_mode):
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
        # Calculate total pip count for each player
        if self.team_mode:
            team_0_score = sum(tile[0] + tile[1] for i in [0, 2] for tile in self.players[i])
            team_1_score = sum(tile[0] + tile[1] for i in [1, 3] for tile in self.players[i])
            if team_0_score < team_1_score:
                return "Team A"
            elif team_1_score < team_0_score:
                return "Team B"
            else:
                return -1  # Tie
        else:
            player_scores = []
            for i, hand in enumerate(self.players):
                total = sum(tile[0] + tile[1] for tile in hand)
                player_scores.append((i, total))

            # Sort players by score (lowest total wins)
            player_scores.sort(key=lambda x: x[1])

            # Check for a tie (two or more players with the same lowest score)
            lowest_score = player_scores[0][1]
            tied_players = [i for i, score in player_scores if score == lowest_score]

            if len(tied_players) > 1:
                 return -1  # Tie
            else:
                 return player_scores[0][0]  # Index of the winning player

# ------------ GUI ------------

class DominoGUI:
    def __init__(self, root, team_mode):
        self.root = root
        self.root.title("Domino - 4 Players (You vs 3 AI)")
        self.game = DominoGame(team_mode)

        if team_mode:
            self.player_colors = ['blue', 'red', 'blue', 'red']
        else:
            self.player_colors = ['blue', 'red', 'green', 'purple']

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
                ("Player 1 (Team A)" if team_mode else "AI 0", self.player_colors[0]),
                ("AI 1 (Team B)" if team_mode else "AI 1", self.player_colors[1]),
                ("AI  (Team A)" if team_mode else "AI 2", self.player_colors[2]),
                ("AI 3 (Team B)" if team_mode else "AI 3", self.player_colors[3]),
            ]
        else:
            legend_info = [
                ("Player 1", 'blue'),
                ("AI 1", 'red'),
                ("AI 2", 'green'),
                ("AI 3", 'purple'),
            ]

        for name, color in legend_info:
            label = tk.Label(self.legend_frame, text=f"{name}", fg=color, font=("Arial", 10, 'bold'))
            label.pack(side=tk.LEFT, padx=5)

        # Buttons
        self.pass_button = tk.Button(self.controls_frame, text="Pass Turn", command=self.pass_turn)
        self.pass_button.pack(side=tk.LEFT, padx=5)

        self.draw_button = tk.Button(self.controls_frame, text="Draw Tile", command=self.draw_tile)
        self.draw_button.pack(side=tk.LEFT, padx=5)

        self.music_on = True
        self.music_button = tk.Button(self.controls_frame, text="Mute Music", command=self.toggle_music)
        self.music_button.pack(side=tk.LEFT, padx=5)

        # Labels
        self.status_label = tk.Label(self.info_frame, text="Your turn!")
        self.status_label.pack(side=tk.LEFT, padx=10)

        self.ai_labels = [tk.Label(self.info_frame, text=f"AI {i} has 7 tiles") for i in range(1, 4)]
        for label in self.ai_labels:
            label.pack(side=tk.RIGHT, padx=5)

        self.draw_board()
        self.draw_hand()
        if self.game.current_player != 0:
            self.status_label.config(
                text=f"AI {self.game.current_player} starts with (6|6)"
            )
            self.root.after(1000, self.ai_turn)
        else:
            self.status_label.config(text="You start with (6|6)!")


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

    def draw_hand(self):
        for widget in self.hand_frame.winfo_children():
            widget.destroy()
        hand = self.game.players[0]
        valid_moves = self.game.get_valid_moves(hand)
        for tile in hand:
            tile_str = f"[{tile[0]}|{tile[1]}]"
            btn = tk.Button(self.hand_frame, text=tile_str, font=('Courier', 12), relief='raised', fg='blue',
                            state=tk.NORMAL if tile in valid_moves else tk.DISABLED,
                            command=lambda t=tile: self.play_tile(t))
            btn.pack(side=tk.LEFT, padx=4)

    def play_tile(self, tile):
        try:
            self.game.play_tile(0, tile)
            self.game.current_player = (self.game.current_player + 1) % 4  # <-- Fix is here
            self.after_move()
        except Exception as e:
            messagebox.showerror("Invalid Move", str(e))

    def pass_turn(self):
        self.game.pass_turn()
        self.game.current_player = (self.game.current_player + 1) % 4
        self.after_move()

    def draw_tile(self):
        tile = self.game.draw_from_stock(0)
        if tile:
            self.status_label.config(text=f"You drew {tile}")
        else:
            self.status_label.config(text="Stock is empty")
        self.draw_hand()

    def after_move(self):
        self.draw_board()
        self.draw_hand()
        self.update_ai_tile_counts()

        if self.game.is_game_over():
            self.end_game()
        else:
            self.root.after(500, self.ai_turn)

    def ai_turn(self):
        if self.game.current_player == 0 or self.game.is_game_over():
            if self.game.is_game_over():
                self.end_game()
            else:
                self.status_label.config(text="Your turn!")
                self.draw_hand()
            return

        cp = self.game.current_player
        hand = self.game.players[cp]
        valid_moves = self.game.get_valid_moves(hand)

        while not valid_moves and self.game.stock:
            drawn = self.game.draw_from_stock(cp) # Se borra pq no se usa???
            valid_moves = self.game.get_valid_moves(self.game.players[cp])

        move = self.monte_carlo_ai_move(cp, simulations=25)
        if move:
            self.game.play_tile(cp, move)
            self.status_label.config(text=f"AI {cp} played {move}")
        else:
            self.game.pass_turn()
            self.status_label.config(text=f"AI {cp} passed")

        self.draw_board()
        self.update_ai_tile_counts()
        self.game.current_player = (self.game.current_player + 1) % 4

        self.root.after(1000, self.ai_turn) # delay between AI turns


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

    def end_game(self):
        winner = self.game.get_winner()

        # Optional: Print all players' remaining points
        player_scores = [
            (i, sum(t[0] + t[1] for t in hand), hand)
            for i, hand in enumerate(self.game.players)
        ]

        if self.game.team_mode:
            # Team-based scoring
            team_0_score = sum(score for i, score, _ in player_scores if i in [0, 2])
            team_1_score = sum(score for i, score, _ in player_scores if i in [1, 3])

            team_lines = "\n".join(
                f"Player {i} ({'You' if i ==0  else 'AI'}): {score} points | Tiles: {hand}"
                for i, score, hand in player_scores
            )
            msg = "🤝 It's a tie!" if winner == -1 else f"🎉 {winner} wins!"
            msg += f"\n\nTeam A score: {team_0_score}\nTeam B score: {team_1_score}"
            msg += "\n\nFinal Player Scores:\n" + team_lines

            messagebox.showinfo("Game Over", msg)
            self.root.quit()
        else:
          # Free-for-all scoring
            score_lines = "\n".join(
                f"Player {i} ({'You' if i == 0 else 'AI'}): {score} points | Tiles: {hand}"
                for i, score, hand in player_scores
            )
            print("Final scores (lower is better):")
            for i, score, hand in player_scores:
                print(f"Player {i}: {score} points")

            if winner == 0:
                msg = "🎉 You win!"
            elif winner == -1:
                msg = "🤝 It's a tie!"
            else:
                msg = f"🤖 AI {winner} wins!"

            msg += "\nFinal Scores:\n" + score_lines

            messagebox.showinfo("Game Over", msg)
            self.root.quit()

# ------------ Run the App ------------

if __name__ == "__main__":
    team_mode = "--team" in sys.argv
    pygame.mixer.init()
    pygame.mixer.music.load("BGM.mp3")
    pygame.mixer.music.play(-1)

    root = tk.Tk()
    app = DominoGUI(root, team_mode)
    root.mainloop()
