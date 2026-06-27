import tkinter as tk
from tkinter import messagebox
import random
import pygame # type: ignore
import sys
import os
import math
import json

# --- 1. RESOURCE PATH HELPER ---
def resource_path(relative_path):
    try:
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path) # type: ignore
    except Exception:
        pass
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, relative_path)

# --- 2. THEME & CONSTANTS ---
COLORS = {
    "bg": "#0F1115",
    "surface": "#16181F",
    "surface_light": "#1E2029",
    "gold": "#D4AF37",
    "gold_glow": "#F8E4A0",
    "win": "#00E676",
    "loss": "#FF3D00",
    "text": "#F5F5F5",
    "text_muted": "#8A8D93",
    "border": "#2A2D35"
}

SYMBOLS = ['🍒', '🍉', '🍋', '🔔', '🍀', '⭐', '💎']
PAYOUTS = {
    '🍒': 2, '🍉': 4, '🍋': 6, '🔔': 10, '🍀': 15, '⭐': 25, '💎': 50
}

if getattr(sys, 'frozen', False):
    SAVE_FILE = os.path.join(os.path.dirname(sys.executable), "save_game.json")
else:
    SAVE_FILE = resource_path("save_game.json")

def get_gaussian_symbol():
    mean = (len(SYMBOLS) - 1) / 2.0
    stdev = len(SYMBOLS) / 4.0
    u = 1.0 - random.random()
    v = 1.0 - random.random()
    z = math.sqrt(-2.0 * math.log(u)) * math.cos(2.0 * math.pi * v)
    index = int(round(z * stdev + mean))
    index = max(0, min(len(SYMBOLS) - 1, index))
    return SYMBOLS[index]

# --- 3. CUSTOM COMPONENTS & EFFECTS ---

class ModernButton(tk.Canvas):
    def __init__(self, master, text, command, bg_color=COLORS["gold"], fg_color="#0F1115", hover_color=COLORS["gold_glow"], width=150, height=45, font=("Segoe UI Semibold", 12)):
        super().__init__(master, width=width, height=height, bg=master["bg"], highlightthickness=0)
        self.command = command
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.hover_color = hover_color
        self.btn_state = "normal"
        self.is_shining = False
        
        self.rect_id = self.create_rounded_rect(2, 2, width-2, height-2, r=height//2, fill=bg_color, outline=COLORS["border"])
        self.text_id = self.create_text(width/2, height/2, text=text, font=font, fill=fg_color)
        
        self.bind("<Button-1>", lambda e: self.on_press())
        self.bind("<ButtonRelease-1>", lambda e: self.on_release())
        self.bind("<Enter>", lambda e: self.on_enter())
        self.bind("<Leave>", lambda e: self.on_leave())
        
    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1]
        return self.create_polygon(points, smooth=True, **kwargs)

    def trigger_shine(self):
        if self.is_shining: return
        self.is_shining = True
        w, h = int(self["width"]), int(self["height"])
        shine = self.create_polygon(0, h, 20, h, 40, 0, 20, 0, fill="#FFFFFF", stipple="gray50", outline="", tags="shine")
        self.coords(shine, -40, h, -20, h, 0, 0, -20, 0)
        self.animate_shine(shine, -40, w + 40, 15)

    def animate_shine(self, shine, x, target_x, speed):
        if not self.winfo_exists(): return
        if x < target_x:
            h = int(self["height"])
            self.coords(shine, x, h, x+20, h, x+40, 0, x+20, 0)
            self.after(16, lambda: self.animate_shine(shine, x+speed, target_x, speed))
        else:
            self.delete(shine)
            self.is_shining = False

    def on_enter(self):
        if self.btn_state == "normal":
            self.itemconfig(self.rect_id, fill=self.hover_color)
            self.config(cursor="hand2")
            self.trigger_shine()

    def on_leave(self):
        if self.btn_state == "normal":
            self.itemconfig(self.rect_id, fill=self.bg_color)
            self.config(cursor="")

    def on_press(self):
        if self.btn_state == "normal":
            self.itemconfig(self.rect_id, fill="#FFFFFF")
    
    def on_release(self):
        if self.btn_state == "normal":
            self.itemconfig(self.rect_id, fill=self.hover_color)
            self.command()
    
    def config_text(self, text):
        self.itemconfig(self.text_id, text=text)
    
    def config_bg(self, color):
        self.bg_color = color
        if self.btn_state == "normal":
            self.itemconfig(self.rect_id, fill=color)

    def disable(self):
        self.btn_state = "disabled"
        self.itemconfig(self.rect_id, fill=COLORS["surface_light"])
        self.itemconfig(self.text_id, fill=COLORS["text_muted"])
        self.config(cursor="")

    def enable(self):
        self.btn_state = "normal"
        self.itemconfig(self.rect_id, fill=self.bg_color)
        self.itemconfig(self.text_id, fill=self.fg_color)


