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

#class for card objects
class Card:
    def __init__(self):
        self.suit = 0
        self.rank = 0
        #self.is_ace = false

#generate a random card
def gen_card():
    card = Card()
    card.rank = random.randint(2, 14)
    suit_int = random.randint(1, 4)
    if (suit_int == 1):
        card.suit = "hearts"
    if (suit_int == 2):
        card.suit = "diamonds"
    if (suit_int == 3):
        card.suit = "spades"
    if (suit_int == 4):
        card.suit = "clubs"
    return card


#hand generation func
def create_hands():
    dealt_cards = [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10]
    hand1 = [0, 0, 0, 0, 0]
    hand2 = [0, 0, 0, 0, 0]
    i = 1
    j = -1
    for c in dealt_cards:
        c = gen_card()
    for i in 10:
        j = 0
        while j < i:
            if (i.suit == j.suit and i.rank == j.rank):
                i = gen_card()

        i = i + 1





#hand type detection func
def hand_type(hand):
    if


