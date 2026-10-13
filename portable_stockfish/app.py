#!/usr/bin/env python3
"""RobSoc portable Stockfish chess GUI."""
import threading
import time
import tkinter as tk
from tkinter import messagebox, filedialog
from pathlib import Path
from datetime import date
import chess
import chess.engine
import chess.pgn

ROOT = Path(__file__).resolve().parent
ENGINE = ROOT / 'engine' / 'stockfish'
SYMBOLS = {'P':'♙','N':'♘','B':'♗','R':'♖','Q':'♕','K':'♔',
           'p':'♟','n':'♞','b':'♝','r':'♜','q':'♛','k':'♚'}

class ChessApp:
    def __init__(self, window):
        # Main window and core app state.
        self.window = window
        window.title('RobSoc Portable Chess')
        self.board = chess.Board()
        self.history = []
        self.selected = None
        self.player_color = chess.WHITE
        self.thinking = False
        self.game_id = 0
        self.engine = None
        self.status = tk.StringVar(value='Your move (White).')
        self.buttons = {}
        self.decision_started_at = None
        self.last_decision_seconds = None
        self.timer_after_id = None

        # Board area and control panel layout.
        layout = tk.Frame(window, padx=15, pady=15)
        layout.pack()
        grid = tk.Frame(layout)
        grid.grid(row=0, column=0, rowspan=5)

        # Create each square button and keep a mapping for quick refreshes.
        for row in range(8):
            for col in range(8):
                b = tk.Button(grid, font=('DejaVu Sans', 31), width=3, height=1,
                              relief='flat', command=lambda r=row,c=col:self.click(r,c))
                b.grid(row=row, column=col, sticky='nsew')
                self.buttons[row,col] = b

        # Right-hand controls: new games, save, engine time, and status messages.
        controls = tk.Frame(layout, padx=20)
        controls.grid(row=0, column=1, sticky='n')
        tk.Label(controls, text='ROBSOC CHESS', font=('Sans', 17, 'bold')).pack(pady=(0,15))
        tk.Button(controls, text='New Game — Play White', width=24,
                  command=lambda:self.new_game(chess.WHITE)).pack(pady=5)
        tk.Button(controls, text='New Game — Play Black', width=24,
                  command=lambda:self.new_game(chess.BLACK)).pack(pady=5)
        tk.Button(controls, text='Save Game (.pgn)', width=24,
                  command=self.save_game).pack(pady=5)

        # Draw a compact chess-clock illustration with live and previous decision times. 
        tk.Label(controls, text='Decision timer', font=('Sans', 11, 'bold')).pack(pady=(18,4))
        self.timer_image = tk.Canvas(controls, width=230, height=100,
                                     bg='#f4f4f4', highlightthickness=0)
        self.timer_image.pack()
        self.timer_image.create_oval(45, 5, 85, 32, fill='#343a40', outline='#343a40')
        self.timer_image.create_oval(145, 5, 185, 32, fill='#343a40', outline='#343a40')
        self.timer_image.create_rectangle(15, 22, 215, 90, fill='#343a40', outline='#343a40')
        self.timer_image.create_rectangle(25, 35, 107, 68, fill='#d7e2c5', outline='#111')
        self.timer_image.create_rectangle(123, 35, 205, 68, fill='#d7e2c5', outline='#111')
        self.timer_image.create_text(66, 28, text='NOW', fill='#343a40',
                                     font=('Sans', 8, 'bold'))
        self.timer_image.create_text(164, 28, text='LAST', fill='#343a40',
                                     font=('Sans', 8, 'bold'))
        self.current_timer_text = self.timer_image.create_text(
            66, 52, text='00:00.0', fill='#172018', font=('Monospace', 11, 'bold'))
        self.last_timer_text = self.timer_image.create_text(
            164, 52, text='--:--.-', fill='#172018', font=('Monospace', 11, 'bold'))
        self.timer_image.create_text(66, 78, text='YOUR TURN', fill='white',
                                     font=('Sans', 8, 'bold'))
        self.timer_image.create_text(164, 78, text='LAST DECISION', fill='white',
                                     font=('Sans', 8, 'bold'))
        self.decision_button = tk.Button(
            controls, text='Decision made — stop timer',
            command=self.mark_decision, state='disabled')
        self.decision_button.pack(pady=(4,8))

        tk.Label(controls, text='Stockfish move time (seconds)').pack(pady=(20,4))
        self.move_seconds = tk.StringVar(value='0.3')
        tk.Entry(controls, textvariable=self.move_seconds, width=10).pack()
        tk.Label(controls, textvariable=self.status, wraplength=230,
                 justify='left').pack(pady=(20,0))
        self.render()
        window.protocol('WM_DELETE_WINDOW', self.close)
        self.start_decision_timer()
        self.update_decision_timer()

    def square_for(self, row, col):
        # Convert a GUI row/column into the chess square used by python-chess.
        # The board is flipped when the player is black so the user always sees their
        # own pieces at the bottom.
        if self.player_color == chess.WHITE:
            return chess.square(col, 7-row)
        return chess.square(7-col, row)

    def render(self):
        # Highlight legal destinations for the selected piece and mark checks.
        possible = set()
        if self.selected is not None:
            possible = {m.to_square for m in self.board.legal_moves if m.from_square == self.selected}
        for (r,c), button in self.buttons.items():
            sq = self.square_for(r,c)
            piece = self.board.piece_at(sq)
            base = '#f0d9b5' if (r+c)%2==0 else '#b58863'
            if sq == self.selected: base = '#f6f669'
            elif sq in possible: base = '#9fd18b'
            elif self.board.is_check() and piece and piece.piece_type == chess.KING and piece.color == self.board.turn:
                base = '#ef8888'
            button.configure(text=SYMBOLS.get(piece.symbol(),'') if piece else '', bg=base,
                             activebackground=base)

    def click(self, row, col):
        # Ignore clicks while the engine is thinking or after the game is over.
        if self.thinking or self.board.is_game_over() or self.board.turn != self.player_color:
            return

        square = self.square_for(row,col)
        piece = self.board.piece_at(square)

        # Select a piece, deselect on second click, or attempt a legal move.
        if self.selected is None:
            if piece and piece.color == self.player_color:
                self.selected = square
        elif self.selected == square:
            self.selected = None
        else:
            candidates = [m for m in self.board.legal_moves
                          if m.from_square == self.selected and m.to_square == square]
            if candidates:
                # Promote pawns to queens automatically to avoid interrupting the flow.
                move = next((m for m in candidates if m.promotion == chess.QUEEN), candidates[0])
                self.stop_decision_timer()
                self.board.push(move)
                self.selected = None
                self.after_move()
                if not self.board.is_game_over():
                    self.engine_move()
            else:
                self.selected = square if piece and piece.color == self.player_color else None
        self.render()

    def after_move(self):
        # Update the status line after any move, including game-over states.
        if self.board.is_game_over():
            self.status.set(f'Game over: {self.board.outcome().result()} — {self.board.outcome().termination.name}')
        else:
            self.status.set('White to move' if self.board.turn else 'Black to move')

    def format_decision_time(self, seconds):
        minutes, remainder = divmod(seconds, 60)
        return f'{int(minutes):02d}:{remainder:04.1f}'

    def start_decision_timer(self):
        # The human's stopwatch runs only during their turn, and not after game end.
        if (self.board.turn == self.player_color and not self.board.is_game_over()
                and self.decision_started_at is None):
            self.decision_started_at = time.monotonic()
        self.decision_button.configure(
            state='normal' if self.decision_started_at is not None else 'disabled')

    def stop_decision_timer(self):
        if self.decision_started_at is not None:
            self.last_decision_seconds = time.monotonic() - self.decision_started_at
            self.decision_started_at = None
            self.timer_image.itemconfigure(
                self.current_timer_text,
                text=self.format_decision_time(self.last_decision_seconds))
        self.decision_button.configure(state='disabled')

    def mark_decision(self):
        # Let the player stop the clock at the moment they have chosen a move.
        self.stop_decision_timer()
        self.update_decision_timer()

    def update_decision_timer(self):
        if self.decision_started_at is not None:
            elapsed = time.monotonic() - self.decision_started_at
            self.timer_image.itemconfigure(
                self.current_timer_text, text=self.format_decision_time(elapsed))
        if self.last_decision_seconds is not None:
            self.timer_image.itemconfigure(
                self.last_timer_text,
                text=self.format_decision_time(self.last_decision_seconds))
        if self.window.winfo_exists():
            self.timer_after_id = self.window.after(100, self.update_decision_timer)

    def engine_move(self):
        # Let Stockfish play only when it is the engine's turn and no move is already running.
        if self.thinking or self.board.turn == self.player_color or self.board.is_game_over():
            return
        self.thinking = True
        self.status.set('Stockfish is thinking…')
        serial = self.game_id
        board_copy = self.board.copy()
        try:
            seconds = max(0.05, min(30.0, float(self.move_seconds.get())))
        except ValueError:
            seconds = 0.3

        def worker():
            try:
                # Each search runs in a fresh engine process so we do not share one instance
                # across threads. The UI thread later updates the board with the chosen move.
                with chess.engine.SimpleEngine.popen_uci(str(ENGINE)) as engine:
                    result = engine.play(board_copy, chess.engine.Limit(time=seconds))
                error = None
                move = result.move
            except Exception as exc:
                error, move = str(exc), None
            self.window.after(0, lambda:self.complete_engine_move(serial, move, error))
        threading.Thread(target=worker, daemon=True).start()

    def complete_engine_move(self, serial, move, error):
        # Ignore stale engine results from older games or interrupted searches.
        if serial != self.game_id: return
        self.thinking = False
        if error:
            self.status.set('Engine error: ' + error)
            messagebox.showerror('Stockfish', error)
        elif move in self.board.legal_moves:
            self.board.push(move)
            self.after_move()
            self.start_decision_timer()
        self.render()

    def new_game(self, color):
        # Reset the board and set whether the human is white or black.
        self.game_id += 1
        self.stop_decision_timer()
        self.board.reset()
        self.selected = None
        self.player_color = color
        self.thinking = False
        self.last_decision_seconds = None
        self.timer_image.itemconfigure(self.current_timer_text, text='00:00.0')
        self.timer_image.itemconfigure(self.last_timer_text, text='--:--.-')
        self.status.set('Your move (White).' if color else 'Stockfish opens as White…')
        self.start_decision_timer()
        self.render()
        if color == chess.BLACK: self.engine_move()

    def save_game(self):
        # Save the current position as a PGN so it can be reopened in chess software.
        game = chess.pgn.Game.from_board(self.board)
        game.headers['Event'] = 'RobSoc Portable Chess'
        game.headers['Date'] = date.today().strftime('%Y.%m.%d')
        game.headers['White'] = 'Human' if self.player_color else 'Stockfish'
        game.headers['Black'] = 'Stockfish' if self.player_color else 'Human'
        games = ROOT / 'games'
        games.mkdir(exist_ok=True)
        filename = filedialog.asksaveasfilename(initialdir=games, defaultextension='.pgn',
                                               filetypes=[('Chess PGN','*.pgn')])
        if filename:
            with open(filename,'w',encoding='utf-8') as f: print(game,file=f)
            self.status.set('Saved: ' + filename)

    def close(self):
        # Prevent stale engine jobs from being applied after the app is closed.
        self.game_id += 1
        if self.timer_after_id is not None:
            self.window.after_cancel(self.timer_after_id)
        self.window.destroy()

if __name__ == '__main__':
    if not ENGINE.is_file():
        raise SystemExit('Missing engine. Run ./setup.sh first.')
    app = tk.Tk()
    ChessApp(app)
    app.mainloop()