class ScrollingReel(tk.Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, width=120, height=200, bg=COLORS["surface"], highlightthickness=0, **kwargs)
        self.symbols = [get_gaussian_symbol() for _ in range(5)]
        self.offset = 0
        self.item_ids = []
        self.draw_reel()
        
        # Simulated cylinder curvature using stippled gradients
        self.create_rectangle(0, 0, 120, 60, fill="#000000", outline="", stipple="gray50", tags="overlay")
        self.create_rectangle(0, 140, 120, 200, fill="#000000", outline="", stipple="gray50", tags="overlay")
        
        # Center target line
        self.create_line(10, 100, 110, 100, fill=COLORS["gold"], width=1, dash=(2, 4), tags="overlay")
        
        # Clean rounded border
        self.create_polygon(10, 0, 110, 0, 120, 10, 120, 190, 110, 200, 10, 200, 0, 190, 0, 10, fill="", outline=COLORS["gold"], width=2, smooth=True, tags="overlay")

    def draw_reel(self):
        self.delete("symbol")
        self.item_ids = []
        for i, sym in enumerate(self.symbols):
            y = (i * 100) - self.offset
            tid = self.create_text(60, y, text=sym, font=("Segoe UI Emoji", 48), fill="white", tags="symbol")
            self.item_ids.append(tid)
        self.tag_raise("overlay")

    def scroll(self, delta):
        self.offset += delta
        if self.offset >= 100:
            self.offset = 0
            self.symbols.pop()
            self.symbols.insert(0, get_gaussian_symbol())
            self.draw_reel()
        else:
            for i, tid in enumerate(self.item_ids):
                y = (i * 100) - self.offset 
                self.coords(tid, 60, y)

    def set_final(self, symbol):
        self.symbols[1] = symbol
        self.offset = 0
        self.draw_reel()


