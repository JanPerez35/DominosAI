import random
from collections import deque
import tkinter as tk
from tkinter import messagebox
# Importing the performance tracker
from PerformanceMeasure import PerformanceTracker
import copy
import pygame

"""
Domino game utilizing two Monte Carlo AI opponents.

This class defines the DominoGame logic and a corresponding GUI class
called DominoGUI to play a dominos game between two AI. This
game specifically utilizes rules from Puerto Rico so it is not a traditional
domino score based game. The word "player" refers the the AI.
"""

class DominoGame:
    """
           Primary game logic for playing a domino game.

          Operations include: creating the domino pieces (tiles), shuffling the tiles, distribution of tiles,
          verifying if a placed tile is a valid domino piece, allowing players to draw from the stock,
          passing turns, deciding the winner and looser of the game, and ending the game.
          The adversarial search utilized for decision-making was the Monte Carlo.

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
        Initializes the game by setting up and shuffling the tiles. Then, distributes 7 tiles to both players. The stock
        takes the rest of the tiles. It also determines the starting player based on the highest double in the original
        hand. This is a Puerto Rican rule where whoever has the [6|6] piece starts the game.
        """

        # Creates the domino pieces (tiles) from [0|0] up to [6|6]
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
        #Finds the highest double piece within the players' hands
        self.highest_double = None
        # Flag to trigger AI move at start
        self.ai_should_start = False
        # Index of the player who starts the game
        self.starting_player = 0

        # Determines the starting AI player by "Regla del 6"
        for n in range(6, -1, -1):
            if (n, n) in self.players[0]:
                self.highest_double = (n, n)
                self.players[0].remove((n, n))
                self.board.append(((n, n), 0))
                self.starting_player = 0
                self.current_player = 1
                self.ai_should_start = True
                break
            elif (n, n) in self.players[1]:
                self.highest_double = (n, n)
                self.players[1].remove((n, n))
                self.board.append(((n, n), 1))
                self.current_player = 0
                self.starting_player = 1
                break



    def is_valid_move(self, tile, end):
        """
        Verifies if a tile can be placed on either end of the board.

        Args:
            tile (Tuple[int, int]): The domino tile to check.
            end (int): The number at the board end to match.

        Returns:
            bool: True if the tile contains the value 'end'.
        """
        return end in tile


    def get_valid_moves(self, hand):
        """
        From the player's hand it highlights the tiles that can be placed on either end of the board.
        If the board is empty, any tile is valid. Since both players are AI the user will not see their hands.

        Args:
              hand (List[Tuple[int, int]]): The AI's current hand.

        Returns:
                List[Tuple[int, int]]: Tiles that can be legally played.
        """
        if not self.board:
            return hand
        left, right = self.board[0][0][0], self.board[-1][0][1]
        return [t for t in hand if self.is_valid_move(t, left) or self.is_valid_move(t, right)]


    def draw_from_stock(self, player):
        if self.stock:
            drawn_tile = self.stock.pop()
            self.players[player].append(drawn_tile)
            return drawn_tile
        return None


    def play_tile(self, player, tile):
        """
         Allows to place a player's tile on the board if the move is valid.

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
        A counter that verifies if the current player has passed their turn.
        If so, the counter is incremented.
        """
        self.passes += 1


    def is_game_over(self):
        """
        Verifies if the game is over. A game over is triggered when the first player is left without any tiles.
        Another way to finish the game is if both players consequently pass their turn and not tiles are left in stock.

        Returns:
            bool: True if the game is over, False otherwise.
        """
        return any(len(p) == 0 for p in self.players) or self.passes >= 2


    def get_winner(self):
        """
         Determines the winner of the game.

         If a player has emptied their hand, they win. Otherwise, the player with
        the lowest pip count wins; ties return -1.

         Returns:
            int: Winning player index (0 or 1), or -1 for a tie.
        """

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
            # Tie
            return -1
        else:
            # Index of the winning player
            return player_scores[0][0]



