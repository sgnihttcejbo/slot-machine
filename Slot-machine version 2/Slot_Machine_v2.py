import tkinter as tk
from tkinter import messagebox
import random
import pygame
import sys
import os
import time
import math

# --- 1. RESOURCE PATH HELPER ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # Check if we are running in a PyInstaller bundle
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
    except Exception:
        pass
    
    # We should look in the directory where the script is located
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

# --- 3. CUSTOM COMPONENTS ---

class ScrollingReel(tk.Canvas):
    """A realistic scrolling reel for that casino feel."""
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
        
        # Add visual depth (Glass effect overlays)
        # Note: Using small rectangles instead of large ones for performance
        self.create_rectangle(0, 0, 100, 40, fill="#0c0c1a", outline="", tags="overlay")
        self.create_rectangle(0, 120, 100, 160, fill="#0c0c1a", outline="", tags="overlay")
        # Central highlight
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
            # Move all symbols
            for i, tid in enumerate(self.item_ids):
                y = (i * 80) - self.offset 
                self.coords(tid, 50, y)

    def set_final(self, symbol):
        # Force the middle symbol (index 2 in a 5-symbol list for 160 height) to be the target
        # Our view is 160 high. center is 80.
        # symbols[0] is at y=0
        # symbols[1] is at y=80 (Center)
        # symbols[2] is at y=160
        self.symbols[1] = symbol
        self.offset = 0
        self.draw_reel()

class ModernButton(tk.Button):
    def __init__(self, master, **kwargs):
        super().__init__(master, 
            bg=COLORS["accent"], 
            fg="white", 
            font=("Segoe UI", 12, "bold"),
            activebackground="#0055ff",
            activeforeground="white",
            bd=0,
            cursor="hand2",
            padx=30,
            pady=12,
            relief="flat",
            **kwargs
        )
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self.config(bg="#33e0ff")
    
    def on_leave(self, e):
        self.config(bg=COLORS["accent"])

