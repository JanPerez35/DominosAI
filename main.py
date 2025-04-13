import random
from collections import deque
import tkinter as tk
from tkinter import messagebox
import copy

# ------------ Game Logic ------------

class DominoGame:
    def __init__(self):
        # Create all 28 unique domino tiles (no repeats, no reverses)
        self.tiles = [(i, j) for i in range(7) for j in range(i, 7)]
        random.shuffle(self.tiles)  # Shuffle tiles before dealing

        # Deal 7 tiles to each player
        self.players = [self.tiles[:7], self.tiles[7:14]]

        # Remaining tiles go into the stock pile
        self.stock = self.tiles[14:]

        # Board is a deque to easily add tiles to both ends
        self.board = deque()

        # Player 0 (human) starts the game
        self.current_player = 0

        # Count consecutive passes (used to detect blocked games)
        self.passes = 0

    def is_valid_move(self, tile, end):
        # A move is valid if one of the tile's numbers matches the board end
        return end in tile

    def get_valid_moves(self, hand):
        # Returns a list of all playable tiles in hand
        if not self.board:
            return hand  # Any tile can be played first
        left, right = self.board[0][0], self.board[-1][1]
        return [t for t in hand if self.is_valid_move(t, left) or self.is_valid_move(t, right)]

    def draw_from_stock(self, player):
        # Player draws a tile from the stock if available
        if self.stock:
            drawn_tile = self.stock.pop()
            self.players[player].append(drawn_tile)
            return drawn_tile
        return None

    def play_tile(self, player, tile):
        # Add tile to the appropriate end of the board
        if not self.board:
            self.board.append(tile)
        else:
            left, right = self.board[0][0], self.board[-1][1]
            if self.is_valid_move(tile, left):
                self.board.appendleft(tile if tile[1] == left else (tile[1], tile[0]))
            elif self.is_valid_move(tile, right):
                self.board.append(tile if tile[0] == right else (tile[1], tile[0]))
            else:
                raise ValueError("Invalid move")
        self.players[player].remove(tile)
        self.passes = 0  # Reset pass counter after a move

    def pass_turn(self):
        # Increment pass counter (used when player can't move)
        self.passes += 1

    def is_game_over(self):
        # Game ends if a player finishes their hand or if both pass
        return any(len(p) == 0 for p in self.players) or self.passes >= 2

    def get_winner(self):
        # Return the winner based on who emptied their hand or has fewer pips
        if len(self.players[0]) == 0:
            return 0
        elif len(self.players[1]) == 0:
            return 1
        else:
            score0 = sum(sum(t) for t in self.players[0])
            score1 = sum(sum(t) for t in self.players[1])
            if score0 == score1:
                return -1  # Tie
            return 0 if score0 < score1 else 1

# ------------ GUI ------------

class DominoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Domino - You vs AI (Monte Carlo)")
        self.game = DominoGame()

        # Layout frames
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

        # Status Labels
        self.status_label = tk.Label(self.info_frame, text="Your turn!")
        self.status_label.pack(side=tk.LEFT, padx=10)

        self.ai_tiles_label = tk.Label(self.info_frame, text="AI has 7 tiles")
        self.ai_tiles_label.pack(side=tk.RIGHT, padx=10)

        # Initial drawing
        self.draw_board()
        self.draw_hand()

    def draw_board(self):
        # Display all tiles currently on the board
        for widget in self.board_frame.winfo_children():
            widget.destroy()
        for tile in self.game.board:
            tile_str = f"[{tile[0]}|{tile[1]}]"
            tk.Label(self.board_frame, text=tile_str, font=('Courier', 14), relief='ridge', padx=6, pady=4).pack(side=tk.LEFT)

    def draw_hand(self):
        # Display all tiles in the player's hand as buttons
        for widget in self.hand_frame.winfo_children():
            widget.destroy()
        hand = self.game.players[0]
        valid_moves = self.game.get_valid_moves(hand)
        for tile in hand:
            tile_str = f"[{tile[0]}|{tile[1]}]"
            btn = tk.Button(self.hand_frame, text=tile_str, font=('Courier', 12), relief='raised',
                            state=tk.NORMAL if tile in valid_moves else tk.DISABLED,
                            command=lambda t=tile: self.play_tile(t))
            btn.pack(side=tk.LEFT, padx=4)

    def play_tile(self, tile):
        # Handle player move
        try:
            self.game.play_tile(0, tile)
            self.after_move()
        except Exception as e:
            messagebox.showerror("Invalid Move", str(e))

    def pass_turn(self):
        # Handle pass
        self.game.pass_turn()
        self.after_move()

    def draw_tile(self):
        # Player draws from stock
        tile = self.game.draw_from_stock(0)
        if tile:
            self.status_label.config(text=f"You drew {tile}")
        else:
            self.status_label.config(text="Stock is empty")
        self.draw_hand()

    def after_move(self):
        # Update UI and check game state after move
        self.draw_board()
        self.draw_hand()
        self.update_ai_tile_count()

        if self.game.is_game_over():
            self.end_game()
        else:
            self.game.current_player = 1
            self.root.after(500, self.ai_turn)

    def ai_turn(self):
        # AI plays using Monte Carlo Simulation
        hand = self.game.players[1]
        valid_moves = self.game.get_valid_moves(hand)

        # AI draws tiles until a move is possible or stock is empty
        while not valid_moves and self.game.stock:
            drawn = self.game.draw_from_stock(1)
            valid_moves = self.game.get_valid_moves(self.game.players[1])
            self.status_label.config(text=f"AI drew a tile")

        # Try to play the best move using MCS
        move = self.monte_carlo_ai_move(simulations=30)
        if move:
            self.game.play_tile(1, move)
            self.status_label.config(text=f"AI played {move} (MCS)")
        else:
            self.game.pass_turn()
            self.status_label.config(text="AI passed")

        self.draw_board()
        self.update_ai_tile_count()

        if self.game.is_game_over():
            self.end_game()
        else:
            self.game.current_player = 0
            self.status_label.config(text="Your turn!")
            self.draw_hand()

    def monte_carlo_ai_move(self, simulations=30):
        # AI evaluates all valid moves via Monte Carlo Simulation
        hand = self.game.players[1]
        valid_moves = self.game.get_valid_moves(hand)
        if not valid_moves:
            return None

        move_scores = {}
        for move in valid_moves:
            total_score = 0
            for _ in range(simulations):
                sim_game = copy.deepcopy(self.game)
                try:
                    sim_game.play_tile(1, move)
                except:
                    continue
                winner = self.simulate_random_playout(sim_game)
                total_score += 1 if winner == 1 else 0
            move_scores[move] = total_score / simulations

        best_move = max(move_scores, key=move_scores.get)
        return best_move

    def simulate_random_playout(self, sim_game):
        # Randomly simulates the rest of the game to estimate outcomes
        current = 0
        while not sim_game.is_game_over():
            hand = sim_game.players[current]
            valid = sim_game.get_valid_moves(hand)
            if valid:
                sim_game.play_tile(current, random.choice(valid))
            elif sim_game.stock:
                sim_game.draw_from_stock(current)
            else:
                sim_game.pass_turn()
            current = 1 - current
        return sim_game.get_winner()

    def update_ai_tile_count(self):
        # Show how many tiles the AI has left
        self.ai_tiles_label.config(text=f"AI has {len(self.game.players[1])} tiles")

    def end_game(self):
        # Display final result
        winner = self.game.get_winner()
        if winner == 0:
            msg = "🎉 You win!"
        elif winner == 1:
            msg = "🤖 AI wins!"
        else:
            msg = "🤝 It's a tie!"
        messagebox.showinfo("Game Over", msg)
        self.root.quit()

# ------------ Run the App ------------
if __name__ == "__main__":
    root = tk.Tk()
    app = DominoGUI(root)
    root.mainloop()
