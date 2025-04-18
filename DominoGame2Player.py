import random
from collections import deque
import tkinter as tk
from tkinter import messagebox
import copy
import pygame

"""
Domino game utilizing Monter Carlo AI opponent

This class defines the DominoGame logic and a corresponding GUI class
called DominoGUI to play a dominoes game between a human and an AI. This
game specifically utilizes rules from Puerto Rico so it is not a traditional
domino score based game.
"""

class DominoGame:
    """
        Core game logic for Domino.

        Handles tile creation, shuffling, dealing, move validation, drawing from stock,
        turn passing, and determining game end and winner. Uses a Monte Carlo
        approach for AI decision-making.

        Attributes:
            tiles (List[Tuple[int, int]]): All domino tiles in the game.
            players (List[List[Tuple[int, int]]]): Two players' hands.
            stock (List[Tuple[int, int]]): Remaining tiles to draw.
            board (Deque[Tuple[Tuple[int, int], int]]): Placed tiles with their owner index.
            current_player (int): Index of the player whose turn it is (0 or 1).
            passes (int): Number of consecutive passes.
            highest_double (Optional[Tuple[int, int]]): The highest starting double.
            ai_should_start (bool): Flag indicating if AI plays first.
            starting_player (int): Index of the player who started.
        """


    def __init__(self):
        """
        This definition initializes the game by creating and shuffling the tiles,
        dealing to players, setting up the stock and determining the starting player
        based on the highest double in initial hands. This rule is taken from Puerto Rico's "Regla del 6" rule.
        """

        # This creates the tiles from (0-0 up to 6-6)
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
        #finds highest double in players' hands
        self.highest_double = None
        # Flag to trigger AI move at start
        self.ai_should_start = False
        # Index of the player who starts the game
        self.starting_player = 0

        for n in range(6, -1, -1):
            if (n, n) in self.players[0]:
                self.highest_double = (n, n)
                self.players[0].remove((n, n))
                self.board.append(((n, n), 0))
                self.starting_player = 0
                # AI goes next
                self.current_player = 1
                self.ai_should_start = True
                break
            elif (n, n) in self.players[1]:
                self.highest_double = (n, n)
                self.players[1].remove((n, n))
                self.board.append(((n, n), 1))
                self.starting_player = 1
                # Human goes next
                self.current_player = 0
                break
                        

    def is_valid_move(self, tile, end):
        """
               Checks if a tile can be placed at one end of the board or the other.

               Args:
                   tile (Tuple[int, int]): The domino tile to check.
                   end (int): The number at the board end to match.

               Returns:
                   bool: True if the tile contains the value 'end'.
               """
        return end in tile



    def get_valid_moves(self, hand):
        """
               List valid moves for a given hand based on current board ends.
               If the board is empty, any tile is valid.

               Args:
                   hand (List[Tuple[int, int]]): The player's current hand.

               Returns:
                   List[Tuple[int, int]]: Tiles that can be legally played.
               """
        if not self.board:
            return hand
        left, right = self.board[0][0][0], self.board[-1][0][1]
        return [t for t in hand if self.is_valid_move(t, left) or self.is_valid_move(t, right)]

    def draw_from_stock(self, player):
        """
                Draw a tile from the stock for a player if available.

                Args:
                    player (int): Index of the player drawing (0 or 1).

                Returns:
                    Optional[Tuple[int, int]]: The drawn tile, or None if stock is empty.
                """
        if self.stock:
            drawn_tile = self.stock.pop()
            self.players[player].append(drawn_tile)
            return drawn_tile
        return None



    def play_tile(self, player, tile):
        """
               Place a tile on the board for a player if the move is valid.

               Tiles are oriented correctly to match the board end.

               Args:
                   player (int): Index of the player playing (0 or 1).
                   tile (Tuple[int, int]): The tile to play.

               Raises:
                   ValueError: If the move is invalid.
               """
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

    def pass_turn(self):
        """
                Verifies a pass for the current player, incrementing the pass counter.
                """
        self.passes += 1

    def is_game_over(self):
        """
               Check if the game has ended.

               The game ends when a player has no tiles or both players pass consecutively.
               This was done to avoid infinite looping.

               Returns:
                   bool: True if the game is over.
               """
        return any(len(p) == 0 for p in self.players) or self.passes >= 2


    def get_winner(self):
        """
                Determine the winner of the game.

                If a player emptied their hand, they win. Otherwise, the player with
                the lowest pip count wins; ties return -1.

                Returns:
                    int: Winning player index (0 or 1), or -1 for a tie.
                """

        # Calculates total pip count for each player
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
            # Index of the winning player
            return player_scores[0][0]


