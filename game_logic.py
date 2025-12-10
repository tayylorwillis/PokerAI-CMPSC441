""""
A:14
K:13
Q:12
J:11
10:10...

add pot tracking, as well as call/raise/fold
"""

import random
#import array

class Pot:
    def __init__(self, pot_sum1 = 0, agent_chips1 = 1000, player_chips1 = 1000):
        self.pot_sum = pot_sum1
        self.last_raise = 0
        self.agent_chips = agent_chips1
        self.player_chips = player_chips1
        self.agent_chips_in = 0             #how many of their chips are in curr pot (used for call calc)
        self.player_chips_in  = 0

    @staticmethod
    def my_bet(num, who):
        #will be in player and ai_logic classes instead
        """
        if (who == "ai"):  
            if (agent_chips < num):  #if an attempt to raise is made w/ chips a player does not have, just raise by all remaining chips
                num = agent_chips
            agent_chips = agent_chips - num
        """
        if (who == "agent"):  
            agent_chips_in = agent_chips_in + num
            agent_chips = agent_chips - num
        if (who == "player"):  
            player_chips_in = player_chips_in + num
            player_chips = player_chips - num
        pot_sum = pot_sum + num
        last_raise = num

    def 

        




        

#class for card objects
class Card:
    def __init__(self):
        self.suit = 0
        self.rank = 0
        self.id = 0
        #self.is_ace = false

#generate a random card
def gen_card():
    card = Card()
    #every card in deck has unique id through 52, decipher which is which accordingly:
    card_num = random.randint(1, 52)
    card.id = card_num
    # modulo 13 to get rank, +1 to adjust for ace high
    card.rank = (card_num % 13) + 1
    #rank order irrelevant, but divided evenly
    if ( card_num >= 1 and card_num <= 13):
        card.suit = "hearts"
    if ( card_num >= 14 and card_num <= 26):
        card.suit = "diamonds"
    if ( card_num >= 27 and card_num <= 39):
        card.suit = "spades"
    if ( card_num >= 40 and card_num <= 52):
        card.suit = "clubs"
    '''
    if (card.rank == 14):
        card.is_ace = true
    '''
    return card

#generate a specific card (only used for testing)
def create_card(card_num):
    card = Card()
    card.id = card_num
    # modulo 13 to get rank, +1 to adjust for ace high
    card.rank = (card_num % 13) + 1
    #rank order irrelevant, but divided evenly
    if ( card_num >= 1 and card_num <= 13):
        card.suit = "hearts"
    if ( card_num >= 14 and card_num <= 26):
        card.suit = "diamonds"
    if ( card_num >= 27 and card_num <= 39):
        card.suit = "spades"
    if ( card_num >= 40 and card_num <= 52):
        card.suit = "clubs"
    '''
    if (card.rank == 14):
        card.is_ace = true
    '''
    return card


#hand generation func
def create_hands():
    #track undealt cards
    #deck = list(range(1, 53))
    dealt_cards = []
    hand1 = []
    hand2 = []
    i = 0
    #generate first hand
    while (i < 5):
        c = gen_card()
        #if new card has already been dealt, generate a new card until it is unique
        while (c.id in dealt_cards):
            c = gen_card()
        #deck.remove(c.id)
        dealt_cards.append(c.id)
        hand1.append(c)
        i = i + 1

    i = 0
    while (i < 5):
        c = gen_card()
        while (c.id in dealt_cards):
            c = gen_card()
        #deck.remove(c.id)
        dealt_cards.append(c.id)
        hand2.append(c)
        i = i + 1
    
    return hand1, hand2

def print_hand(hand):
    print(hand[0].suit, hand[0].rank, ", ", hand[1].suit, hand[1].rank, ", ", hand[2].suit, hand[2].rank,
           ", ", hand[3].suit, hand[3].rank, ", ", hand[4].suit, hand[4].rank)

def hand_type(hand):
    ranks = [hand[0].rank, hand[1].rank, hand[2].rank, hand[3].rank, hand[4].rank]
    suits = [hand[0].suit, hand[1].suit, hand[2].suit, hand[3].suit, hand[4].suit]
    max_rank = max(ranks)
    is_flush = False
    is_straight = False

    has_pair = False
    pair_rank = 0
    has_three = False
    three_rank = 0
    has_two_pair = False
    second_pair_rank = 0
    has_four = False
    four_rank = 0

    #check for straight
    if (max_rank - 1 in ranks and max_rank - 2 in ranks and max_rank - 3 in ranks and 
        max_rank - 4 in ranks):
        is_straight = True
    #check for flush
    if (suits[0] == suits[1] and suits[0] == suits[2] and suits[0] == suits[3] and
        suits[0] == suits[4]):
        is_flush = True

    rank_nums = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for c in hand:
        rank_nums[c.rank - 1] = rank_nums[c.rank - 1] + 1

    i = 1
    for n in rank_nums:
        if (n == 4):
            has_four = True
            four_rank = i
        i = i + 1

    i = 1
    for n in rank_nums:
        if (n == 3):
            has_three = True
            three_rank = i
        i = i + 1

    i = 1
    for n in rank_nums:
        if (n == 2 and has_pair == True):
            has_two_pair = True
            second_pair_rank = i
        if (n == 2 and has_pair == False):
            has_pair = True
            pair_rank = i
        i = i + 1

    # return hand type and relevant val in case of tied hand type and 
    # needing to compare ranks to determine winner
    if (is_flush and is_straight and max_rank == 14):
        return "Royal Flush", max_rank
    
    if (is_flush and is_straight):
        return "Straight Flush", max_rank
    
    if (has_four):
        return "Four of a Kind", four_rank

    if (has_pair and has_three):
        return "Full House", three_rank

    if (is_flush):
        return "Flush", max_rank

    if (is_straight):
        return "Straight", max_rank
    
    if (has_three):
        return "Three of a Kind", three_rank

    if (has_two_pair):
        return "Two Pair", max(pair_rank, second_pair_rank)

    if (has_pair):
        return "One Pair", pair_rank

    return "High Card", max_rank


