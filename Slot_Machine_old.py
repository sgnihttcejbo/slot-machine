import random

def spin_row():
    symbols = ['🍒', '🍉', '🍋', '🔔', '⭐']
    result = [random.choice(symbols) for _ in range(3)]
    return result

def print_row(row):
    print("-------------")
    print(" | ".join(row))
    print("-------------")

def get_payout(row, bet):
    # Check if all three symbols match
    if row[0] == row[1] == row[2]:
        if row[0] == '🍒':
            return bet * 2
        elif row[0] == '🍉':
            return bet * 4
        elif row[0] == '🍋':
            return bet * 6
        elif row[0] == '🔔':
            return bet * 8
        elif row[0] == '⭐':
            return bet * 20
    return 0

def main():
    balance = 100  # Fixed spelling from 'ballence'
    
    print("----------------------------------")
    print("Welcome to the Slot Machine!")
    print("Symbols: 🍒 🍉 🍋 🔔 ⭐")
    print("----------------------------------")
    
    while balance > 0:
        print(f"Current Balance: ₹{balance}")
        bet_input = input("Enter your bet amount: ₹")
        
        # Validation
        if not bet_input.isdigit():
            print("Invalid bet amount. Please enter a valid number.")
            continue

        bet = int(bet_input)
        
        if bet > balance:
            print(f"Insufficient balance. You only have ₹{balance}.")
            continue
        if bet <= 0:
            print("Bet amount must be greater than zero.")
            continue
        
        # Deduct bet
        balance -= bet
        
        # Spin
        row = spin_row()
        print("Spinning...\n")
        print_row(row)

        # Calculate Payout
        payout = get_payout(row, bet)
        
        # Handle Win/Loss
        if payout > 0:
            print(f"Jackpot! You won ₹{payout}!")
            balance += payout
        else:
            print("Sorry, you didn't win this time.")
        
        # Check if user is broke
        if balance == 0:
            print("You ran out of money! Game Over.")
            break

        # Ask to play again
        play_again = input("Do you want to play again? (yes/no): ").strip().lower()
        if play_again != 'yes': 
            break
            
    print(f"Game over! You left with ₹{balance}")

if __name__ == "__main__":
    main()