import pygame
import numpy as np
import random
import sys
from IPython.display import display, clear_output
import matplotlib.pyplot as plt
import time
import ipywidgets as widgets

class EightPuzzleGame:
    def __init__(self, initial_state=None, goal_state=None):
        # Default initial state
        if initial_state is None:
            self.board = np.array([[4, 1, 3], [0, 8, 5], [2, 7, 6]])
        else:
            self.board = np.array(initial_state)
        
        # Default goal state
        if goal_state is None:
            self.goal_state = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 0]])
        else:
            self.goal_state = np.array(goal_state)
        
        self.move_history = []
        # Find blank position
        blank_pos = np.where(self.board == 0)
        self.blank_row, self.blank_col = blank_pos[0][0], blank_pos[1][0]
    
    def get_board(self):
        return self.board
    
    def get_move_history(self):
        return self.move_history
    
    def is_solved(self):
        return np.array_equal(self.board, self.goal_state)
    
    def move_blank(self, direction):
        new_row, new_col = self.blank_row, self.blank_col
        
        # Convert direction to lowercase for consistency
        direction = direction.lower() if isinstance(direction, str) else direction
        
        if direction == 'up' and self.blank_row > 0:
            new_row = self.blank_row - 1
        elif direction == 'down' and self.blank_row < 2:
            new_row = self.blank_row + 1
        elif direction == 'left' and self.blank_col > 0:
            new_col = self.blank_col - 1
        elif direction == 'right' and self.blank_col < 2:
            new_col = self.blank_col + 1
        else:
            return False
        
        # Swap the blank with the tile
        self.board[self.blank_row, self.blank_col] = self.board[new_row, new_col]
        self.board[new_row, new_col] = 0
        self.blank_row, self.blank_col = new_row, new_col
        self.move_history.append(direction)
        return True
    
    def click_tile(self, row, col):
        # Check if the tile is adjacent to the blank
        if (abs(row - self.blank_row) == 1 and col == self.blank_col) or \
           (abs(col - self.blank_col) == 1 and row == self.blank_row):
            
            if row < self.blank_row:
                return self.move_blank('up')
            elif row > self.blank_row:
                return self.move_blank('down')
            elif col < self.blank_col:
                return self.move_blank('left')
            elif col > self.blank_col:
                return self.move_blank('right')
        
        return False
    
    def shuffle(self, moves=50):
        directions = ['up', 'down', 'left', 'right']
        for _ in range(moves):
            direction = random.choice(directions)
            self.move_blank(direction)
        self.move_history = []  # Reset move history after shuffling

