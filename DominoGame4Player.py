import random
from collections import deque
import tkinter as tk
from tkinter import messagebox
from PerformanceMeasure import PerformanceTracker #importing the performance tracker
import copy
import pygame
import sys

"""
Domino game utilizing Monte Carlo AI opponent

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

    def __init__(self, team_mode):

        """
        Initialize the game by creating, shuffling, and dealing tiles,
        setting up player hands, stock, board, and determining first player
        based on the 6|6 tile.

        Args:
            team_mode (bool): Enable team scoring if True.
        """

        self.tiles = [(i, j) for i in range(7) for j in range(i, 7)]
        random.shuffle(self.tiles)
        self.players = [self.tiles[i*7:(i+1)*7] for i in range(4)]
        self.stock = self.tiles[28:]
        self.board = deque()
        # To track who placed each tile
        self.board_owners = deque()
        self.current_player = 0
        self.passes = 0
        self.team_mode = team_mode
        #Determine starting player with the highest double
        for i, hand in enumerate(self.players):
            if (6, 6) in hand:
                self.current_player = (i + 1) % 4
                # Remove from hand
                hand.remove((6, 6))
                # Place it on the board
                self.board.append((6, 6))
                # Track who played it
                self.board_owners.append(i)
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
        left, right = self.board[0][0], self.board[-1][1]
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
        return any(len(p) == 0 for p in self.players) or self.passes >= 4

    def get_winner(self):
        """
                    Determine the winner of the game.

                    If a player emptied their hand, they win. Otherwise, the player with
                    the lowest pip count wins; ties return -1.

                    Returns:
                        int: Winning player index (0 or 1), or -1 for a tie.
                    """
        # Calculate total pip count for each player
        if self.team_mode:
            team_0_score = sum(tile[0] + tile[1] for i in [0, 2] for tile in self.players[i])
            team_1_score = sum(tile[0] + tile[1] for i in [1, 3] for tile in self.players[i])
            if team_0_score < team_1_score:
                return "Team 1"
            elif team_1_score < team_0_score:
                return "Team 2"
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
                # Index of the winning player
                 return player_scores[0][0]



class DominoGUI:
    """
          GUI for DominoGame using Tkinter, with Monte Carlo AI opponent.

          Provides controls for playing, drawing, passing, and displays game state.
          """

    def __init__(self, root, team_mode, tracker):
        """
               Initialize GUI components, set up game and layout frames,
               and begin game loop after initial placement.

               Args:
                   root (tk.Tk): Main Tkinter window.
                   team_mode (bool): Enable team scoring visuals.
               """
        self.root = root
        self.root.title("Domino - 4 Players (You vs 3 AI)")
        self.tracker = PerformanceTracker() #tracker added
        self.game = DominoGame(team_mode)

        if team_mode:
            self.player_colors = ['blue', 'red', 'blue', 'red']
        else:
            self.player_colors = ['blue', 'red', 'green', 'purple']

        # Frames for Layout
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
                ("Player 1 (Team 0)" if team_mode else "AI 0", self.player_colors[0]),
                ("AI 1 (Team 1)" if team_mode else "AI 1", self.player_colors[1]),
                ("AI 2 (Team 0)" if team_mode else "AI 2", self.player_colors[2]),
                ("AI 3 (Team 1)" if team_mode else "AI 3", self.player_colors[3]),
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

        # Control Buttons
        self.pass_button = tk.Button(self.controls_frame, text="Pass Turn", command=self.pass_turn)
        self.pass_button.pack(side=tk.LEFT, padx=5)

        self.draw_button = tk.Button(self.controls_frame, text="Draw Tile", command=self.draw_tile)
        self.draw_button.pack(side=tk.LEFT, padx=5)

        self.music_on = True
        self.music_button = tk.Button(self.controls_frame, text="Mute Music", command=self.toggle_music)
        self.music_button.pack(side=tk.LEFT, padx=5)

        #Status Labels
        self.status_label = tk.Label(self.info_frame, text="Your turn!")
        self.status_label.pack(side=tk.LEFT, padx=10)

        self.ai_labels = [tk.Label(self.info_frame, text=f"AI {i} has 7 tiles") for i in range(1, 4)]
        for label in self.ai_labels:
            label.pack(side=tk.RIGHT, padx=5)

        self.draw_board()
        self.draw_hand()
        #Announces starting player
        if self.game.current_player != 0:
            self.status_label.config(
                text=f"AI {self.game.current_player} starts with (6|6)"
            )
            self.root.after(1000, self.ai_turn)
        else:
            self.status_label.config(text="You start with (6|6)!")


    def scroll_left(self):
        """
         Scroll left by one unit
        """
        current_x = self.board_canvas.canvasx(0)
        self.board_canvas.xview_scroll(-1, "units")

    def scroll_right(self):
        """
        Scroll right by one unit
        """
        current_x = self.board_canvas.canvasx(0)
        self.board_canvas.xview_scroll(1, "units")


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
        self.board_canvas.delete("all")
        # Start position
        x, y = 500, 150
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
        """
             Render the human player's hand with buttons for valid moves.
            """
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
        """
            Handle the human player's play action and update state.

            Args:
                tile (Tuple[int, int]): Tile chosen by player.
            """
        try:
            self.game.play_tile(0, tile)
            self.game.current_player = (self.game.current_player + 1) % 4  # <-- Fix is here
            self.after_move()
        except Exception as e:
            messagebox.showerror("Invalid Move", str(e))

    def pass_turn(self):
        """
            Handles when a human player is passing their turn.
            """
        self.game.pass_turn()
        self.game.current_player = (self.game.current_player + 1) % 4
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
        self.update_ai_tile_counts()

        if self.game.is_game_over():
            self.end_game()
        else:
            self.root.after(500, self.ai_turn)

    def ai_turn(self):
        """
            Perform AI turn using Monte Carlo simulations for decision-making.
            """
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


    def monte_carlo_ai_move(self, player_index, simulations=30):
        """
            Evaluate possible moves via Monte Carlo playouts and return best one.
            Currently, it runs 30 simulations per move.

            Args:
                simulations (int): Number of random playouts per move.

            Returns:
                Optional[Tuple[int, int]]: Best tile to play or None to pass.
            """
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
            current = (current + 1) % 4
        return sim_game.get_winner()

    def update_ai_tile_counts(self):
        """
            Refresh label showing how many tiles AI holds.
            """
        for i in range(1, 4):
            self.ai_labels[i - 1].config(text=f"AI {i} has {len(self.game.players[i])} tiles")

    '''
    Starts a new game.
    '''

    def start_new_game(self,teamMode):
        self.game = DominoGame(teamMode)
        self.game_over = False
        self.last_human = None

        # Clear canvas (but keep the widget)
        self.board_canvas.delete("all")

        # Clear player hand
        for widget in self.hand_frame.winfo_children():
            widget.destroy()

        self.draw_board()
        self.draw_hand()
        self.update_ai_tile_counts()

        if self.game.current_player in [0,1,2]:
            self.status_label.config(text=f"AI {1 if self.game.current_player == 1 else 2} starts with (6|6)!")
            self.root.after(1000, self.ai_turn)
        else:
            self.status_label.config(text=f"You start with (6|6)!")

    def end_game(self):
        """
            Handle end-of-game display and exit. Displays who wins.
                """
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
            msg += f"\n\nTeam 0 score: {team_0_score}\nTeam 1 score: {team_1_score}"
            msg += "\n\nFinal Player Scores:\n" + team_lines

            messagebox.showinfo("Game Over", msg)
            #Performance Tracking 
            self.tracker.update_tracker_team_mode(winner, True, team_0_score, team_1_score)
            self.tracker.report()

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

            tracker_scores = [score for i, score, hand in player_scores]
            #Performance Tracking 
            self.tracker.update_tracker_4_player(winner, tracker_scores[0], tracker_scores[1], tracker_scores[2], tracker_scores[3], "1v3")
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

#This area runs the app

if __name__ == "__main__":
    team_mode = "--team" in sys.argv
    pygame.mixer.init()
    # Copyright free music to set the mood for the game. Just a fun addition.
    pygame.mixer.music.load("BGM.mp3")
    pygame.mixer.music.play(-1)

    tracker = PerformanceTracker() #tracker added   
    root = tk.Tk()
   
    app = DominoGUI(root, team_mode, tracker)
    root.mainloop()