# --- 4. MAIN GAME ENGINE ---
class SlotMachinePro:
    def __init__(self, root):
        self.root = root
        self.root.title("NEON STRIKE")
        self.root.geometry("600x850") # Slightly larger default
        self.root.configure(bg=COLORS["bg"])
        
        self.balance = 20000
        self.is_spinning = False
        
        # Audio System
        self.has_audio = False
        try:
            pygame.mixer.init()
            spin_path = resource_path("spin.wav")
            win_path = resource_path("win.wav")
            
            if os.path.exists(spin_path):
                self.sound_spin = pygame.mixer.Sound(spin_path)
                self.has_audio = True
            else:
                self.sound_spin = None

            if os.path.exists(win_path):
                self.sound_win = pygame.mixer.Sound(win_path)
            else:
                self.sound_win = None
        except:
            self.sound_spin = self.sound_win = None

        self.is_muted = False
        self.setup_ui()
        self.root.bind("<Configure>", self.on_resize)

    def setup_ui(self):
        # Set window icon if exists
        icon_path = resource_path("icon.png")
        if os.path.exists(icon_path):
            try:
                img = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(False, img)
            except:
                pass

        # Center container
        self.container = tk.Frame(self.root, bg=COLORS["bg"])
        self.container.place(relx=0.5, rely=0.5, anchor="center", width=500, height=750)

        self.main_canvas = tk.Canvas(self.container, bg=COLORS["bg"], highlightthickness=0, width=500, height=750)
        self.main_canvas.pack(fill="both", expand=True)

        # Draw a Vector Logo (Lightning Bolt)
        self.draw_vector_logo(250, 45)

        self.main_canvas.create_text(250, 90, text="NEON STRIKE", font=("Segoe UI Black", 32), fill=COLORS["accent"])
        self.main_canvas.create_text(252, 92, text="NEON STRIKE", font=("Segoe UI Black", 32), fill=COLORS["accent_glow"])
        
        # Balance Card
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
        self.main_canvas.create_window(250, 580, window=self.controls_frame)

        tk.Label(self.controls_frame, text="BET AMOUNT", font=("Segoe UI", 10, "bold"), bg=COLORS["bg"], fg=COLORS["text_muted"]).pack()
        self.bet_var = tk.StringVar(value="20")
        self.ent_bet = tk.Entry(self.controls_frame, textvariable=self.bet_var, font=("Segoe UI", 20, "bold"), width=5, justify="center", bg=COLORS["surface"], fg="white", bd=0)
        self.ent_bet.pack(pady=10)
        
        self.btn_spin = ModernButton(self.controls_frame, text="SPIN TO WIN", command=self.start_spin)
        self.btn_spin.pack(pady=10)

        self.status_text = self.main_canvas.create_text(250, 710, text="LUCK IS IN THE AIR", font=("Segoe UI", 12, "italic"), fill=COLORS["text_muted"])
        
        # Audio Button (Interactive)
        self.audio_btn_text = "🔊" if self.has_audio else "🔇"
        self.audio_display = self.main_canvas.create_text(470, 30, text=self.audio_btn_text, font=("Segoe UI Symbol", 20), fill=COLORS["text_muted"])
        self.main_canvas.tag_bind(self.audio_display, "<Button-1>", lambda e: self.toggle_mute())
        self.main_canvas.tag_bind(self.audio_display, "<Enter>", lambda e: self.main_canvas.itemconfig(self.audio_display, fill=COLORS["accent"]))
        self.main_canvas.tag_bind(self.audio_display, "<Leave>", lambda e: self.main_canvas.itemconfig(self.audio_display, fill=COLORS["text_muted"]))

    def on_resize(self, event):
        # Keep the container centered regardless of window size
        self.container.place(relx=0.5, rely=0.5, anchor="center")

    def toggle_mute(self):
        if not self.has_audio: return
        self.is_muted = not self.is_muted
        new_icon = "🔇" if self.is_muted else "🔊"
        self.main_canvas.itemconfig(self.audio_display, text=new_icon)
        self.set_status("SOUND MUTED" if self.is_muted else "SOUND ON", COLORS["accent"] if not self.is_muted else COLORS["text_muted"])

    def draw_vector_logo(self, x, y):
        # Draw a stylized lightning bolt logo
        pts = [
            x-10, y-25, 
            x+15, y-25, 
            x-5, y, 
            x+15, y, 
            x-20, y+35, 
            x, y, 
            x-15, y
        ]
        self.main_canvas.create_polygon(pts, fill=COLORS["accent"], outline=COLORS["accent_glow"], width=2)
        # Add glow circles
        self.main_canvas.create_oval(x-30, y-30, x+30, y+30, outline=COLORS["accent_glow"], width=1, dash=(2, 4))

    def draw_rounded_rect(self, x1, y1, x2, y2, r, color):
        points = [x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1]
        return self.main_canvas.create_polygon(points, fill=color, smooth=True)

    def update_balance(self, amount):
        self.balance = amount
        self.main_canvas.itemconfig(self.lbl_balance, text=f"₹{self.balance:,}")

    def set_status(self, text, color=None):
        if not color: color = COLORS["text_muted"]
        self.main_canvas.itemconfig(self.status_text, text=text, fill=color)

    def start_spin(self):
        if self.is_spinning: return
        try:
            bet = int(self.bet_var.get())
        except:
            return

        if bet <= 0 or bet > self.balance:
            return

        self.is_spinning = True
        self.update_balance(self.balance - bet)
        self.btn_spin.config(state="disabled")
        self.set_status("SPINNING...", COLORS["accent"])
        
        if self.sound_spin and not self.is_muted: 
            self.sound_spin.play()
        
        # UI-Friendly Animation
        self.animation_step = 0
        self.animate_tick(bet)

    def animate_tick(self, bet):
        if self.animation_step < 50:
            speed = max(5, int(25 * (1 - (self.animation_step/50)**0.5)))
            for reel in self.reels:
                reel.scroll(speed)
            self.animation_step += 1
            self.root.after(20, lambda: self.animate_tick(bet))
        else:
            self.finish_spin(bet)

    def finish_spin(self, bet):
        final_results = [random.choice(SYMBOLS) for _ in range(3)]
        for i, reel in enumerate(self.reels):
            reel.set_final(final_results[i])

        if final_results[0] == final_results[1] == final_results[2]:
            multi = PAYOUTS[final_results[0]]
            win_amt = bet * multi
            self.update_balance(self.balance + win_amt)
            self.set_status(f"🎉 BIG WIN: ₹{win_amt}!", COLORS["win"])
            if self.sound_win and not self.is_muted: 
                self.sound_win.play()
            self.shake_ui()
        else:
            self.set_status("TRY AGAIN", COLORS["loss"])

        self.btn_spin.config(state="normal")
        self.is_spinning = False

    def shake_ui(self):
        def do_shake(count):
            if count > 0:
                ox = random.randint(-5, 5)
                oy = random.randint(-5, 5)
                self.container.place(relx=0.5, rely=0.5, anchor="center", x=ox, y=oy)
                self.root.after(20, lambda: do_shake(count - 1))
            else:
                self.container.place(relx=0.5, rely=0.5, anchor="center", x=0, y=0)
        do_shake(10)

if __name__ == "__main__":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    root = tk.Tk()
    app = SlotMachinePro(root)
    root.mainloop()
