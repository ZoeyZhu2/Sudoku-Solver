@ -1,111 +0,0 @@
import tkinter as tk
from tkinter import font
import sudoku_solver as solver

import tkinter as tk
from tkinter import font
import sudoku_solver as solver

class HomeScreen(tk.Frame):
    def __init__(self, parent, app):
        # parent = the container
        # app = the App window (so we can call app.show_frame())
        super().__init__(parent)  # creates the frame
        self.app = app  # store reference to app so we can call show_frame()
        self.create_widgets()
        
    def create_widgets(self):
            #title
        tk.Label(
            self,
            text="Sudoku",
            bg="#FFFFFF",
            fg="#121212",
            font=("Helvetica", 48, "bold")
        ).pack(pady=40)
        
        # mode 1 button
        tk.Button(
            self,
            text="Puzzle Solver",
            command=lambda: self.app.show_frame(Mode1Screen)
        ).pack(pady=10)

        # mode 2 button
        tk.Button(
            self,
            text="Solve a Puzzle",
            command=lambda: self.app.show_frame(Mode2Screen)
        ).pack(pady=10)
    
class Mode1Screen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#FFFFFF")
        self.app = app

class Mode2Screen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#FFFFFF")
        self.app = app

class App(tk.Tk): #inherist from tk.Tk the main window
    def __init__(self):
        super().__init__() #creating window
        self.title("Sudoku")
        self.resizable(False, False) #not resizable!
        
        # color scheme
        self.BG = "#FFFFFF"        # white background
        self.DARK_BLUE = "#1B4F8A" # dark blue
        self.LIGHT_BLUE = "#A8C8E8" # light blue highlight
        self.BLACK = "#121212"      # near black
        
        self.configure(bg=self.BG)
        
        # container holds all frames
        container = tk.Frame(self, bg=self.BG)
        container.pack(fill="both", expand=True) #fill whole window
        
        self.frames = {} #dict of all scree s
        for Screen in (HomeScreen, Mode1Screen, Mode2Screen):
            frame = Screen(container, self) #putting each screen in the window
            self.frames[Screen] = frame #puts the frame in the dictionary
            frame.grid(row=0, column=0, sticky="nsew") #stack frames on top of each other
        
        self.show_frame(HomeScreen) #show home screen first
    
    def show_frame(self, screen):
        self.frames[screen].tkraise()  # brings that frame to front

if __name__ == "__main__":
    app = App()
    app.mainloop()
#The plan:
# Color scheme: like NYT but Columbia blue mode. Very vibrant colors. Black, white, and light blude mostly, with some dark blue.
# Clicking a cell highlights it light blue.
# can traverse cells by clicking or with arrow keys.
# There will be a button to show errors, which will highlight the cell light red.
# Buttons:
# For mode 1, show next step, show previous step, show original, show final like Chess.com game review. 
# For mode 2, pause, solve, reset, hint, check, new puzzle buttons.
# Timer only for mode 2.
# Difficulty selector on mode 2 like on NYT.

# Overall structure before coding: 1 file, separate classes
# Two screens:
# Home screen — choose Mode 1 or Mode 2, with NYT-style clean design
# Game screen — the actual board with buttons
# Mode 1 game screen:
# 9x9 board display and must input all the numbers a player has
# convert blanks to 0s
# check if it is solvable
# Show original / Step back / Step forward / Show final buttons
# At each step, Current strategy being used displayed
# Mode 2 game screen:
# Difficulty selector (Easy/Medium/Hard/Evil)
# 9x9 board display with given numbers filled in and unchangeable. Make these numbers bold black.
# Timer showing the time elapsed. Automatically pause if user leaves the window/tab
# Pausing should show an overlay blocking the 9x9 board with "Game Paused" text and a Click to Resume butotn
# Pause / Solve / Reset / Hint / Check / New Puzzle buttons