class DominoGUI:
    """
       GUI for DominoGame using Tkinter, with Monte Carlo AI opponent.

       Provides controls for playing, drawing, passing, and displays game state.
       """

    def __init__(self, root):
        """
                Initializes GUI components, starts music, and kicks off game loop.

                Args:
                    root (tk.Tk): The main Tkinter window.
                """
        self.root = root
        self.root.title("Domino - You vs AI (Monte Carlo)")
        self.game = DominoGame()

        #Frames for Layout
        self.board_frame = tk.Frame(root)
        self.board_frame.pack(pady=10)

        self.hand_frame = tk.Frame(root)
        self.hand_frame.pack(pady=10)

        self.info_frame = tk.Frame(root)
        self.info_frame.pack()

        self.controls_frame = tk.Frame(root)
        self.controls_frame.pack(pady=10)

        #Control buttons
        self.pass_button = tk.Button(self.controls_frame, text="Pass Turn", command=self.pass_turn)
        self.pass_button.pack(side=tk.LEFT, padx=5)

        self.draw_button = tk.Button(self.controls_frame, text="Draw Tile", command=self.draw_tile)
        self.draw_button.pack(side=tk.LEFT, padx=5)

        self.music_on = True
        self.music_button = tk.Button(self.controls_frame, text="Mute Music", command=self.toggle_music)
        self.music_button.pack(side=tk.LEFT, padx=5)

        #Status labels
        self.status_label = tk.Label(self.info_frame, text="Your turn!")
        self.status_label.pack(side=tk.LEFT, padx=10)

        self.ai_tiles_label = tk.Label(self.info_frame, text="AI has 7 tiles")
        self.ai_tiles_label.pack(side=tk.RIGHT, padx=10)


        #Initial draw of tiles.
        self.draw_board()
        self.draw_hand()
        self.update_ai_tile_count()

        # Announces starting player
        if self.game.starting_player != 0:
            self.status_label.config(
                text=f"AI starts with {self.game.highest_double}!"
            )            
        else:
            self.status_label.config(text=f"You start with {self.game.highest_double}!")
            self.root.after(1000, self.ai_turn)            

    def toggle_music(self):
        """
               Toggles the background music's play/pause state.
               """
        if self.music_on:
            pygame.mixer.music.pause()
            self.music_button.config(text="Play Music")
        else:
            pygame.mixer.music.unpause()
            self.music_button.config(text="Mute Music")
        self.music_on = not self.music_on

    def draw_board(self):
        """
               Render the current domino board in the GUI.
               """
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

    def draw_hand(self):
        """
               Render the human player's hand with buttons for valid moves.
               """

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

    def play_tile(self, tile):
        """
        Handle the human player's play action and update state.

        Args:
            tile (Tuple[int, int]): Tile chosen by player.
        """
        try:
            self.game.play_tile(0, tile)
            self.after_move()
        except Exception as e:
            messagebox.showerror("Invalid Move", str(e))

    def pass_turn(self):
        """
        Handles when a human player is passing their turn.
        """
        self.game.pass_turn()
        self.after_move()

    def draw_tile(self):
        """
        Handles human player drawing from stock and update GUI.
        """
        tile = self.game.draw_from_stock(0)
        if tile:
            self.status_label.config(text=f"You drew {tile}")
        else:
            self.status_label.config(text="Stock is empty")
        self.draw_hand()

    def after_move(self):
        """
        Update board and hand after a move and trigger AI or end game.
        """
        self.draw_board()
        self.draw_hand()
        self.update_ai_tile_count()

        if self.game.is_game_over():
            self.end_game()
        else:
            self.game.current_player = 1
            self.root.after(500, self.ai_turn)

    def ai_turn(self):
        """
        Perform AI turn using Monte Carlo simulations for decision-making.
        """
        hand = self.game.players[1]
        valid = self.game.get_valid_moves(hand)
        # Draw until a valid move or stock empty
        while not valid and self.game.stock:
            tile = self.game.draw_from_stock(1)
            valid = self.game.get_valid_moves(self.game.players[1])
            self.status_label.config(text="AI drew a tile")

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
        """
        Evaluate possible moves via Monte Carlo playouts and return best one.
        Currently, it runs 30 simulations per move.

        Args:
            simulations (int): Number of random playouts per move.

        Returns:
            Optional[Tuple[int, int]]: Best tile to play or None to pass.
        """
        hand = self.game.players[1]
        valid = self.game.get_valid_moves(hand)
        if not valid:
            return None

        scores = {}
        for m in valid:
            wins = 0
            for _ in range(simulations):
                sim = copy.deepcopy(self.game)
                try:
                    sim.play_tile(1, m)
                except ValueError:
                    continue
                if self.simulate_random_playout(sim) == 1:
                    wins += 1
            scores[m] = wins / simulations
        return max(scores, key=scores.get)

    def simulate_random_playout(self, sim_game):
        """
        Run a random playout until game end to estimate outcome.

        Args:
            sim_game (DominoGame): Game state copy.

        Returns:
            int: Winning player index or -1 for tie.
        """
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
            current = 1 - current
        return sim_game.get_winner()

    def update_ai_tile_count(self):
        """
        Refresh label showing how many tiles AI holds.
        """
        self.ai_tiles_label.config(text=f"AI has {len(self.game.players[1])} tiles")

    def end_game(self):
        """
        Handle end-of-game display and exit. Displays who wins.
        """
        winner = self.game.get_winner()
        scores = [(i, sum(a + b for a, b in hand), hand) for i, hand in enumerate(self.game.players)]
        summary = "\n".join(
            f"Player {i} ({'You' if i == 0 else 'AI'}): {pts} points | Tiles: {hand}"
            for i, pts, hand in scores
        )
        if winner == 0:
            msg = "\uD83C\uDF89 You win!"
        elif winner == -1:
            msg = "\uD83E\uDD1D It's a tie!"
        else:
            msg = "\uD83E\uDD16 AI wins!"
        msg += f"\nFinal Scores:\n{summary}"
        messagebox.showinfo("Game Over", msg)
        self.root.quit()
#This area runs the app

if __name__ == "__main__":
    pygame.mixer.init()
    #Copyright free music to set the mood for the game. Just a fun addition.
    pygame.mixer.music.load("BGM.mp3")
    pygame.mixer.music.play(-1)

    root = tk.Tk()
    app = DominoGUI(root)
    root.mainloop()