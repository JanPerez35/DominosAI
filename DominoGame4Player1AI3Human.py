import random
from collections import deque
import tkinter as tk
from tkinter import messagebox
#importing the performance tracker
from PerformanceMeasure import PerformanceTracker
import copy
import pygame
import sys

"""
Domino game utilizing four Monte Carlo AI opponent

This class defines the DominoGame logic and a corresponding GUI class
called DominoGUI to play a dominos game between a human and an AI. This
game specifically utilizes rules from Puerto Rico so it is not a traditional
domino score based game. 
"""

class DominoGame:
    """
    A class to model the state and logic of a 4-player domino game.

    The game supports team play (3 humans vs 1 AI) or a free-for-all mode.
    Tiles are dealt randomly, the game starts with the double-six tile,
    and players take turns placing valid tiles or drawing from the stock.

    Attributes:
        team_mode (bool): Whether the game is played in teams.
        layout (str): Layout string ('p1', 'p2', or 'p3') defining human-AI team configurations.
        teams (list[list[int]]): A list of two lists indicating player indices per team (only in team mode).
        tiles (list[tuple[int, int]]): The full shuffled domino tile set.
        players (list[list[tuple[int, int]]]): A list containing 4 lists of player hands.
        stock (list[tuple[int, int]]): Remaining tiles not dealt to any player.
        board (deque[tuple[int, int]]): The current sequence of tiles played on the table.
        board_owners (deque[int]): Tracks which player placed each tile on the board.
        current_player (int): Index of the player whose turn it is.
        passes (int): Consecutive pass counter (used to determine blocked games).
    """
    def __init__(self,team_mode,layout):
        """
        Initialize the game state, assign teams, shuffle tiles, and determine the starting player.

        Args:
            team_mode (bool): If True, players are grouped into two teams (3 humans vs 1 AI).
            layout (str): Determines which human player is teamed with the AI. 
                          Accepts 'p1', 'p2', or 'p3', meaning:
                          - 'p1': Player 1 (index 0) + AI (index 3) vs Player 2 + Player 3
                          - 'p2': Player 2 + AI vs Player 1 + Player 3
                          - 'p3': Player 3 + AI vs Player 1 + Player 2
        """

        self.layout = layout

        # define the two teams based on which human pairs with the AI
        if team_mode:
            if layout == "p1":
                # Player 1 (0) + AI (3) vs Player 2 (1)+Player 3 (2)
                self.teams = [[0, 3], [1, 2]]
            elif layout == "p2":
                # Player 2 + AI vs Player 1+Player 3
                self.teams = [[1, 3], [0, 2]]
            else:  # "p3"
                # Player 3 + AI vs Player 1+Player 2
                self.teams = [[2, 3], [0, 1]]
        else:
            # free‑for‑all: no teams
            self.teams = []

        self.tiles = [(i, j) for i in range(7) for j in range(i, 7)]
        random.shuffle(self.tiles)
        # Deal 7 tiles to each of 4 players (players: 0, 1, and 2 = human; 3 = AI)
        self.players = [self.tiles[i*7:(i+1)*7] for i in range(4)]
        self.stock = self.tiles[28:]
        self.board = deque()
        # To track who placed each tile
        self.board_owners = deque()  
        self.current_player = 0
        self.passes = 0
        self.team_mode = team_mode
        # Find the (6,6) to start the game
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
        Check if a tile can be played at a given end of the board.
        
        Args:
            tile (tuple[int, int]): The tile being evaluated.
            end (int): The open end of the board to match.

        Returns:
            bool: True if the tile can be played at the specified end.
        """
        return end in tile

    def get_valid_moves(self, hand):
        """
        Get a list of valid moves for the current player based on their hand and the current board.

        Args:    
            hand (list[tuple[int, int]]): The player's hand (a list of tiles).

        Returns:
            list[tuple[int, int]]: List of tiles that are valid moves.
        """
        if not self.board:
            return hand
        left, right = self.board[0][0], self.board[-1][1]
        return [t for t in hand if self.is_valid_move(t, left) or self.is_valid_move(t, right)]

    def draw_from_stock(self, player):
        """
        Draw a tile from the stock and add it to the player's hand.

        Args:
            player (int): The index of the player drawing the tile.

        Returns:
            tuple[int, int] | None: The tile drawn from the stock, or None if the stock is empty.
        """
        if self.stock:
            drawn_tile = self.stock.pop()
            self.players[player].append(drawn_tile)
            return drawn_tile
        return None

    def play_tile(self, player, tile):
        """
        Play a tile on the board, ensuring it matches one of the open ends.

        Args:
            player (int): The index of the player playing the tile.
            tile (tuple[int, int]): The tile to be played.
        
        Raises:
            ValueError: If the tile is not valid.
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
        Increment the pass counter when a player cannot make a valid move.
        """
        self.passes += 1

    def is_game_over(self):
        """
        Check if the game is over based on the conditions: all players have passed or a player has emptied their hand.

        Returns:
            bool: True if the game is over, False otherwise.
        """
        return any(len(p) == 0 for p in self.players) or self.passes >= 4

    def get_winner(self):
        """
        Determine the winner of the game.

        If a player emptied their hand, they win. Otherwise, the player with
        the lowest pip count wins; ties return -1.

        Returns:
            int or str: Winning player index (0-3) in free-for-all, or
                        "Team 1"/"Team 2" in team mode, or -1 for a tie.
        """
        # Check if anyone has emptied their hand
        for i, hand in enumerate(self.players):
            if len(hand) == 0:
                # If in team mode, return the winning team based on the player's index
                if self.team_mode:
                    if i in self.teams[0]:  
                        # Player is in team 1
                        return "Team 1"
                    else:
                        # Player is in team 2
                        return "Team 2"
                else:
                    # Player index in free-for-all
                    return i  

        # No one has emptied their hand, calculate total pip count
        if self.team_mode:
            team_0_score = sum(tile[0] + tile[1] for i in [0, 2] for tile in self.players[i])
            team_1_score = sum(tile[0] + tile[1] for i in [1, 3] for tile in self.players[i])
            if team_0_score < team_1_score:
                return "Team 1"
            elif team_1_score < team_0_score:
                return "Team 2"
            else:
                # Tie
                return -1  
        else:
            player_scores = []
            for i, hand in enumerate(self.players):
                total = sum(tile[0] + tile[1] for tile in hand)
                player_scores.append((i, total))

            player_scores.sort(key=lambda x: x[1])
            lowest_score = player_scores[0][1]
            tied_players = [i for i, score in player_scores if score == lowest_score]

            if len(tied_players) > 1:
                # Tie
                return -1 
            else:
                # Winning player index
                return player_scores[0][0]  
            
# -------------- GUI --------------

class DominoGUI:
    """
    The main graphical user interface (GUI) class for the domino game.
    It handles user interaction, drawing the game board, displaying hands,
    and managing the flow of the game.
    """
    def __init__(self, root, team_mode, layout, tracker):
        """
        Initializes the game interface, including the setup for the game board,
        player hands, and control buttons.
        
        Args:
            root (tk.Tk): The root Tkinter window.
            team_mode (bool): Flag indicating whether the game is in team mode.
            layout (str): Defines the player layout for the game.
            tracker (PerformanceTracker): A performance tracker instance.
        """
        self.root = root
        self.root.title("Domino - 3 Players vs 1 AI (Pass-and-Play)")
        self.tracker = PerformanceTracker() #tracker added
        # initialize game logic with team_mode and layout
        self.game = DominoGame(team_mode, layout)

        # Color mapping
        if team_mode:
            self.player_colors = ['blue', 'red', 'blue', 'red']
        else:
            self.player_colors = ['blue', 'red', 'green', 'purple']

        self.game_over = False

        # Main board frame
        self.board_frame = tk.Frame(root)
        self.board_frame.pack(pady=10)

        self.canvas_width = 1000
        self.canvas_height = 300

        self.canvas_scrollbar = tk.Scrollbar(self.board_frame, orient=tk.HORIZONTAL)
        self.canvas_scrollbar.pack(fill=tk.X)

        self.board_canvas = tk.Canvas(
            self.board_frame,
            width=self.canvas_width,
            height=self.canvas_height,
            bg='light gray',
            xscrollcommand=self.canvas_scrollbar.set,
            scrollregion=(0, 0, 5000, 300)
        )
        self.board_canvas.pack(side=tk.TOP, fill=tk.X)
        self.canvas_scrollbar.config(command=self.board_canvas.xview)

        # Scroll buttons
        self.scroll_button_frame = tk.Frame(self.board_frame)
        self.scroll_button_frame.pack(pady=5)
        tk.Button(self.scroll_button_frame, text="Scroll Left", command=self.scroll_left).pack(side=tk.LEFT, padx=5)
        tk.Button(self.scroll_button_frame, text="Scroll Right", command=self.scroll_right).pack(side=tk.LEFT, padx=5)

        # Hand frame
        self.hand_frame = tk.Frame(root)
        self.hand_frame.pack(pady=10)

        # Info and controls
        self.info_frame = tk.Frame(root)
        self.info_frame.pack()
        self.controls_frame = tk.Frame(root)
        self.controls_frame.pack(pady=10)

        # Legend
        self.legend_frame = tk.Frame(root)
        self.legend_frame.pack(pady=5)
        tk.Label(self.legend_frame, text="Legend:").pack(side=tk.LEFT)
        if self.game.team_mode:
            for team_index, team in enumerate(self.game.teams):
                for p in team:
                    name = ["Player 1","Player 2","Player 3","AI 1"][p]
                    tk.Label(
                        self.legend_frame,
                        text=f"{name} (Team {team_index+1})",
                        fg=self.player_colors[p],
                        font=("Arial", 10, "bold")
                    ).pack(side=tk.LEFT, padx=5)
        else:
            names = ["Player 1","Player 2","Player 3","AI 1"]
            for i, name in enumerate(names):
                tk.Label(
                    self.legend_frame,
                    text=name,
                    fg=self.player_colors[i],
                    font=("Arial", 10, "bold")
                ).pack(side=tk.LEFT, padx=5)

        # Control buttons
        tk.Button(self.controls_frame, text="Pass Turn", command=self.pass_turn).pack(side=tk.LEFT, padx=5)
        tk.Button(self.controls_frame, text="Draw Tile", command=self.draw_tile).pack(side=tk.LEFT, padx=5)
        self.music_on = True
        tk.Button(self.controls_frame, text="Mute Music", command=self.toggle_music).pack(side=tk.LEFT, padx=5)
        #Music buttons
        self.music_on = True
        self.music_button = tk.Button(self.controls_frame, text="Mute Music", command=self.toggle_music)
        self.music_button.pack(side=tk.LEFT, padx=5)
        # Status and AI tile count
        self.status_label = tk.Label(self.info_frame, text="Your turn!", font=("Arial", 12))
        self.status_label.pack(side=tk.LEFT, padx=10)
        self.ai_label = tk.Label(self.info_frame, text=f"AI 1 has {len(self.game.players[3])} tiles", font=("Arial", 10))
        self.ai_label.pack(side=tk.RIGHT, padx=5)

        # For pass-and-play
        self.last_human = None

        # Initial draw
        self.draw_board()
        self.draw_hand()
        if self.game.current_player not in [0, 1, 2]:
            self.status_label.config(text=f"AI starts with (6|6)")
            self.root.after(1000, self.ai_turn)
        else:
            self.status_label.config(text=self.human_status_text())

    def human_status_text(self):
        """
        Returns the appropriate status text for the current human player.
        
        Returns:
            str: A status message indicating whose turn it is.
        """
        if self.game.current_player == 0:
            return "Your turn! (Player 1)"
        elif self.game.current_player == 1:
            return "Your turn! (Player 2)"
        elif self.game.current_player == 2:
            return "Your turn! (Player 3)"
        else:
            return ""

    def scroll_left(self):
        """
        Scrolls the board view to the left.
        """
        self.board_canvas.xview_scroll(-1, "units")

    def scroll_right(self):
        """
        Scrolls the board view to the right.
        """
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
        Draws the current state of the game board on the canvas.
        Updates the scroll region and view based on the tiles.
        """
        self.board_canvas.delete("all")
        # Start position for board drawing
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

            self.board_canvas.config(scrollregion=(0, 0, max(x + 100, 1000), 300))
            if tile_positions:
                latest_x = tile_positions[-1][0]
                canvas_view_x = max(latest_x - self.canvas_width // 2, 0)
                self.board_canvas.xview_moveto(canvas_view_x / (max(x + 100, 1000)))

    def draw_hand(self):
        """
        Draws the current player's hand of tiles on the screen.
        It also disables buttons for invalid moves.
        """
        for widget in self.hand_frame.winfo_children():
            widget.destroy()
        player = self.game.current_player
        hand = self.game.players[player]
        valid_moves = self.game.get_valid_moves(hand)
        # Display the complete hand (7 tiles at game start, or remaining tiles)
        for tile in hand:
            tile_str = f"[{tile[0]}|{tile[1]}]"
            btn = tk.Button(self.hand_frame, text=tile_str, font=('Courier', 12), relief='raised',
                            fg=self.player_colors[player],
                            state=tk.NORMAL if tile in valid_moves else tk.DISABLED,
                            command=lambda t=tile: self.play_tile(t))
            btn.pack(side=tk.LEFT, padx=4)

    def show_pass_screen(self, next_player):
        """
        Displays a pass screen to prompt the next human player to press "Ready."
        
        Args:
            next_player (int): The player number (0, 1, 2) who should press "Ready."
        """
        print(f"Showing pass screen for player {self.game.current_player}")
        pass_screen = tk.Toplevel(self.root)
        pass_screen.grab_set()
        pass_screen.geometry("400x200+400+200")
        pass_screen.title("Pass Device")
        msg = ""
        if next_player == 0:
            msg = "Pass device to Player 1\n\n(Ensure previous hand is not visible.)"
        elif next_player == 1:
            msg = "Pass device to Player 2\n\n(Ensure previous hand is not visible.)"
        elif next_player == 2:
            msg = "Pass device to Player 3\n\n(Ensure previous hand is not visible.)"
        label = tk.Label(pass_screen, text=msg, font=("Arial", 14))
        label.pack(expand=True)
        btn = tk.Button(pass_screen, text="I'm Ready", font=("Arial", 12),
                        command=lambda: self.close_pass_screen(pass_screen))
        btn.pack(pady=10)
        # Wait until user clicks ready.
        self.root.wait_window(pass_screen)

    def close_pass_screen(self, window):
        """
        Closes the pass screen and updates the status for the new human turn.
        
        Args:
            window (tk.Toplevel): The window to be closed.
        """
        window.destroy()
        # After closing, update status and show hand for new human turn.
        self.status_label.config(text=self.human_status_text())
        self.draw_hand()

    def after_move(self):
        """
        Updates the board and moves to the next turn. If the game is over, it ends the game.
        If it's a human player's turn, it shows the pass screen.
        """
        self.draw_board()
        self.update_ai_tile_counts()
        if self.game.is_game_over():
            self.end_game()
        else:
            # If next turn is human, check if pass screen is needed.
            if self.game.current_player in [0, 1, 2]:
                # Always show pass screen between human turns
                #if self.last_human is None or self.last_human != self.game.current_player:
                print(f"Showing pass screen for player {self.game.current_player}")
                self.show_pass_screen(self.game.current_player)
                self.last_human = self.game.current_player
                self.status_label.config(text=self.human_status_text())
                self.draw_hand()
            else:
                # reset since it's an AI's turn
                self.last_human = None 
                self.root.after(500, self.ai_turn)

    def play_tile(self, tile):
        """
        Handles playing a tile by the current player and updates the game state.

        Args:
            tile (tuple[int, int]): The tile to be played.

        Raises:
            Exception: If the tile cannot be played (invalid move), an error message will be shown.
        """
        try:
            # Use the current player's hand (will be 0 or 2)
            self.game.play_tile(self.game.current_player, tile)
            self.game.current_player = (self.game.current_player + 1) % 4
            self.after_move()
        except Exception as e:
            messagebox.showerror("Invalid Move", str(e))

    def pass_turn(self):
        """
        Passes the turn to the next player.
        """
        self.game.pass_turn()
        self.game.current_player = (self.game.current_player + 1) % 4
        self.after_move()

    def draw_tile(self):
        """
        Draws a tile for the current player.
        """
        tile = self.game.draw_from_stock(self.game.current_player)
        if tile:
            self.status_label.config(text=f"You drew {tile}")
        else:
            self.status_label.config(text="Stock is empty")
        self.draw_hand()

    def ai_turn(self):
        """
        Handles the AI player's turn using Monte Carlo simulation. If it's not the AI's turn or the game is over, 
        it updates the UI. If valid moves exist, the AI plays a move, otherwise, it draws from the stock. 
        If no move is possible, the AI passes. Updates the board and advances the turn.
        """
        if self.game.current_player in [0, 1, 2] or self.game.is_game_over():
            if self.game.is_game_over():
                self.end_game()
            else:
                self.status_label.config(text=self.human_status_text())
                self.draw_hand()
            return

        cp = self.game.current_player
        hand = self.game.players[cp]
        valid_moves = self.game.get_valid_moves(hand)
        # If no valid move exists, draw from stock until a move is possible or stock empty
        while not valid_moves and self.game.stock:
            self.game.draw_from_stock(cp)
            valid_moves = self.game.get_valid_moves(self.game.players[cp])

        # Use monte-carlo simulation for AI move if possible
        move = self.monte_carlo_ai_move(cp, simulations=25) if valid_moves else None
        if move:
            self.game.play_tile(cp, move)
            self.status_label.config(text=f"AI played {move}")
        else:
            self.game.pass_turn()
            self.status_label.config(text=f"AI passed")
        self.draw_board()
        self.update_ai_tile_counts()
        self.game.current_player = (self.game.current_player + 1) % 4
        self.root.after(1000, self.after_move)

    def monte_carlo_ai_move(self, player_index, simulations=30):
        """
        Uses Monte Carlo simulation to determine the best move for the AI.

        The method simulates multiple games by playing valid moves and scoring them based on how many times 
        the AI wins in the simulation. It returns the move that maximizes the AI's chances of winning.

        Args:
            player_index (int): The index of the AI player (3 in a 3v1 setup).
            simulations (int): The number of simulations to run for move evaluation.

        Returns:
            tuple: The best move for the AI, or None if no valid move exists.
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
        Simulates a random playthrough of the game to determine the winner.

        The method plays out the game randomly from the current state by choosing random valid moves for 
        each player, drawing from the stock when necessary, and passing turns when no valid moves exist.

        Args:
            sim_game (DominoGame): A deep copy of the current game to simulate.

        Returns:
            int: The index of the winning player.
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
        Updates the label displaying the number of tiles remaining for AI players.
        """
        self.ai_label.config(text=f"AI 1 has {len(self.game.players[3])} tiles")

    
    def start_new_game(self, teamMode, layout):
        """
        Starts a new game with the specified team mode and player layout.

        The method resets the game state, clears the board and player hands, and initializes a fresh game.

        Args:
            teamMode (bool): Flag to indicate whether the game is in team mode.
            layout (str): The layout configuration of players (e.g., "p1", "p2", "p3").
        """
        self.game = DominoGame(teamMode, layout)
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

        if self.game.current_player in [2]:
            self.status_label.config(text=f"AI {1 if self.game.current_player == 1 else 2} starts with (6|6)!")
            self.root.after(1000, self.ai_turn)
        else:
            self.status_label.config(text=f"You start with (6|6)!")

    def end_game(self):
        """
        Ends the game and displays the final scores and winner.

        The method calculates the scores for each player, determines the winner, and displays a message with
        the final scores. If the game was played in team mode, the team scores are also displayed.

        After the game ends, the user is prompted with an option to start a new game or quit.
        """
        winner = self.game.get_winner()
        player_scores = [
            (i, sum(t[0] + t[1] for t in hand), hand)
            for i, hand in enumerate(self.game.players)
        ]

        if self.game.team_mode:
            # Team-based scoring
            team_0_score = sum(score for i, score, _ in player_scores if i in [0, 2])
            team_1_score = sum(score for i, score, _ in player_scores if i in [1, 3])

            team_lines = "\n".join(
                f"Player {i} ({'You' if i in [0, 1, 2] else 'AI'}): {score} points | Tiles: {hand}"
                for i, score, hand in player_scores
            )
            msg = "🤝 It's a tie!" if winner == -1 else f"🎉 {winner} wins!"
            msg += f"\n\nTeam A score: {team_0_score}\nTeam B score: {team_1_score}"
            msg += "\n\nFinal Player Scores:\n" + team_lines

            messagebox.showinfo("Game Over", msg)
            #Performance Tracking 
            self.tracker.update_tracker_team_mode(winner, True, team_0_score, team_1_score)
            self.tracker.report()

        else:
            # Free-for-all scoring
            score_lines = "\n".join(
                f"Player {i} ({'You' if i in [0, 1, 2] else 'AI'}): {score} points | Tiles: {hand}"
                for i, score, hand in player_scores
            )

            if winner in [0,1,2]:
                msg = "🎉 You win!"
            elif winner == -1:
                msg = "🤝 It's a tie!"
            else:
                msg = f"🤖 AI {1} wins!"
            msg += "\nFinal Scores:\n" + score_lines
            messagebox.showinfo("Game Over", msg)

            tracker_scores = [score for i, score, hand in player_scores]
            #Performance Tracking 
            self.tracker.update_tracker_4_player(winner, tracker_scores[0], tracker_scores[1], tracker_scores[2], tracker_scores[3], "3v1")
            self.tracker.report()

        #Play again option
        play_again = messagebox.askyesno(
            title="Play again?",
            message="Would you like to play again?"
        )
        if play_again:
            self.start_new_game(team_mode, layout)
        else:
            self.root.quit()

# -------------- Run the App --------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--team",
        action="store_true",
        help="Enable team mode"
    )
    parser.add_argument(
        "--layout",
        choices=["p1", "p2", "p3"],
        default="p1",
        help=(
            "p1: Player 1 + AI vs Players 2&3\n"
            "p2: Player 2 + AI vs Players 1&3\n"
            "p3: Player 3 + AI vs Players 1&2"
        )
    )
    args = parser.parse_args()

    team_mode = args.team
    layout   = args.layout

    pygame.mixer.init()
    pygame.mixer.music.load("BGM.mp3")
    pygame.mixer.music.play(-1)

    root = tk.Tk()
    #tracker added 
    tracker = PerformanceTracker() 
    app = DominoGUI(root, team_mode, layout, tracker)
    root.mainloop()
    sys.exit()