class DominoGUI:
    """
        GUI for DominoGame using Tkinter, with two Monte Carlo AI opponent.

        Provides controls for playing, drawing, passing, and displays game state.
    """
    def __init__(self, root, tracker):
        """
         Initializes GUI components, starts music, and kicks off game loop.

        Args:
             root (tk.Tk): The main Tkinter window.
        """
        self.root = root
        # Tracker added for performance measurement
        self.tracker = PerformanceTracker()
        self.root.title("Domino - AI vs AI (Monte Carlo)")
        self.game = DominoGame()

        # Frames for Layout
        self.board_frame = tk.Frame(root)
        self.board_frame.pack(pady=10)

        self.root.after(1000, self.ai_turn)

        self.info_frame = tk.Frame(root)
        self.info_frame.pack()

        self.controls_frame = tk.Frame(root)
        self.controls_frame.pack(pady=10)

        self.music_on = True
        self.music_button = tk.Button(self.controls_frame, text="Mute Music", command=self.toggle_music)
        self.music_button.pack(side=tk.LEFT, padx=5)

        # Status labels
        self.status_label = tk.Label(self.info_frame, text="AI 0 vs AI 1")
        self.status_label.pack(side=tk.LEFT, padx=10)

        self.ai_tiles_label = tk.Label(self.info_frame, text="AI has 7 tiles")
        self.ai_tiles_label.pack(side=tk.RIGHT, padx=10)

        # Initial draw of tiles and determines the current player by highest
        #double valued piece.
        self.draw_board()
        if self.game.ai_should_start:
            self.root.after(500, self.ai_turn)

        if self.game.current_player != 0:
            self.status_label.config(
                text=f"AI {self.game.current_player} starts with (6|6)"
            )
            self.root.after(1000, self.ai_turn)
        else:
            self.status_label.config(text=f"AI {self.game.current_player} starts with (6|6)")


    def toggle_music(self):
        """
        Toggle the background music's play/pause state.
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
        Creates and renders the current domino board within the GUI.
        """
        for widget in self.board_frame.winfo_children():
            widget.destroy()

        for tile, player in self.game.board:
            #Designates a specific color to each Player.
            color = 'blue' if player == 0 else 'red'

            if tile[0] == tile[1]:
                # It's a double tile that should be displayed vertically.
                frame = tk.Frame(self.board_frame)
                tk.Label(frame, text=f"{tile[0]}", font=('Courier', 12), fg=color,bg= 'white', relief='ridge').pack()
                tk.Label(frame, text=f"{tile[1]}", font=('Courier', 12), fg=color,bg= 'white', relief='ridge').pack()
                frame.pack(side=tk.LEFT, padx=4)
            else:
                # Any other tile is displayed horizontally.
                tile_str = f"{tile[0]}|{tile[1]}"
                tk.Label(self.board_frame, text=tile_str, font=('Courier', 14), relief='ridge',
                         padx=6, pady=4, fg=color, bg='white').pack(side=tk.LEFT)


    def ai_turn(self):
        """
        Play actions of the AI, makes use of Monte Carlo simulations for decision-making.
        """
        if self.game.is_game_over():
            # Prevents calling the game over screen again.
            return

        player = self.game.current_player
        hand = self.game.players[player]
        valid_moves = self.game.get_valid_moves(hand)

        # Draw until a valid move or stock empty
        while not valid_moves and self.game.stock:
            self.game.draw_from_stock(player)
            valid_moves = self.game.get_valid_moves(self.game.players[player])
            self.status_label.config(text=f"AI {player} drew a tile")

        # Employs the Monte Carlo simulation.
        move = self.monte_carlo_ai_move(player, simulations=30)
        # Labels that show which player is currently playing and what piece have they played
        if move:
            self.game.play_tile(player, move)
            self.status_label.config(text=f"AI {player} played {move}")
        else:
            # Label that presents which player has skipped their turns
            self.game.pass_turn()
            self.status_label.config(text=f"AI {player} passed")

        self.draw_board()
        # Updates the current amount of tiles that a player has left
        self.update_ai_tile_count()

        if self.game.is_game_over():
            self.end_game()
        else:
            # Next player is allowed to play.
            self.game.current_player = 1 - player
            self.root.after(1500, self.ai_turn)


    def monte_carlo_ai_move(self, player, simulations=30):
        """
            Evaluate possible moves via Monte Carlo playouts and return best one.
            Currently, it runs 30 simulations per move.

            Args:
                simulations (int): Number of random playouts per move.

            Returns:
                Optional[Tuple[int, int]]: Best tile to play or None to pass.
            """
        hand = self.game.players[player]
        valid_moves = self.game.get_valid_moves(hand)
        if not valid_moves:
            return None

        move_scores = {}
        for move in valid_moves:
            total_score = 0
            for _ in range(simulations):
                sim_game = copy.deepcopy(self.game)
                try:
                    sim_game.play_tile(player, move)
                except ValueError:
                    continue
                winner = self.simulate_random_playout(sim_game)
                total_score += 1 if winner == player else 0
            move_scores[move] = total_score / simulations

        best_move = max(move_scores, key=move_scores.get)
        return best_move


    def simulate_random_playout(self, sim_game):
        """
        Run a random playout until game end to estimate outcome.

        Args:
            sim_game (DominoGame): Game state copy.

        Returns:
            int: Winning player index or -1 for tie.
        """
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
        """
        Refresh label showing how many tiles AI holds.
        """
        self.ai_tiles_label.config(text=f"AI {self.game.current_player} has {len(self.game.players[1])} tiles")


    def start_new_game(self):
        """
        Initiates a new instance of a domino game.
        """
        self.game = DominoGame()

        # Resets the board display
        for widget in self.board_frame.winfo_children():
            widget.destroy()

        # Redraws the board on screen
        self.draw_board()

        # Update the AI tile count display
        self.update_ai_tile_count()

        # Set the status label based on who starts
        if self.game.current_player != 0:
            self.status_label.config(text=f"AI {self.game.current_player} starts with (6|6)!")
        else:
            self.status_label.config(text=f"AI {self.game.current_player} starts with (6|6)!")

        # Delay to allow the game to update before the first move
        self.root.after(1000, self.ai_turn)


    def end_game(self):
        """
        Handle end-of-game display and exit. Displays who wins.
        """
        winner = self.game.get_winner()

        # Prints all players' remaining points
        player_scores = [
            (i, sum(t[0] + t[1] for t in hand), hand)
            for i, hand in enumerate(self.game.players)
        ]
        score_lines = "\n".join(
            f"Player {i} (AI {i}): {score} points | Tiles: {hand}"
            for i, score, hand in player_scores
        )
        print("Final scores (lower is better):")
        for i, score, hand in player_scores:
            print(f"AI {i}: {score} points")
            # Stores the scores for each AI player
            if i == 0:
                ai1_score = score
            else: ai2_score = score

        if winner == 0:
            msg = f"🎉 AI {winner} wins!"
        elif winner == -1:
            msg = "🤝 It's a tie!"
        else:
            msg = f"🤖 AI {winner} wins!"

        msg += "\nFinal Scores:\n" + score_lines

        messagebox.showinfo("Game Over", msg)

        #Performance Tracking 
        self.tracker.update_tracker_2_player(winner, ai1_score, ai2_score, "2 AI")
        self.tracker.report()

        #Play again option
        play_again = messagebox.askyesno(
            title="Play again?",
            message="Would you like to play again?"
        )
        if play_again:
            self.start_new_game()
        else:
            self.root.quit()



# Runs the application
if __name__ == "__main__":
    pygame.mixer.init()
    # Copyright free music to set the mood for the game.
    pygame.mixer.music.load("BGM.mp3")
    pygame.mixer.music.play(-1)

    # Tracker added for performance measurement
    tracker = PerformanceTracker()
    root = tk.Tk()
    # Tracker added for performance measurement
    app = DominoGUI(root, tracker)
    root.mainloop()