# --- 4. MAIN GAME ENGINE ---
class SlotMachineV3_2:
    def __init__(self, root):
        self.root = root
        self.root.title("ROYAL SLOTS")
        self.root.geometry("1000x850")
        self.root.configure(bg=COLORS["bg"])
        self.root.minsize(1000, 850)
        
        self.balance = self.load_game()
        self.is_spinning = False
        self.auto_spin = False
        self.is_muted = False
        self.is_fullscreen = False
        
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_fullscreen)
        
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
        self.glow_step = 0
        self.animation_loop()

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

    def draw_rounded_rect(self, canvas, x1, y1, x2, y2, r, color, outline=""):
        points = [x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1]
        return canvas.create_polygon(points, fill=color, outline=outline, smooth=True, width=1)

    def setup_ui(self):
        self.main_canvas = tk.Canvas(self.root, bg=COLORS["bg"], highlightthickness=0, width=1000, height=850)
        self.main_canvas.place(relx=0.5, rely=0.5, anchor="center")

        # --- BACKGROUND GLOW ---
        # Draw concentric subtle rings for a breathing glow effect behind reels
        self.glow_rings = []
        cx, cy = 350, 420
        for i in range(3):
            ring = self.main_canvas.create_oval(cx-1, cy-1, cx+1, cy+1, outline=COLORS["gold"], width=1, stipple="gray25", state="hidden")
            self.glow_rings.append(ring)

        # --- TOP NAVIGATION BAR ---
        self.main_canvas.create_rectangle(0, 0, 1000, 60, fill=COLORS["surface"], outline=COLORS["border"], width=1)
        self.main_canvas.create_text(500, 30, text="R O Y A L   S L O T S", font=("Segoe UI", 16, "bold"), fill=COLORS["gold"])

        # Audio Toggle
        self.audio_btn_text = "🔊" if self.has_audio else "🔇"
        self.audio_display = self.main_canvas.create_text(50, 30, text=self.audio_btn_text, font=("Segoe UI Emoji", 20), fill=COLORS["text"])
        self.main_canvas.tag_bind(self.audio_display, "<Button-1>", lambda e: self.toggle_mute())
        self.main_canvas.tag_bind(self.audio_display, "<Enter>", lambda e: self.main_canvas.itemconfig(self.audio_display, fill=COLORS["gold"]))
        self.main_canvas.tag_bind(self.audio_display, "<Leave>", lambda e: self.main_canvas.itemconfig(self.audio_display, fill=COLORS["text"]))

        # Fullscreen Toggle
        self.fs_display = self.main_canvas.create_text(950, 30, text="⛶", font=("Segoe UI Symbol", 20), fill=COLORS["text"])
        self.main_canvas.tag_bind(self.fs_display, "<Button-1>", self.toggle_fullscreen)
        self.main_canvas.tag_bind(self.fs_display, "<Enter>", lambda e: self.main_canvas.itemconfig(self.fs_display, fill=COLORS["gold"]))
        self.main_canvas.tag_bind(self.fs_display, "<Leave>", lambda e: self.main_canvas.itemconfig(self.fs_display, fill=COLORS["text"]))

        # --- LEFT STAGE (Main Game) ---
        game_cx = 350

        # Balance Display
        self.main_canvas.create_text(game_cx, 130, text="CURRENT BALANCE", font=("Segoe UI", 11), fill=COLORS["text_muted"])
        self.lbl_balance = self.main_canvas.create_text(game_cx, 170, text=f"₹{self.balance:,}", font=("Segoe UI", 42, "bold"), fill=COLORS["gold"])

        # Slot Machine Housing
        self.draw_rounded_rect(self.main_canvas, game_cx - 240, 260, game_cx + 240, 520, 30, COLORS["surface"])
        self.draw_rounded_rect(self.main_canvas, game_cx - 225, 275, game_cx + 225, 505, 20, COLORS["bg"])
        
        self.reels_frame = tk.Frame(self.main_canvas, bg=COLORS["bg"])
        self.main_canvas.create_window(game_cx, 390, window=self.reels_frame)
        
        self.reels = []
        for i in range(3):
            reel = ScrollingReel(self.reels_frame)
            reel.pack(side="left", padx=15)
            self.reels.append(reel)

        # Status Text
        self.status_text = self.main_canvas.create_text(game_cx, 560, text="Place your bet.", font=("Georgia", 14, "italic"), fill=COLORS["text_muted"])

        # Bottom Control Deck
        deck_y = 620
        self.draw_rounded_rect(self.main_canvas, 40, deck_y, 660, deck_y + 160, 25, COLORS["surface"], outline=COLORS["border"])
        
        # Bet Input
        self.main_canvas.create_text(160, deck_y + 40, text="BET AMOUNT", font=("Segoe UI", 10, "bold"), fill=COLORS["text_muted"])
        self.draw_rounded_rect(self.main_canvas, 90, deck_y + 60, 230, deck_y + 120, 15, COLORS["bg"], outline=COLORS["border"])
        self.bet_var = tk.StringVar(value="20")
        self.ent_bet = tk.Entry(self.main_canvas, textvariable=self.bet_var, font=("Segoe UI", 24, "bold"), width=6, justify="center", bg=COLORS["bg"], fg=COLORS["gold"], bd=0, highlightthickness=0, insertbackground=COLORS["gold"])
        self.main_canvas.create_window(160, deck_y + 90, window=self.ent_bet)

        # Action Buttons
        self.btn_spin = ModernButton(self.main_canvas, text="SPIN", command=self.start_spin, bg_color=COLORS["gold"], hover_color=COLORS["gold_glow"], fg_color=COLORS["bg"], width=160, height=60, font=("Segoe UI", 16, "bold"))
        self.main_canvas.create_window(360, deck_y + 80, window=self.btn_spin)

        self.btn_auto = ModernButton(self.main_canvas, text="AUTO PLAY", command=self.toggle_auto, bg_color=COLORS["surface_light"], hover_color="#3A3D45", fg_color=COLORS["text"], width=120, height=60, font=("Segoe UI", 12))
        self.main_canvas.create_window(540, deck_y + 80, window=self.btn_auto)


        # --- RIGHT SIDEBAR (History) ---
        side_x = 720
        self.main_canvas.create_rectangle(side_x, 60, 1000, 850, fill=COLORS["surface"], outline=COLORS["border"], width=1)
        
        # History Setup
        self.setup_history_section("WINS", COLORS["win"], side_x + 30, 100, 220, 320, is_win=True)
        self.main_canvas.create_line(side_x + 30, 440, 970, 440, fill=COLORS["border"])
        self.setup_history_section("LOSSES", COLORS["loss"], side_x + 30, 470, 220, 320, is_win=False)


    def setup_history_section(self, title, color, x, y_start, width, h, is_win):
        # Header
        self.main_canvas.create_text(x, y_start, text=title, font=("Segoe UI", 14, "bold"), fill=color, anchor="w")
        
        # Total Label
        lbl = self.main_canvas.create_text(x + width, y_start, text=f"Total: {self.win_count if is_win else self.loss_count}", font=("Segoe UI", 12), fill=COLORS["text_muted"], anchor="e")
        if is_win: self.lbl_win_total_canvas = lbl
        else: self.lbl_loss_total_canvas = lbl

        # Text Widget
        text_widget = tk.Text(self.main_canvas, bg=COLORS["surface"], fg=COLORS["text"] if is_win else COLORS["text_muted"], font=("Segoe UI", 11), bd=0, highlightthickness=0, wrap="word")
        text_widget.insert("1.0", "No recent history.\n")
        text_widget.config(state="disabled")
        self.main_canvas.create_window(x + width/2, y_start + 160, window=text_widget, width=width, height=h-40)

        if is_win: self.win_list = text_widget
        else: self.loss_list = text_widget


    def animation_loop(self):
        # Premium Breathing Glow behind the slot machine
        self.glow_step += 0.02
        cx, cy = 350, 390
        
        for i, ring in enumerate(self.glow_rings):
            offset = i * (math.pi / 3)
            radius = 260 + math.sin(self.glow_step + offset) * 30
            self.main_canvas.coords(ring, cx - radius, cy - radius, cx + radius, cy + radius)
            self.main_canvas.itemconfig(ring, state="normal")
            
        self.root.after(40, self.animation_loop)


    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)
        return "break"

    def exit_fullscreen(self, event=None):
        self.is_fullscreen = False
        self.root.attributes("-fullscreen", False)
        return "break"


    def toggle_auto(self):
        self.auto_spin = not self.auto_spin
        if self.auto_spin:
            self.btn_auto.config_text("AUTO: ON")
            self.btn_auto.config_bg(COLORS["win"])
            self.btn_auto.fg_color = COLORS["bg"]
        else:
            self.btn_auto.config_text("AUTO PLAY")
            self.btn_auto.config_bg(COLORS["surface_light"])
            self.btn_auto.fg_color = COLORS["text"]
        self.btn_auto.enable() # refresh colors
        
        if self.auto_spin and not self.is_spinning:
            self.start_spin()

    def toggle_mute(self):
        if not self.has_audio: return
        self.is_muted = not self.is_muted
        self.main_canvas.itemconfig(self.audio_display, text="🔇" if self.is_muted else "🔊")

    def update_balance(self, amount, win=False):
        self.balance = amount
        self.main_canvas.itemconfig(self.lbl_balance, text=f"₹{self.balance:,}")
        if win:
            self.main_canvas.itemconfig(self.lbl_balance, fill=COLORS["win"])
            # Scale bump effect via font size
            self.main_canvas.itemconfig(self.lbl_balance, font=("Segoe UI", 48, "bold"))
            self.root.after(150, lambda: self.main_canvas.itemconfig(self.lbl_balance, font=("Segoe UI", 42, "bold")))
            self.root.after(600, lambda: self.main_canvas.itemconfig(self.lbl_balance, fill=COLORS["gold"]))
        self.save_game()

    def set_status(self, text, color=None):
        if not color: color = COLORS["text_muted"]
        self.main_canvas.itemconfig(self.status_text, text=text, fill=color)

    def start_spin(self):
        if self.is_spinning: return
        try: bet = int(self.bet_var.get())
        except: return
        if bet <= 0 or bet > self.balance:
            self.auto_spin = False
            self.toggle_auto()
            self.set_status("Insufficient balance.", COLORS["loss"])
            return

        self.is_spinning = True
        self.update_balance(self.balance - bet)
        self.btn_spin.disable()
        self.set_status("Spinning...", COLORS["gold"])
        if self.sound_spin and not self.is_muted: self.sound_spin.play()
        self.animation_step = 0
        self.animate_tick(bet)

    def animate_tick(self, bet):
        if self.animation_step < 40:
            speed = max(6, int(30 * (1 - (self.animation_step/40)**0.5)))
            for reel in self.reels: reel.scroll(speed)
            self.animation_step += 1
            self.root.after(20, lambda: self.animate_tick(bet))
        else: self.finish_spin(bet)

    def add_to_history(self, msg, type_name):
        target = self.win_list if type_name == "win" else self.loss_list
        lbl_total = self.lbl_win_total_canvas if type_name == "win" else self.lbl_loss_total_canvas
        
        target.config(state="normal")
        if "No recent history" in target.get("1.0", "end"): target.delete("1.0", "end")
            
        if type_name == "win":
            self.win_count += 1
            self.main_canvas.itemconfig(lbl_total, text=f"Total: {self.win_count}")
        else:
            self.loss_count += 1
            self.main_canvas.itemconfig(lbl_total, text=f"Total: {self.loss_count}")

        target.insert("1.0", f"• {msg}\n")
        target.config(state="disabled")
        self.save_game()

    def finish_spin(self, bet):
        final_results = [get_gaussian_symbol() for _ in range(3)]
        
        if random.random() < 0.01:
            win_sym = get_gaussian_symbol()
            final_results = [win_sym, win_sym, win_sym]

        for i, reel in enumerate(self.reels):
            reel.set_final(final_results[i])

        if final_results[0] == final_results[1] == final_results[2]:
            multi = PAYOUTS[final_results[0]]
            win_amt = bet * multi
            self.update_balance(self.balance + win_amt, win=True)
            self.set_status(f"Winner! Payout ₹{win_amt:,}", COLORS["win"])
            if self.sound_win and not self.is_muted: self.sound_win.play()
            self.add_to_history(f"Won ₹{win_amt:,} ({final_results[0]})", "win")
        else:
            self.set_status("Try again.", COLORS["text_muted"])
            self.add_to_history(f"Lost ₹{bet:,}", "loss")

        self.btn_spin.enable()
        self.is_spinning = False
        
        if self.auto_spin and self.balance > 0:
            self.root.after(1200, self.start_spin)
        elif self.balance <= 0:
            self.auto_spin = False
            self.toggle_auto()
            messagebox.showinfo("Game Over", "Balance depleted. Resetting to ₹1,000 bonus.")
            self.update_balance(1000)

if __name__ == "__main__":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except: pass
    root = tk.Tk()
    app = SlotMachineV3_2(root)
    root.mainloop()
