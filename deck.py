from game_logic import gen_card

class Deck:
    """Manages a deck of cards for dealing hands."""

    def __init__(self):
        self.dealt_cards = []

    def reset(self):
        """Resets the deck for a new game."""
        self.dealt_cards = []

    def deal_unique_card(self):
        """Deals a single unique card that hasn't been dealt yet. Returns a Card object."""
        card = gen_card()
        while card.id in self.dealt_cards:
            card = gen_card()

        self.dealt_cards.append(card.id)
        return card

    def deal_hand(self, num_cards=5):
        """Deals a hand of cards. Returns a list of Card objects."""
        hand = []
        for i in range(num_cards):
            card = self.deal_unique_card()
            hand.append(card)
        return hand

    def deal_hands(self, num_players=2, cards_per_hand=5):
        """Deals hands to multiple players. Returns a list of hands."""
        hands = []
        for i in range(num_players):
            hand = self.deal_hand(cards_per_hand)
            hands.append(hand)
        return hands