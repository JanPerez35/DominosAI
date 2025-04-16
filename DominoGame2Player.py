import random
from collections import deque
import tkinter as tk
from tkinter import messagebox
import copy
import pygame

'''
Class that starts the domino game. It creates the dominos, shuffles them, sets the players,
stock, board, player that's currently playing and the passes. 
'''


class DominoGame:
    def __init__(self):
        # This creates the tiles
        self.tiles = [(i, j) for i in range(7) for j in range(i, 7)]
        # Shuffles the tiles
        random.shuffle(self.tiles)
        # Gives the player the tiles to play
        self.players = [self.tiles[:7], self.tiles[7:14]]
        # Keeps stock of the available tiles
        self.stock = self.tiles[14:]
        # Stores (tile, player)
        self.board = deque()
        # Checks who's playing
        self.current_player = 0
        # Checks who passed
        self.passes = 0
        #find highest double in players' hands
        highest_double = None
        self.ai_should_start = False  # Flag to trigger AI move at start

        for n in range(6, -1, -1):
            if (n, n) in self.players[0]:
                highest_double = (n, n)
                self.players[0].remove((n, n))
                self.board.append(((n, n), 0))
                self.current_player = 1  # AI goes next
                self.ai_should_start = True
                break
            elif (n, n) in self.players[1]:
                highest_double = (n, n)
                self.players[1].remove((n, n))
                self.board.append(((n, n), 1))
                self.current_player = 0  # Human goes next
                break

        for i, hand in enumerate(self.players):
            if (6, 6) in hand:
                self.current_player = (i + 1) % 4
                hand.remove((6, 6))  # Remove from hand
                self.board.append((6, 6))  # Place it on the board
                self.board_owners.append(i)  # Track who played it
                break

    '''
    Verifies if the move is valid, meaning if the tile you want to use matches with a corner
    '''

    def is_valid_move(self, tile, end):
        return end in tile

    '''
    Verifies if the move is valid and highlights it
    '''

    def get_valid_moves(self, hand):
        if not self.board:
            return hand
        left, right = self.board[0][0][0], self.board[-1][0][1]
        return [t for t in hand if self.is_valid_move(t, left) or self.is_valid_move(t, right)]

    '''
    Verifies if there are available tiles to draw from.
    '''

    def draw_from_stock(self, player):
        if self.stock:
            drawn_tile = self.stock.pop()
            self.players[player].append(drawn_tile)
            return drawn_tile
        return None

    '''
    Allows you to play a tile.
    '''

    def play_tile(self, player, tile):
        if not self.board:
            self.board.append((tile, player))
        else:
            left, right = self.board[0][0][0], self.board[-1][0][1]
            if self.is_valid_move(tile, left):
                t = tile if tile[1] == left else (tile[1], tile[0])
                self.board.appendleft((t, player))
            elif self.is_valid_move(tile, right):
                t = tile if tile[0] == right else (tile[1], tile[0])
                self.board.append((t, player))
            else:
                raise ValueError("Invalid move")
        self.players[player].remove(tile)
        self.passes = 0

    '''
    Passes a turn if the user or the AI clicks on pass.
    '''

    def pass_turn(self):
        self.passes += 1

    '''
    Defines the end of the game.
    '''

    def is_game_over(self):
        return any(len(p) == 0 for p in self.players) or self.passes >= 2

    '''
    Defines winner of the game as the player that has no tiles or in the case of getting stuck
    chooses the player with the least amount of points as the winner.
    '''

    def get_winner(self):
        # Calculate total pip count for each player
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

'''
Class that handles the GUI and interacts with the game logic for user and AI interactions.
'''


class DominoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Domino - You vs AI (Monte Carlo)")
        self.game = DominoGame()

        self.board_frame = tk.Frame(root)
        self.board_frame.pack(pady=10)

        self.hand_frame = tk.Frame(root)
        self.hand_frame.pack(pady=10)

        self.info_frame = tk.Frame(root)
        self.info_frame.pack()

        self.controls_frame = tk.Frame(root)
        self.controls_frame.pack(pady=10)

        self.pass_button = tk.Button(self.controls_frame, text="Pass Turn", command=self.pass_turn)
        self.pass_button.pack(side=tk.LEFT, padx=5)

        self.draw_button = tk.Button(self.controls_frame, text="Draw Tile", command=self.draw_tile)
        self.draw_button.pack(side=tk.LEFT, padx=5)

        self.music_on = True
        self.music_button = tk.Button(self.controls_frame, text="Mute Music", command=self.toggle_music)
        self.music_button.pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(self.info_frame, text="Your turn!")
        self.status_label.pack(side=tk.LEFT, padx=10)

        self.ai_tiles_label = tk.Label(self.info_frame, text="AI has 7 tiles")
        self.ai_tiles_label.pack(side=tk.RIGHT, padx=10)

        self.draw_board()
        self.draw_hand()
        if self.game.ai_should_start:
            self.root.after(500, self.ai_turn)

        if self.game.current_player != 0:
            self.status_label.config(
                text=f"AI {self.game.current_player} starts with (6|6)"
            )
            self.root.after(1000, self.ai_turn)
        else:
            self.status_label.config(text="You start with (6|6)!")

    '''
    Toggles the music playback between playing and pausing.
    (Why not? It was a few lines of code)
    '''

    def toggle_music(self):
        if self.music_on:
            pygame.mixer.music.pause()
            self.music_button.config(text="Play Music")
        else:
            pygame.mixer.music.unpause()
            self.music_button.config(text="Mute Music")
        self.music_on = not self.music_on

    '''
    Draws the current state of the game board.
    '''

    def draw_board(self):
            for widget in self.board_frame.winfo_children():
                widget.destroy()

            for tile, player in self.game.board:
                color = 'blue' if player == 0 else 'red'

                if tile[0] == tile[1]:  # It's a double - display vertically
                    frame = tk.Frame(self.board_frame)
                    tk.Label(frame, text=f"{tile[0]}", font=('Courier', 12), fg=color,bg= 'white', relief='ridge').pack()
                    tk.Label(frame, text=f"{tile[1]}", font=('Courier', 12), fg=color,bg= 'white', relief='ridge').pack()
                    frame.pack(side=tk.LEFT, padx=4)
                else:
                    # Regular horizontal display
                    tile_str = f"{tile[0]}|{tile[1]}"
                    tk.Label(self.board_frame, text=tile_str, font=('Courier', 14), relief='ridge',
                             padx=6, pady=4, fg=color, bg='white').pack(side=tk.LEFT)

    '''
    Draws the player's hand, displaying their available tiles and valid moves.
    '''

    def draw_hand(self):
        for widget in self.hand_frame.winfo_children():
            widget.destroy()
        hand = self.game.players[0]
        valid_moves = self.game.get_valid_moves(hand)
        for tile in hand:
            tile_str = f"[{tile[0]}|{tile[1]}]"
            btn = tk.Button(self.hand_frame, text=tile_str, font=('Courier', 12), relief='raised',fg = 'blue',
                            state=tk.NORMAL if tile in valid_moves else tk.DISABLED,
                            command=lambda t=tile: self.play_tile(t))
            btn.pack(side=tk.LEFT, padx=4)

    '''
    Handles the player's move, tries to play the tile and updates the game state.
    '''

    def play_tile(self, tile):
        try:
            self.game.play_tile(0, tile)
            self.after_move()
        except Exception as e:
            messagebox.showerror("Invalid Move", str(e))

    '''
    Passes the turn to the next player and updates the game state.
    '''

    def pass_turn(self):
        self.game.pass_turn()
        self.after_move()

    '''
    Draws a tile from the stock and updates the player's hand.
    '''

    def draw_tile(self):
        tile = self.game.draw_from_stock(0)
        if tile:
            self.status_label.config(text=f"You drew {tile}")
        else:
            self.status_label.config(text="Stock is empty")
        self.draw_hand()

    '''
    Updates the board, hand, and AI tile counts after a move. Checks if the game is over.
    '''

    def after_move(self):
        self.draw_board()
        self.draw_hand()
        self.update_ai_tile_count()

        if self.game.is_game_over():
            self.end_game()
        else:
            self.game.current_player = 1
            self.root.after(500, self.ai_turn)

    '''
    Simulates the AI's turn using Monte Carlo tree search.
    '''

    def ai_turn(self):
        hand = self.game.players[1]
        valid_moves = self.game.get_valid_moves(hand)

        while not valid_moves and self.game.stock:
            drawn = self.game.draw_from_stock(1)
            valid_moves = self.game.get_valid_moves(self.game.players[1])
            self.status_label.config(text=f"AI drew a tile")

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

    '''
    Uses Monte Carlo simulations to decide on the best move for the AI.
    Currently it makes 30 simulations to find the best solution but this could
    change depending on the difficulty we want it to have.
    '''

    def monte_carlo_ai_move(self, simulations=30):
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

    '''
    Simulates a random playout of the game to determine the outcome.
    Aids Monte Carlo simulations to decide on the best move for the AI.
    '''

    def simulate_random_playout(self, sim_game):
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

    '''
    Updates the label displaying the number of tiles the AI has.
    '''

    def update_ai_tile_count(self):
        self.ai_tiles_label.config(text=f"AI has {len(self.game.players[1])} tiles")

    '''
    Ends the game and displays the winner.
    '''

    def end_game(self):
        winner = self.game.get_winner()

        # Optional: Print all players' remaining points
        player_scores = [
            (i, sum(t[0] + t[1] for t in hand), hand)
            for i, hand in enumerate(self.game.players)
        ]
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
    pygame.mixer.init()
    #Royalty free BGM to set the mood
    pygame.mixer.music.load("BGM.mp3")
    pygame.mixer.music.play(-1)

    root = tk.Tk()
    app = DominoGUI(root)
    root.mainloop()
