import tkinter as tk
from tkinter import messagebox
import random
import pygame
import sys
import os
import threading
import time

# --- 1. RESOURCE PATH HELPER ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- 2. THEME & CONSTANTS ---
COLORS = {
    "bg": "#0f0f1a",
    "surface": "#1e1e2e",
    "accent": "#00d4ff",
    "win": "#39ff14",
    "loss": "#ff3131",
    "text": "#ffffff",
    "text_muted": "#888899",
    "gold": "#f1c40f"
}

SYMBOLS = ['🍒', '🍉', '🍋', '🔔', '⭐']
PAYOUTS = {
    '🍒': 2,
    '🍉': 4,
    '🍋': 6,
    '🔔': 8,
    '⭐': 20
}

# --- 3. CUSTOM COMPONENTS ---
class ModernButton(tk.Button):
    def __init__(self, master, **kwargs):
        super().__init__(master, 
            bg=COLORS["accent"], 
            fg="white", 
            font=("Segoe UI", 12, "bold"),
            activebackground="#00aacc",
            activeforeground="white",
            bd=0,
            cursor="hand2",
            padx=20,
            pady=10,
            **kwargs
        )
        self.bind("<Enter>", lambda e: self.config(bg="#33e0ff"))
        self.bind("<Leave>", lambda e: self.config(bg=COLORS["accent"]))

class SlotReel(tk.Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, 
            width=100, 
            height=120, 
            bg="#111111", 
            highlightthickness=2, 
            highlightbackground="#2c2c3e",
            **kwargs
        )
        self.text_id = self.create_text(50, 60, text="❓", font=("Segoe UI Emoji", 45), fill="white")
    
    def set_symbol(self, symbol):
        self.itemconfig(self.text_id, text=symbol)

# --- 4. MAIN GAME ENGINE ---
class SlotMachineV2:
    def __init__(self, root):
        self.root = root
        self.root.title("Super Slots Pro 🎰")
        self.root.geometry("450x650")
        self.root.configure(bg=COLORS["bg"])
        
        self.balance = 100
        self.is_spinning = False
        
        # Initialize Audio
        try:
            pygame.mixer.init()
            self.sound_spin = pygame.mixer.Sound(resource_path("spin.wav"))
            self.sound_win = pygame.mixer.Sound(resource_path("win.wav"))
        except:
            self.sound_spin = self.sound_win = None
            print("Audio devices not found. Running in silent mode.")

        self.setup_ui()

    def setup_ui(self):
        # Header Area
        header = tk.Frame(self.root, bg=COLORS["bg"], pady=30)
        header.pack(fill="x")
        
        tk.Label(header, text="SUPER SLOTS", font=("Impact", 36), bg=COLORS["bg"], fg=COLORS["accent"]).pack()
        tk.Label(header, text="PREMIUM EDITION", font=("Segoe UI", 10, "bold"), bg=COLORS["bg"], fg=COLORS["text_muted"]).pack()

        # Balance Display
        self.balance_frame = tk.Frame(self.root, bg=COLORS["surface"], padx=20, pady=10)
        self.balance_frame.pack(pady=10)
        
        tk.Label(self.balance_frame, text="BALANCE", font=("Segoe UI", 9, "bold"), bg=COLORS["surface"], fg=COLORS["text_muted"]).pack()
        self.lbl_balance = tk.Label(self.balance_frame, text=f"₹{self.balance}", font=("Segoe UI", 24, "bold"), bg=COLORS["surface"], fg=COLORS["gold"])
        self.lbl_balance.pack()

        # Reels Area
        reels_container = tk.Frame(self.root, bg=COLORS["bg"], pady=40)
        reels_container.pack()
        
        self.reels = []
        for i in range(3):
            reel = SlotReel(reels_container)
            reel.grid(row=0, column=i, padx=10)
            self.reels.append(reel)

        # Controls Area
        controls = tk.Frame(self.root, bg=COLORS["bg"])
        controls.pack(pady=20)

        tk.Label(controls, text="BET AMOUNT", font=("Segoe UI", 10, "bold"), bg=COLORS["bg"], fg=COLORS["text_muted"]).pack()
        
        self.bet_var = tk.StringVar(value="10")
        self.ent_bet = tk.Entry(controls, textvariable=self.bet_var, font=("Segoe UI", 16, "bold"), width=6, justify="center", bg=COLORS["surface"], fg="white", insertbackground="white", bd=0)
        self.ent_bet.pack(pady=10)
        
        self.btn_spin = ModernButton(controls, text="SPIN NOW", command=self.start_spin)
        self.btn_spin.pack(pady=15)

        # Status Messenger
        self.lbl_status = tk.Label(self.root, text="Ready to Win?", font=("Segoe UI", 11, "italic"), bg=COLORS["bg"], fg=COLORS["text_muted"])
        self.lbl_status.pack(pady=10)

    def update_balance(self, amount):
        self.balance = amount
        self.lbl_balance.config(text=f"₹{self.balance}")
        # Pulse animation
        self.lbl_balance.config(fg="white")
        self.root.after(200, lambda: self.lbl_balance.config(fg=COLORS["gold"]))

    def show_status(self, text, color=None):
        if not color: color = COLORS["text_muted"]
        self.lbl_status.config(text=text, fg=color)

    def start_spin(self):
        if self.is_spinning: return
        
        try:
            bet = int(self.bet_var.get())
        except ValueError:
            messagebox.showerror("Error", "Enter a valid bet!")
            return

        if bet <= 0:
            self.show_status("Invalid Bet!", COLORS["loss"])
            return
        if bet > self.balance:
            self.show_status("Insufficient Funds!", COLORS["loss"])
            return

        self.is_spinning = True
        self.update_balance(self.balance - bet)
        self.btn_spin.config(state="disabled")
        self.show_status("Good Luck...", COLORS["accent"])
        
        if self.sound_spin: self.sound_spin.play()
        
        # Start animation thread
        threading.Thread(target=self.animate_spin, args=(bet,), daemon=True).start()

    def animate_spin(self, bet):
        for i in range(20):
            symbols_temp = [random.choice(SYMBOLS) for _ in range(3)]
            for j, reel in enumerate(self.reels):
                reel.set_symbol(symbols_temp[j])
            time.sleep(0.05 + (i * 0.005)) # Gradually slows down
        
        self.root.after(0, lambda: self.finalize_spin(bet))

    def finalize_spin(self, bet):
        final_results = [random.choice(SYMBOLS) for _ in range(3)]
        for i, reel in enumerate(self.reels):
            reel.set_symbol(final_results[i])

        if final_results[0] == final_results[1] == final_results[2]:
            multiplier = PAYOUTS[final_results[0]]
            winnings = bet * multiplier
            self.update_balance(self.balance + winnings)
            self.show_status(f"JACKPOT! WIN ₹{winnings}", COLORS["win"])
            if self.sound_win: self.sound_win.play()
        else:
            self.show_status("Try Again!", COLORS["loss"])

        self.btn_spin.config(state="normal")
        self.is_spinning = False

        if self.balance <= 0:
            messagebox.showinfo("Game Over", "Bust! Better luck next time.")
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    # Simple fix for blurry text on High DPI Windows screens
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
        
    game = SlotMachineV2(root)
    root.mainloop()
