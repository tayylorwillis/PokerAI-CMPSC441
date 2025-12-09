class Player:
    def __init__(self, name, starting_money=1000, is_bot=False):
        self.name = name
        self.money = starting_money
        self.hand = []
        self.current_bet = 0
        self.is_folded = False
        self.is_bot = is_bot
        self.is_active = True  # Player is still in the game (has money)

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

    def place_bet(self, amount):
        """Place a bet (deduct from money, add to current_bet)"""
        if amount > self.money:
            amount = self.money  # All-in
        self.money -= amount
        self.current_bet += amount
        return amount

    def win_pot(self, pot_amount):
        """Add winnings to player's money"""
        self.money += pot_amount

    def __str__(self):
        return f"{self.name}: ${self.money} (Current bet: ${self.current_bet})"