class PuzzleGame:
    def __init__(self, initial_state=None, goal_state=None, solution=None):
        # Initialize pygame
        pygame.init()
        self.width, self.height = 300, 400  # Increased height to accommodate move history
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("8-Puzzle Game")
        
        # Colors and fonts
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (200, 200, 200)
        self.BLUE = (0, 120, 255)
        self.GREEN = (0, 180, 0)
        self.RED = (255, 0, 0)
        self.YELLOW = (255, 255, 0)
        self.FONT = pygame.font.Font(None, 36)
        self.SMALL_FONT = pygame.font.Font(None, 24)
        self.TINY_FONT = pygame.font.Font(None, 16)
        
        # Default initial and goal states
        if initial_state is None:
            initial_state = [[4, 1, 3], [0, 8, 5], [2, 7, 6]]
        if goal_state is None:
            goal_state = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
            
        # Game instance
        self.game = EightPuzzleGame(initial_state, goal_state)
        self.tile_size = 100
        self.running = True
        
        # Solution replay variables
        self.solution = solution
        if solution:
            self.solution = [step.lower() for step in solution]  # Convert all to lowercase
        self.solution_index = 0
        self.solution_playing = False
        self.solution_delay = 500  # ms between moves
        self.last_solution_move_time = 0
        
        # Animation variables
        self.animating = False
        self.animation_frames = 10
        self.current_frame = 0
        self.source_pos = None
        self.target_pos = None
        self.moving_tile = None
        
        # Move history display
        self.history_display_count = 15  # Number of moves to display
    
    def animate_move(self, from_row, from_col, to_row, to_col, tile_value):
        """Set up animation parameters"""
        self.animating = True
        self.current_frame = 0
        self.source_pos = (from_col * self.tile_size, from_row * self.tile_size)
        self.target_pos = (to_col * self.tile_size, to_row * self.tile_size)
        self.moving_tile = tile_value
        
    def draw_board(self):
        """Draw the current game board"""
        self.screen.fill(self.WHITE)
        board = self.game.get_board()
        
        # Draw grid and static tiles
        for i in range(3):
            for j in range(3):
                # Draw grid cell
                pygame.draw.rect(self.screen, self.BLACK, 
                                (j * self.tile_size, i * self.tile_size, 
                                 self.tile_size, self.tile_size), 2)
                
                # If we're not animating this tile, draw it normally
                if not self.animating or (i, j) != (self.game.blank_row, self.game.blank_col):
                    if board[i, j] != 0:  # Only draw numbers for non-blank tiles
                        text = self.FONT.render(str(board[i, j]), True, self.BLACK)
                        text_rect = text.get_rect(center=(j * self.tile_size + self.tile_size//2, 
                                                        i * self.tile_size + self.tile_size//2))
                        self.screen.blit(text, text_rect)
        
        # Draw animated tile if needed
        if self.animating and self.current_frame < self.animation_frames:
            progress = self.current_frame / self.animation_frames
            x = int(self.source_pos[0] + (self.target_pos[0] - self.source_pos[0]) * progress)
            y = int(self.source_pos[1] + (self.target_pos[1] - self.source_pos[1]) * progress)
            
            # Draw moving tile
            pygame.draw.rect(self.screen, self.GRAY, (x, y, self.tile_size, self.tile_size))
            pygame.draw.rect(self.screen, self.BLACK, (x, y, self.tile_size, self.tile_size), 2)
            
            # Highlight the blank tile's movement path with semi-transparent red
            pygame.draw.rect(self.screen, (*self.RED, 128), (x, y, self.tile_size, self.tile_size), 2)
            
            if self.moving_tile != 0:  # Only draw number for non-blank tiles
                text = self.FONT.render(str(self.moving_tile), True, self.BLACK)
                text_rect = text.get_rect(center=(x + self.tile_size//2, y + self.tile_size//2))
                self.screen.blit(text, text_rect)
            
            self.current_frame += 1
            if self.current_frame >= self.animation_frames:
                self.animating = False
        
        # Draw buttons
        shuffle_rect = pygame.Rect(20, 320, 80, 25)
        reset_rect = pygame.Rect(110, 320, 80, 25)
        
        # Add solution replay button if solution is provided
        if self.solution:
            play_rect = pygame.Rect(200, 320, 80, 25)
            pygame.draw.rect(self.screen, self.YELLOW, play_rect)
            play_text = self.SMALL_FONT.render("Play Sol", True, self.BLACK)
            self.screen.blit(play_text, (play_rect.x + 10, play_rect.y + 5))
        
        pygame.draw.rect(self.screen, self.BLUE, shuffle_rect)
        pygame.draw.rect(self.screen, self.GREEN, reset_rect)
        
        shuffle_text = self.SMALL_FONT.render("Shuffle", True, self.WHITE)
        reset_text = self.SMALL_FONT.render("Reset", True, self.WHITE)
        
        self.screen.blit(shuffle_text, (shuffle_rect.x + 15, shuffle_rect.y + 5))
        self.screen.blit(reset_text, (reset_rect.x + 20, reset_rect.y + 5))
        
        # Draw move history title
        history_title = self.SMALL_FONT.render("Blank Tile Movement History:", True, self.BLACK)
        self.screen.blit(history_title, (10, 350))
        
        # Draw move history
        move_history = self.game.get_move_history()
        history_to_show = move_history[-self.history_display_count:] if move_history else []
        
        # Create a formatted representation of the history using plain text directions
        history_text = ""
        direction_symbols = {
            'up': 'U', 
            'down': 'D', 
            'left': 'L', 
            'right': 'R'
        }
        
        for i, move in enumerate(history_to_show):
            history_text += direction_symbols.get(move, move) + " "
            if (i + 1) % 15 == 0:  # Line break every 15 moves
                history_text += "\n"
                
        if history_text:
            # Render each line of the history text
            lines = history_text.split('\n')
            for i, line in enumerate(lines):
                history_line = self.SMALL_FONT.render(line, True, self.BLACK)
                self.screen.blit(history_line, (10, 375 + i * 18))
        else:
            no_history = self.SMALL_FONT.render("No moves yet", True, self.GRAY)
            self.screen.blit(no_history, (10, 375))
        
        pygame.display.flip()
    
    def handle_click(self, pos):
        """Handle mouse clicks on the board or buttons"""
        x, y = pos
        
        # Check if clicked on buttons
        if 320 <= y <= 345:
            if 20 <= x <= 100:  # Shuffle button
                self.game.shuffle()
                self.solution_playing = False  # Stop solution playback if in progress
            elif 110 <= x <= 190:  # Reset button
                self.game = EightPuzzleGame()
                self.solution_playing = False  # Stop solution playback if in progress
            elif self.solution and 200 <= x <= 280:  # Play solution button
                self.solution_playing = True
                self.solution_index = 0
                self.last_solution_move_time = pygame.time.get_ticks()
        
        # Check if clicked on a tile
        elif y < 300:
            row = y // self.tile_size
            col = x // self.tile_size
            self.game.click_tile(row, col)
            
            # Check if solved after move
            if self.game.is_solved():
                print("Puzzle Solved!")
                print("Move History:", self.game.get_move_history())
    
    def run(self):
        """Main game loop"""
        clock = pygame.time.Clock()
        self.running = True
        
        while self.running:
            current_time = pygame.time.get_ticks()
            
            # Handle solution playback
            if self.solution_playing and self.solution_index < len(self.solution):
                if current_time - self.last_solution_move_time > self.solution_delay:
                    self.game.move_blank(self.solution[self.solution_index])
                    self.solution_index += 1
                    self.last_solution_move_time = current_time
                    
                    # Check if solution playback is complete
                    if self.solution_index >= len(self.solution):
                        self.solution_playing = False
                        if self.game.is_solved():
                            print("Solution successful! Puzzle solved!")
                        else:
                            print("Solution completed but puzzle not solved.")
            
            self.draw_board()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and not self.solution_playing:
                    self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN and not self.solution_playing:
                    if event.key == pygame.K_UP:
                        self.game.move_blank('up')
                    elif event.key == pygame.K_DOWN:
                        self.game.move_blank('down')
                    elif event.key == pygame.K_LEFT:
                        self.game.move_blank('left')
                    elif event.key == pygame.K_RIGHT:
                        self.game.move_blank('right')
                    
                    # Check if solved after key move
                    if self.game.is_solved():
                        print("Puzzle Solved!")
                        print("Move History:", self.game.get_move_history())
            
            clock.tick(30)
        
        pygame.quit()
    
    def run_in_jupyter(self):
        """Run the game in Jupyter notebook"""
        import matplotlib.pyplot as plt
        from IPython.display import clear_output
        import time
        
        # Initial shuffle
        self.game.shuffle()
        
        while True:
            # Draw the board
            self.draw_board()
            
            # Convert pygame surface to an image for display in Jupyter
            data = pygame.image.tostring(self.screen, 'RGB')
            img = np.frombuffer(data, dtype=np.uint8)
            img = img.reshape((self.height, self.width, 3))
            
            # Display the image
            clear_output(wait=True)
            plt.figure(figsize=(5, 5))
            plt.imshow(img)
            plt.axis('off')
            plt.show()
            
            # Process any pending events
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.game.move_blank('up')
                    elif event.key == pygame.K_DOWN:
                        self.game.move_blank('down')
                    elif event.key == pygame.K_LEFT:
                        self.game.move_blank('left')
                    elif event.key == pygame.K_RIGHT:
                        self.game.move_blank('right')
            
            # Check if solved
            if self.game.is_solved():
                clear_output(wait=True)
                self.draw_board()
                data = pygame.image.tostring(self.screen, 'RGB')
                img = np.frombuffer(data, dtype=np.uint8)
                img = img.reshape((self.height, self.width, 3))
                plt.figure(figsize=(5, 5))
                plt.imshow(img)
                plt.axis('off')
                plt.show()
                print("Puzzle Solved! 🎉")
                print("Move History:", self.game.get_move_history())
                break
                
            # Small delay to prevent notebook from becoming unresponsive
            time.sleep(0.1)

def run_with_widgets(initial_state=None, goal_state=None, solution=None):
    """Run the game using ipywidgets (better for Jupyter)"""
    import ipywidgets as widgets
    from IPython.display import display
    from functools import partial
    
    # Initialize with defaults if not provided
    if initial_state is None:
        initial_state = [[4, 1, 3], [0, 8, 5], [2, 7, 6]]
    if goal_state is None:
        goal_state = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
    
    # Convert solution to lowercase if provided
    if solution:
        solution = [step.lower() for step in solution]
    
    # Initialize game with the specified states
    game = EightPuzzleGame(initial_state, goal_state)
    
    # Create output area for status messages
    status_output = widgets.Output()
    
    # Create buttons grid
    buttons = []
    for i in range(3):
        row = []
        for j in range(3):
            # Create button with specific ID to track position
            btn = widgets.Button(
                description="",
                layout=widgets.Layout(width='80px', height='80px', font_size='24px')
            )
            row.append(btn)
        buttons.append(row)
    
    # Create control elements
    shuffle_button = widgets.Button(
        description="Shuffle",
        button_style="primary", 
        layout=widgets.Layout(width="100px")
    )
    
    reset_button = widgets.Button(
        description="Reset",
        button_style="success", 
        layout=widgets.Layout(width="100px")
    )
    
    # Function to update the UI based on game state
    def update_ui():
        board = game.get_board()
        
        for i in range(3):
            for j in range(3):
                # Get the tile value at this position
                value = board[i, j]
                # Set button text based on value (empty string for blank tile)
                if value == 0:
                    buttons[i][j].description = ""
                    buttons[i][j].style.button_color = 'lightgray'  # Highlight blank tile
                else:
                    buttons[i][j].description = str(value)
                    buttons[i][j].style.button_color = 'white'
        
        if game.is_solved():
            with status_output:
                status_output.clear_output()
                print(f"Puzzle solved! 🎉")
                print(f"Move history: {game.get_move_history()}")
        else:
            with status_output:
                status_output.clear_output()
                print("Click on a tile adjacent to the blank space to move it")
    
    # Create tile click handler
    def on_tile_click(i, j):
        game.click_tile(i, j)
        update_ui()
    
    # Create shuffle handler
    def on_shuffle(b):
        # Reset to default shuffled state
        game.board = np.array([[4, 1, 3], [0, 8, 5], [2, 7, 6]])
        # Update blank position to match the new board
        game.blank_row = 1  # Second row (index 1)
        game.blank_col = 0  # First column (index 0)
        
        game.move_history = []
        with status_output:
            status_output.clear_output()
            print("Game reset to initial state")
        update_ui()
    
    # Create reset handler
    def on_reset(b):
        # Reset to solved state
        game.board = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 0]])
        game.blank_row = 2
        game.blank_col = 2
        game.move_history = []
        with status_output:
            status_output.clear_output()
            print("Game reset to solved state")
        update_ui()
    
    # Connect handlers
    for i in range(3):
        for j in range(3):
            # Use partial to properly capture the indices
            buttons[i][j].on_click(partial(lambda b, r, c: on_tile_click(r, c), r=i, c=j))
    
    shuffle_button.on_click(on_shuffle)
    reset_button.on_click(on_reset)
    
    # Create UI layout
    grid = widgets.GridBox(
        children=[buttons[i][j] for i in range(3) for j in range(3)],
        layout=widgets.Layout(
            grid_template_columns='repeat(3, 80px)',
            grid_gap='5px', 
            width='250px',
            margin='10px'
        )
    )
    
    control_buttons = widgets.HBox([shuffle_button, reset_button], 
                                  layout=widgets.Layout(justify_content='center'))
    
    # Add play solution button if solution is provided
    if solution:
        play_solution_button = widgets.Button(
            description="Play Solution",
            button_style="warning", 
            layout=widgets.Layout(width="140px")
        )
        control_buttons = widgets.HBox([shuffle_button, reset_button, play_solution_button])
        
        # Create solution playback handler
        def on_play_solution(b):
            # Disable buttons during replay
            play_solution_button.disabled = True
            shuffle_button.disabled = True
            reset_button.disabled = True
            
            with status_output:
                status_output.clear_output()
                print("Playing solution...")
            
            # Reset to initial state
            game.board = np.array(initial_state)
            blank_pos = np.where(game.board == 0)
            game.blank_row, game.blank_col = blank_pos[0][0], blank_pos[1][0]
            game.move_history = []
            update_ui()
            
            # Play solution step by step with delay
            for i, move in enumerate(solution):
                # Need to use a sleep to show progress
                time.sleep(0.5)  # Half second delay between moves
                game.move_blank(move)
                update_ui()
            
            # Re-enable buttons
            play_solution_button.disabled = False
            shuffle_button.disabled = False
            reset_button.disabled = False
            
            with status_output:
                if game.is_solved():
                    print("Solution successfully completed! Puzzle solved!")
                else:
                    print("Solution completed but puzzle not solved.")
        
        play_solution_button.on_click(on_play_solution)
    
    # Create the full UI
    ui = widgets.VBox([
        grid, 
        control_buttons,
        status_output
    ], layout=widgets.Layout(align_items='center'))
    
    # Display once and never re-display the entire UI
    display(ui)
    
    # Set initial board (no shuffle needed)
    update_ui()
    
    return game  # Return game instance for debugging

def run_interactive_puzzle(initial_state=None, goal_state=None, solution=None):
    """Run an interactive 8-puzzle using a table-based display"""
    if initial_state is None:
        initial_state = [[4, 1, 3], [0, 8, 5], [2, 7, 6]]
    if goal_state is None:
        goal_state = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
    
    # Create game
    game = EightPuzzleGame(initial_state, goal_state)
    
    # Convert solution to lowercase if provided
    if solution:
        solution = [step.lower() for step in solution]
    
    # Status output
    status = widgets.Output()
    
    # Create buttons for each direction
    up_btn = widgets.Button(description="Up", button_style="primary")
    down_btn = widgets.Button(description="Down", button_style="primary")
    left_btn = widgets.Button(description="Left", button_style="primary")
    right_btn = widgets.Button(description="Right", button_style="primary")
    
    # Control buttons
    shuffle_btn = widgets.Button(description="Shuffle", button_style="warning")
    reset_btn = widgets.Button(description="Reset", button_style="success")
    play_btn = widgets.Button(description="Play Solution", button_style="info", 
                             layout=widgets.Layout(width="150px"))
    
    # Function to update the display
    def update_display():
        # Clear previous output
        out.clear_output(wait=True)
        
        with out:
            # Print the board
            board = game.get_board()
            print("Current board:")
            for row in board:
                print(" ".join(["_" if cell == 0 else str(cell) for cell in row]))
            print("\n")
    
    # Button click handlers
    def on_direction(b, direction):
        moved = game.move_blank(direction)
        with status:
            status.clear_output()
            if not moved:
                print(f"Cannot move {direction}")
            elif game.is_solved():
                print("Puzzle solved! 🎉")
        update_display()
    
    def on_shuffle(b):
        game.shuffle()
        with status:
            status.clear_output()
            print("Puzzle shuffled")
        update_display()
    
    def on_reset(b):
        # Reset to initial state
        game.board = np.array(initial_state)
        blank_pos = np.where(game.board == 0)
        game.blank_row, game.blank_col = blank_pos[0][0], blank_pos[1][0]
        game.move_history = []
        with status:
            status.clear_output()
            print("Game reset to initial state")
        update_display()
    
    def on_play_solution(b):
        if not solution:
            return
        
        # Disable buttons during replay
        up_btn.disabled = down_btn.disabled = left_btn.disabled = right_btn.disabled = True
        shuffle_btn.disabled = reset_btn.disabled = play_btn.disabled = True
        
        # Reset to initial state
        game.board = np.array(initial_state)
        blank_pos = np.where(game.board == 0)
        game.blank_row, game.blank_col = blank_pos[0][0], blank_pos[1][0]
        game.move_history = []
        update_display()
        
        with status:
            status.clear_output()
            print("Playing solution...")
            
        # Play each move with a delay
        for move in solution:
            time.sleep(0.5)  # Half-second delay
            game.move_blank(move)
            update_display()
        
        # Re-enable buttons
        up_btn.disabled = down_btn.disabled = left_btn.disabled = right_btn.disabled = False
        shuffle_btn.disabled = reset_btn.disabled = play_btn.disabled = False
        
        with status:
            status.clear_output()
            if game.is_solved():
                print("Puzzle solved! 🎉")
            else:
                print("Solution completed but puzzle not solved!")
    
    # Connect handlers
    up_btn.on_click(lambda b: on_direction(b, "up"))
    down_btn.on_click(lambda b: on_direction(b, "down"))
    left_btn.on_click(lambda b: on_direction(b, "left"))
    right_btn.on_click(lambda b: on_direction(b, "right"))
    shuffle_btn.on_click(on_shuffle)
    reset_btn.on_click(on_reset)
    play_btn.on_click(on_play_solution)
    
    # Layout
    direction_buttons = widgets.HBox([left_btn, up_btn, down_btn, right_btn])
    control_buttons = widgets.HBox([shuffle_btn, reset_btn])
    
    if solution:
        control_buttons = widgets.HBox([shuffle_btn, reset_btn, play_btn])
    
    # Output area for board display
    out = widgets.Output()
    
    # Assemble UI
    ui = widgets.VBox([
        out,
        direction_buttons,
        control_buttons,
        status
    ])
    
    # Show initial state
    update_display()
    
    display(ui)
    return game

# To use this function:
# run_interactive_puzzle(solution=['down', 'right', 'up', 'left', 'up', 'right', 'down', 'right', 'down'])

# Run the game if this file is executed directly
if __name__ == "__main__":
    # Check if command line arguments are provided
    if len(sys.argv) > 1:
        # Parse command line arguments for solution if provided
        solution = sys.argv[1].split(',') if len(sys.argv) > 1 else None
        game = PuzzleGame(solution=solution)
    else:
        game = PuzzleGame([[4, 1, 3], [0, 8, 5], [2, 7, 6]])
    game.run()