import tkinter as tk
from tkinter import messagebox
import random
import pygame
import sys
import os

# --- 1. EXE RESOURCE HELPER ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

# --- 2. SOUND MANAGER CLASS ---
class SoundManager:
    """Handles loading and playing sounds safely."""
    def __init__(self):
        self.sounds = {}
        try:
            print("   [Audio] Initializing Pygame Mixer...")
            pygame.mixer.init()
            # Load sounds safely
            self.load_sound("spin", resource_path("spin.wav"))
            self.load_sound("win", resource_path("win.wav"))
        except Exception as e:
            print(f"   [Audio Error] {e}")

    def load_sound(self, name, filepath):
        if os.path.exists(filepath):
            self.sounds[name] = pygame.mixer.Sound(filepath)
            print(f"   [Audio] Loaded: {name}")
        else:
            print(f"   [Audio Warning] File not found: {filepath}")

    def play(self, name):
        if name in self.sounds:
            self.sounds[name].play()

# --- 3. MAIN GUI CLASS ---
class SlotMachineGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Slot Machine")
        self.root.geometry("500x500")
        self.root.configure(bg="#2c3e50")

        # Initialize Audio
        self.audio = SoundManager()

        # Game State
        self.balance = 100
        self.symbols = ['🍒', '🍉', '🍋', '🔔', '⭐']
        self.is_spinning = False

        # Title
        self.title_label = tk.Label(root, text="🎰 Super Slots 🎰", font=("Arial", 24, "bold"), bg="#2c3e50", fg="#f1c40f")
        self.title_label.pack(pady=20)

        # Balance
        self.balance_label = tk.Label(root, text=f"Balance: ₹{self.balance}", font=("Arial", 14), bg="#2c3e50", fg="white")
        self.balance_label.pack()

        # Slots
        self.slots_frame = tk.Frame(root, bg="#2c3e50")
        self.slots_frame.pack(pady=30)

        self.slot_labels = []
        for i in range(3):
            lbl = tk.Label(self.slots_frame, text="❓", font=("Segoe UI Emoji", 40), bg="#ecf0f1", width=3, relief="sunken", bd=3)
            lbl.grid(row=0, column=i, padx=10)
            self.slot_labels.append(lbl)

        # Betting
        self.bet_frame = tk.Frame(root, bg="#2c3e50")
        self.bet_frame.pack(pady=10)
        
        tk.Label(self.bet_frame, text="Bet Amount: ₹", bg="#2c3e50", fg="white", font=("Arial", 12)).pack(side=tk.LEFT)
        self.bet_entry = tk.Entry(self.bet_frame, font=("Arial", 12), width=5, justify="center")
        self.bet_entry.insert(0, "10")
        self.bet_entry.pack(side=tk.LEFT, padx=5)

        # Spin Button
        self.spin_btn = tk.Button(root, text="SPIN!", font=("Arial", 16, "bold"), bg="#e74c3c", fg="white", command=self.start_spin, padx=20, pady=5)
        self.spin_btn.pack(pady=20)

        # Status
        self.status_label = tk.Label(root, text="Good Luck!", font=("Arial", 12, "italic"), bg="#2c3e50", fg="#bdc3c7")
        self.status_label.pack()

    def spin_logic(self):
        return [random.choice(self.symbols) for _ in range(3)]

    def get_payout(self, row, bet):
        if row[0] == row[1] == row[2]:
            if row[0] == '🍒': return bet * 2
            elif row[0] == '🍉': return bet * 4
            elif row[0] == '🍋': return bet * 6
            elif row[0] == '🔔': return bet * 8
            elif row[0] == '⭐': return bet * 20
        return 0

    def start_spin(self):
        if self.is_spinning: return

        try:
            bet = int(self.bet_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number.")
            return

        if bet <= 0:
            messagebox.showerror("Error", "Bet must be > 0.")
            return
        if bet > self.balance:
            messagebox.showerror("Error", "Insufficient funds!")
            return

        self.balance -= bet
        self.update_balance()
        self.is_spinning = True
        self.spin_btn.config(state="disabled", bg="#95a5a6")
        self.status_label.config(text="Spinning...", fg="#f1c40f")

        self.audio.play("spin")
        self.animate_slots(0, bet)

    def animate_slots(self, count, bet):
        temp_row = self.spin_logic()
        for i, symbol in enumerate(temp_row):
            self.slot_labels[i].config(text=symbol)

        if count < 15:
            self.root.after(100, lambda: self.animate_slots(count + 1, bet))
        else:
            self.finalize_spin(bet)

    def finalize_spin(self, bet):
        final_row = self.spin_logic()
        for i, symbol in enumerate(final_row):
            self.slot_labels[i].config(text=symbol)

        winnings = self.get_payout(final_row, bet)
        
        if winnings > 0:
            self.balance += winnings
            self.status_label.config(text=f"JACKPOT! You won ₹{winnings}!", fg="#2ecc71")
            self.audio.play("win")
            messagebox.showinfo("Winner!", f"You won ₹{winnings}!")
        else:
            self.status_label.config(text="No luck this time.", fg="#e74c3c")

        self.update_balance()
        self.is_spinning = False
        self.spin_btn.config(state="normal", bg="#e74c3c")

        if self.balance == 0:
            messagebox.showinfo("Game Over", "You have run out of money!")
            self.root.destroy()

    def update_balance(self):
        self.balance_label.config(text=f"Balance: ₹{self.balance}")

# --- 4. EXECUTION BLOCK ---
if __name__ == "__main__":
    print("--- DEBUG MODE START ---")
    print("1. Initializing Tkinter Root...")
    try:
        root = tk.Tk()
        print("2. Root created successfully.")
        
        print("3. initializing Application Logic...")
        app = SlotMachineGUI(root)
        print("4. App initialized.")
        
        print("5. Forcing Window to Front...")
        root.lift()
        root.attributes('-topmost', True)
        root.after_idle(root.attributes, '-topmost', False)
        
        print("6. Entering Main Loop (Game should be visible now)")
        root.mainloop()
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        input("Press Enter to close...")