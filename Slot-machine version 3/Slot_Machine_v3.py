import tkinter as tk
from tkinter import messagebox
import random
import pygame
import sys
import os
import time
import math
import json
import threading

# --- 1. RESOURCE PATH HELPER ---
def resource_path(relative_path):
    try:
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
    except Exception:
        pass
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, relative_path)

# --- 2. THEME & CONSTANTS ---
COLORS = {
    "bg": "#050510",
    "surface": "#12122b",
    "accent": "#00d4ff",
    "accent_glow": "#0055ff",
    "win": "#39ff14",
    "loss": "#ff3131",
    "text": "#ffffff",
    "text_muted": "#888899",
    "gold": "#f1c40f",
    "neon_pink": "#ff00ff"
}

SYMBOLS = ['🍒', '🍉', '🍋', '🔔', '⭐', '💎', '🍀']
PAYOUTS = {
    '🍒': 2,
    '🍉': 4,
    '🍋': 6,
    '🔔': 10,
    '🍀': 15,
    '⭐': 25,
    '💎': 50
}

SAVE_FILE = resource_path("save_game.json")

# --- 3. CUSTOM COMPONENTS ---

class ScrollingReel(tk.Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, 
            width=100, 
            height=160, 
            bg="#000000", 
            highlightthickness=2, 
            highlightbackground="#1a1a2e",
            **kwargs
        )
        self.symbols = [random.choice(SYMBOLS) for _ in range(5)]
        self.offset = 0
        self.item_ids = []
        self.draw_reel()
        self.create_rectangle(0, 0, 100, 40, fill="#0c0c1a", outline="", tags="overlay")
        self.create_rectangle(0, 120, 100, 160, fill="#0c0c1a", outline="", tags="overlay")
        self.create_line(0, 80, 100, 80, fill=COLORS["accent"], width=1, dash=(5, 5), tags="overlay")

    def draw_reel(self):
        self.delete("symbol")
        self.item_ids = []
        for i, sym in enumerate(self.symbols):
            y = (i * 80) - self.offset
            tid = self.create_text(50, y, text=sym, font=("Segoe UI Emoji", 40), fill="white", tags="symbol")
            self.item_ids.append(tid)
        self.tag_raise("overlay")

    def scroll(self, delta):
        self.offset += delta
        if self.offset >= 80:
            self.offset = 0
            self.symbols.pop()
            self.symbols.insert(0, random.choice(SYMBOLS))
            self.draw_reel()
        else:
            for i, tid in enumerate(self.item_ids):
                y = (i * 80) - self.offset 
                self.coords(tid, 50, y)

    def set_final(self, symbol):
        self.symbols[1] = symbol
        self.offset = 0
        self.draw_reel()

class ModernButton(tk.Button):
    def __init__(self, master, **kwargs):
        # Extract bg if it's in kwargs, otherwise use default accent color
        background = kwargs.pop('bg', COLORS["accent"])
        super().__init__(master, 
            bg=background, 
            fg="white", 
            font=("Segoe UI", 12, "bold"),
            activebackground="#0055ff",
            activeforeground="white",
            bd=0,
            cursor="hand2",
            padx=20,
            pady=10,
            relief="flat",
            **kwargs
        )
        self.default_bg = background
        self.bind("<Enter>", lambda e: self.config(bg="#33e0ff"))
        self.bind("<Leave>", lambda e: self.config(bg=self.default_bg))

