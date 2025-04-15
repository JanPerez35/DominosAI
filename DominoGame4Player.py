import random
from collections import deque
import tkinter as tk
from tkinter import messagebox
import copy
import pygame


'''
Okay so this mode is under construction. It currently has 3 AI agaisnt a player but
the order is not clear of who goes when. There is not a feature to have teams or have multiple
human players yet. Also the window is kinda hard to view when there are this many players

'''

class DominoGame:
    def __init__(self):
        self.tiles = [(i, j) for i in range(7) for j in range(i, 7)]
        random.shuffle(self.tiles)
        self.players = [self.tiles[i*7:(i+1)*7] for i in range(4)]
        self.stock = self.tiles[28:]
        self.board = deque()
        self.board_owners = deque()  # To track who placed each tile
        self.current_player = 0
        self.passes = 0

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
        scores = [(i, sum(sum(t) for t in p)) for i, p in enumerate(self.players)]
        scores.sort(key=lambda x: x[1])
        if len(scores) > 1 and scores[0][1] == scores[1][1]:
            return -1  # Tie
        return scores[0][0]

# ------------ GUI ------------

class DominoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Domino - 4 Players (You vs 3 AI)")
        self.game = DominoGame()

        self.player_colors = ['blue', 'red', 'green', 'purple']

        # Layout
        self.board_frame = tk.Frame(root)
        self.board_frame.pack(pady=10)

        self.hand_frame = tk.Frame(root)
        self.hand_frame.pack(pady=10)

        self.info_frame = tk.Frame(root)
        self.info_frame.pack()

        self.controls_frame = tk.Frame(root)
        self.controls_frame.pack(pady=10)

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

    def toggle_music(self):
        if self.music_on:
            pygame.mixer.music.pause()
            self.music_button.config(text="Play Music")
        else:
            pygame.mixer.music.unpause()
            self.music_button.config(text="Mute Music")
        self.music_on = not self.music_on

    def draw_board(self):
        for widget in self.board_frame.winfo_children():
            widget.destroy()
        for i, tile in enumerate(self.game.board):
            owner = self.game.board_owners[i]
            tile_str = f"[{tile[0]}|{tile[1]}]"
            color = self.player_colors[owner]
            tk.Label(self.board_frame, text=tile_str, font=('Courier', 14), relief='ridge', padx=6, pady=4, fg=color).pack(side=tk.LEFT)

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
        while self.game.current_player != 0 and not self.game.is_game_over():
            cp = self.game.current_player
            hand = self.game.players[cp]
            valid_moves = self.game.get_valid_moves(hand)

            while not valid_moves and self.game.stock:
                drawn = self.game.draw_from_stock(cp)
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

        if self.game.current_player == 0 and not self.game.is_game_over():
            self.status_label.config(text="Your turn!")
            self.draw_hand()

        if self.game.is_game_over():
            self.end_game()

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
        if winner == 0:
            msg = "🎉 You win!"
        elif winner == -1:
            msg = "🤝 It's a tie!"
        else:
            msg = f"🤖 AI {winner} wins!"
        messagebox.showinfo("Game Over", msg)
        self.root.quit()

# ------------ Run the App ------------

if __name__ == "__main__":
    pygame.mixer.init()
    pygame.mixer.music.load("BGM.mp3")
    pygame.mixer.music.play(-1)

    root = tk.Tk()
    app = DominoGUI(root)
    root.mainloop()
