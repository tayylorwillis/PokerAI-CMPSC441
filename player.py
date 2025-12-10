from game_logic import Pot

class Player:
    def __init__(self, name, starting_money=1000, is_bot=False):
        self.name = name
        self.money = starting_money
        self.hand = []
        self.current_bet = 0
        self.is_folded = False
        self.is_bot = is_bot
        self.is_active = True  # Player is still in the game

    def receive_hand(self, hand):
        """Assign a hand to the player"""
        self.hand = hand

    def reset_for_new_round(self):
        """Reset player state for a new round"""
        self.hand = []
        self.current_bet = 0
        self.is_folded = False

    def can_bet(self, amount):
        """Check if player has enough money to bet"""
        return self.money >= amount

    def place_bet(self, amount, pot=None):
        """Place a bet (deduct from money, add to current_bet)"""
        if amount > self.money:
            amount = self.money  # All-in
            self.is_active = False
        self.money -= amount
        self.current_bet += amount
        # Add to pot if pot instance is provided
        if pot:
            who = "opponent" if self.is_bot else "player"
            pot.add_bet(amount, who)
        return amount

    def call(self, pot):
        """Call the current bet (match opponent's bet)."""
        who = "opponent" if self.is_bot else "player"
        call_amt = pot.get_call_amount(who)
        if call_amt > 0:
            return self.place_bet(call_amt, pot)
        return 0

    def win_pot(self, pot_amount):
        """Add winnings to player's money"""
        self.money += pot_amount

    def __str__(self):
        return f"{self.name}: ${self.money} (Current bet: ${self.current_bet})"