# --- 4. MAIN GAME ENGINE ---
class SlotMachineV3:
    def __init__(self, root):
        self.root = root
        self.root.title("NEON STRIKE V3")
        self.root.geometry("1000x850") # Increased width to fit all panels
        self.root.configure(bg=COLORS["bg"])
        
        self.balance = self.load_game()
        self.is_spinning = False
        self.auto_spin = False
        self.is_muted = False
        self.history = []
        
        # Audio System
        self.has_audio = False
        try:
            pygame.mixer.init()
            spin_path = resource_path("spin.wav")
            win_path = resource_path("win.wav")
            if os.path.exists(spin_path):
                self.sound_spin = pygame.mixer.Sound(spin_path)
                self.has_audio = True
            else: self.sound_spin = None
            if os.path.exists(win_path): self.sound_win = pygame.mixer.Sound(win_path)
            else: self.sound_win = None
        except: self.sound_spin = self.sound_win = None

        self.setup_ui()
        self.root.bind("<Configure>", self.on_resize)

    def load_game(self):
        try:
            if os.path.exists(SAVE_FILE):
                with open(SAVE_FILE, 'r') as f:
                    data = json.load(f)
                    self.win_count = data.get("win_count", 0)
                    self.loss_count = data.get("loss_count", 0)
                    return data.get("balance", 20000)
        except: pass
        self.win_count = 0
        self.loss_count = 0
        return 20000

    def save_game(self):
        try:
            with open(SAVE_FILE, 'w') as f:
                json.dump({
                    "balance": self.balance,
                    "win_count": self.win_count,
                    "loss_count": self.loss_count
                }, f)
        except: pass

    def setup_ui(self):
        # 1. Main Center Container
        self.container = tk.Frame(self.root, bg=COLORS["bg"])
        self.container.place(relx=0.45, rely=0.5, anchor="center", width=500, height=750)

        self.main_canvas = tk.Canvas(self.container, bg=COLORS["bg"], highlightthickness=0, width=500, height=750)
        self.main_canvas.pack(fill="both", expand=True)

        self.draw_vector_logo(250, 45)
        self.main_canvas.create_text(250, 90, text="NEON STRIKE V3", font=("Segoe UI Black", 32), fill=COLORS["accent"])
        self.main_canvas.create_text(252, 92, text="NEON STRIKE V3", font=("Segoe UI Black", 32), fill=COLORS["accent_glow"])
        
        self.draw_rounded_rect(150, 140, 350, 220, 20, COLORS["surface"])
        self.main_canvas.create_text(250, 160, text="TOTAL BALANCE", font=("Segoe UI", 10, "bold"), fill=COLORS["text_muted"])
        self.lbl_balance = self.main_canvas.create_text(250, 192, text=f"₹{self.balance:,}", font=("Segoe UI", 28, "bold"), fill=COLORS["gold"])

        self.draw_rounded_rect(40, 260, 460, 480, 30, "#0a0a1a")
        self.reels_frame = tk.Frame(self.container, bg="#000000", padx=10, pady=10)
        self.main_canvas.create_window(250, 370, window=self.reels_frame)
        
        self.reels = []
        for i in range(3):
            reel = ScrollingReel(self.reels_frame)
            reel.pack(side="left", padx=8)
            self.reels.append(reel)

        self.controls_frame = tk.Frame(self.container, bg=COLORS["bg"])
        self.main_canvas.create_window(250, 600, window=self.controls_frame)

        tk.Label(self.controls_frame, text="BET AMOUNT", font=("Segoe UI", 10, "bold"), bg=COLORS["bg"], fg=COLORS["text_muted"]).pack()
        self.bet_var = tk.StringVar(value="20")
        self.ent_bet = tk.Entry(self.controls_frame, textvariable=self.bet_var, font=("Segoe UI", 20, "bold"), width=5, justify="center", bg=COLORS["surface"], fg="white", bd=0)
        self.ent_bet.pack(pady=5)
        
        btn_box = tk.Frame(self.controls_frame, bg=COLORS["bg"])
        btn_box.pack(pady=10)
        
        self.btn_spin = ModernButton(btn_box, text="SPIN TO WIN", command=self.start_spin, width=15)
        self.btn_spin.pack(side="left", padx=5)
        
        self.btn_auto = ModernButton(btn_box, text="AUTO: OFF", command=self.toggle_auto, width=10, bg="#444")
        self.btn_auto.pack(side="left", padx=5)

        self.status_text = self.main_canvas.create_text(250, 720, text="LUCK IS IN THE AIR", font=("Segoe UI", 12, "italic"), fill=COLORS["text_muted"])
        
        # Audio Button
        self.audio_btn_text = "🔊" if self.has_audio else "🔇"
        self.audio_display = self.main_canvas.create_text(470, 30, text=self.audio_btn_text, font=("Segoe UI Symbol", 20), fill=COLORS["text_muted"])
        self.main_canvas.tag_bind(self.audio_display, "<Button-1>", lambda e: self.toggle_mute())

        # 2. History Panels (Right Side)
        self.history_frame = tk.Frame(self.root, bg=COLORS["bg"])
        self.history_frame.place(relx=0.78, rely=0.5, anchor="center", width=360, height=600)

        # Win Tab
        self.win_panel = tk.Frame(self.history_frame, bg=COLORS["surface"], bd=1, relief="flat")
        self.win_panel.pack(side="left", fill="both", expand=True, padx=5)
        tk.Label(self.win_panel, text="WINS 🏆", font=("Segoe UI", 10, "bold"), bg=COLORS["surface"], fg=COLORS["win"]).pack(pady=5)
        self.win_list = tk.Text(self.win_panel, bg=COLORS["surface"], fg=COLORS["win"], font=("Segoe UI", 8), bd=0, highlightthickness=0, height=25)
        self.win_list.pack(fill="both", expand=True, padx=5)
        self.win_list.config(state="disabled")
        self.lbl_win_total = tk.Label(self.win_panel, text=f"Total: {self.win_count}", font=("Segoe UI", 10, "bold"), bg=COLORS["surface"], fg=COLORS["win"])
        self.lbl_win_total.pack(pady=5)

        # Loss Tab
        self.loss_panel = tk.Frame(self.history_frame, bg=COLORS["surface"], bd=1, relief="flat")
        self.loss_panel.pack(side="left", fill="both", expand=True, padx=5)
        tk.Label(self.loss_panel, text="LOSSES 💀", font=("Segoe UI", 10, "bold"), bg=COLORS["surface"], fg=COLORS["loss"]).pack(pady=5)
        self.loss_list = tk.Text(self.loss_panel, bg=COLORS["surface"], fg=COLORS["text_muted"], font=("Segoe UI", 8), bd=0, highlightthickness=0, height=25)
        self.loss_list.pack(fill="both", expand=True, padx=5)
        self.loss_list.config(state="disabled")
        self.lbl_loss_total = tk.Label(self.loss_panel, text=f"Total: {self.loss_count}", font=("Segoe UI", 10, "bold"), bg=COLORS["surface"], fg=COLORS["loss"])
        self.lbl_loss_total.pack(pady=5)

    def on_resize(self, event):
        # Optimized spacing for 1000px width
        self.container.place(relx=0.33, rely=0.5, anchor="center")
        self.history_frame.place(relx=0.78, rely=0.5, anchor="center")

    def toggle_auto(self):
        self.auto_spin = not self.auto_spin
        self.btn_auto.config(text=f"AUTO: {'ON' if self.auto_spin else 'OFF'}", bg=COLORS["win"] if self.auto_spin else "#444")
        if self.auto_spin and not self.is_spinning:
            self.start_spin()

    def toggle_mute(self):
        if not self.has_audio: return
        self.is_muted = not self.is_muted
        self.main_canvas.itemconfig(self.audio_display, text="🔇" if self.is_muted else "🔊")

    def draw_vector_logo(self, x, y):
        pts = [x-10, y-25, x+15, y-25, x-5, y, x+15, y, x-20, y+35, x, y, x-15, y]
        self.main_canvas.create_polygon(pts, fill=COLORS["accent"], outline=COLORS["accent_glow"], width=2)
        self.main_canvas.create_oval(x-30, y-30, x+30, y+30, outline=COLORS["accent_glow"], width=1, dash=(2, 4))

    def draw_rounded_rect(self, x1, y1, x2, y2, r, color):
        points = [x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1]
        return self.main_canvas.create_polygon(points, fill=color, smooth=True)

    def update_balance(self, amount):
        self.balance = amount
        self.main_canvas.itemconfig(self.lbl_balance, text=f"₹{self.balance:,}")
        self.save_game()

    def set_status(self, text, color=None):
        if not color: color = COLORS["text_muted"]
        self.main_canvas.itemconfig(self.status_text, text=text, fill=color)

    def start_spin(self):
        if self.is_spinning: return
        try:
            bet = int(self.bet_var.get())
        except: return
        if bet <= 0 or bet > self.balance:
            self.auto_spin = False
            self.btn_auto.config(text="AUTO: OFF", bg="#444")
            return

        self.is_spinning = True
        self.update_balance(self.balance - bet)
        self.btn_spin.config(state="disabled")
        self.set_status("SPINNING...", COLORS["accent"])
        if self.sound_spin and not self.is_muted: self.sound_spin.play()
        self.animation_step = 0
        self.animate_tick(bet)

    def animate_tick(self, bet):
        if self.animation_step < 40:
            speed = max(5, int(25 * (1 - (self.animation_step/40)**0.5)))
            for reel in self.reels: reel.scroll(speed)
            self.animation_step += 1
            self.root.after(20, lambda: self.animate_tick(bet))
        else: self.finish_spin(bet)

    def add_to_history(self, msg, type_name):
        target = self.win_list if type_name == "win" else self.loss_list
        color = COLORS["win"] if type_name == "win" else COLORS["loss"]
        
        if type_name == "win":
            self.win_count += 1
            self.lbl_win_total.config(text=f"Total: {self.win_count}")
        else:
            self.loss_count += 1
            self.lbl_loss_total.config(text=f"Total: {self.loss_count}")

        target.config(state="normal")
        target.insert("1.0", f"• {msg}\n")
        target.config(state="disabled")
        self.save_game()

    def finish_spin(self, bet):
        # Natural Roll
        final_results = [random.choice(SYMBOLS) for _ in range(3)]
        
        # 1% LUCK BOOST: Force a win if a random roll hits
        if random.random() < 0.01:
            win_sym = random.choice(SYMBOLS)
            final_results = [win_sym, win_sym, win_sym]

        for i, reel in enumerate(self.reels):
            reel.set_final(final_results[i])

        if final_results[0] == final_results[1] == final_results[2]:
            multi = PAYOUTS[final_results[0]]
            win_amt = bet * multi
            self.update_balance(self.balance + win_amt)
            self.set_status(f"🎉 BIG WIN: ₹{win_amt}!", COLORS["win"])
            if self.sound_win and not self.is_muted: self.sound_win.play()
            self.add_to_history(f"Won ₹{win_amt} ({final_results[0]})", "win")
            self.shake_ui()
        else:
            self.set_status("TRY AGAIN", COLORS["loss"])
            self.add_to_history(f"Lost ₹{bet}", "loss")

        self.btn_spin.config(state="normal")
        self.is_spinning = False
        
        if self.auto_spin and self.balance > 0:
            self.root.after(1000, self.start_spin)
        elif self.balance <= 0:
            self.auto_spin = False
            messagebox.showinfo("GAME OVER", "Bust! Balance reset to ₹1,000 bonus.")
            self.update_balance(1000)

    def shake_ui(self):
        def do_shake(count):
            if count > 0:
                ox, oy = random.randint(-5, 5), random.randint(-5, 5)
                self.container.place(relx=0.45, rely=0.5, anchor="center", x=ox, y=oy)
                self.root.after(20, lambda: do_shake(count - 1))
            else: self.container.place(relx=0.45, rely=0.5, anchor="center", x=0, y=0)
        do_shake(10)

if __name__ == "__main__":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except: pass
    root = tk.Tk()
    app = SlotMachineV3(root)
    root.mainloop()
