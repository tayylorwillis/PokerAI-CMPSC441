""""
Goals for game_logic:
generate player hands
assign hands to players
detect hand types (ace high)
get_hand()
initiate who starts (not our agent for now)
operate the changing of turns
take_turn() func
call()
fold()
raise()
user prompting for user turn
mode setting for bot v bot or bot v user?
initialize starting money, will use a var for now,
take prompt from user later
ace 14 for now, add is_ace later

NOT: (this is a note to self because I Stew 
struggle to remember what goes where and will
start putting everything here otherwise)
win likelihood for bot logic
turn logic/decision making for bot
"""

"""
A:14
K:13
Q:12
J:11
10:10...
"""

import random
import array

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
    card_num = random.randint(1, 52)
    card.id = card_num
    card.rank = (card_num % 13) + 2
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
    deck = list(range(1, 53))
    dealt_cards = []
    hand1 = []
    hand2 = []
    i = 0
    while (i < 5):
        c = gen_card()
        while (c.id in dealt_cards):
            c = gen_card()
        deck.remove(c.id)
        dealt_cards.append(c.id)
        hand1.append(c)
        i = i + 1

    i = 0
    while (i < 5):
        c = gen_card()
        while (c.id in dealt_cards):
            c = gen_card()
        deck.remove(c.id)
        dealt_cards.append(c.id)
        hand2.append(c)
        i = i + 1
    
    return hand1, hand2

def print_hand(hand):
    print(hand[0].suit, hand[0].rank, ", ", hand[1].suit, hand[1].rank, ", ", hand[2].suit, hand[2].rank,
           ", ", hand[3].suit, hand[3].rank, ", ", hand[4].suit, hand[4].rank)


'''
#hand type detection func
def hand_type(hand):
    if
'''

'''
c1 = gen_card()
print(c1.rank)
print(c1.suit)

hand1, hand2 = create_hands()
print_hand(hand1)
print_hand(hand2)
'''




