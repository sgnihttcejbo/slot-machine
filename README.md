# 🎰 Slot Machine (v1.1)

A classic 3-reel slot machine game built with Python and Tkinter. Featuring sound effects, a GUI, and simple betting logic.

## 🚀 Features
- **Graphic Interface**: Built with Python's built-in Tkinter library.
- **Sound Effects**: Included `spin.wav` and `win.wav` for an immersive experience (requires `pygame`).
- **Dynamic Animation**: Symbols spin smoothly before revealing the result.
- **Docker Support**: Ready to be containerized with the provided Dockerfile.

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.x
- `pygame` library (for sound effects)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/toxicbishop/Slot-Machine.git
   ```
2. Navigate to the project folder:
   ```bash
   cd "Slot-Machine/Slot-machine version 1"
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the game:
   ```bash
   python Slot_Machine.py
   ```

## 🎮 How to Play
1. Start with a balance of ₹100.
2. Enter your bet amount (e.g., ₹10).
3. Click **SPIN!** and wait for the symbols to line up.
4. Winning combinations:
   - 🍒 (Cherry): 2x Bet
   - 🍉 (Watermelon): 4x Bet
   - 🍋 (Lemon): 6x Bet
   - 🔔 (Bell): 8x Bet
   - ⭐ (Star): 20x Bet

## 🐳 Docker
To run using Docker (requires an X11 server on the host for GUI):
```bash
docker build -t slot-machine .
docker run -it --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix slot-machine
```

## 📄 License
Distributed under the MIT License. See [LICENSE](LICENSE) for more information.
