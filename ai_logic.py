from game_logic import gen_card
from hand_evaluator import HandEvaluator

#t.e. 2598960 total possible poker hands

def win_prob(hand):
    type, rank = HandEvaluator.evaluate_hand(hand)
    if (type == "Royal Flush"):
        return 1
    
    if (type == "Straight Flush"):
        if (rank == 13): #K
            prob = (2598960-4)/2598960
            return prob
        if (rank == 12): #Q
            prob = (2598960-8)/2598960
            return prob
        if (rank == 11): #J
            prob = (2598960-12)/2598960
            return prob
        if (rank == 10):
            prob = (2598960-16)/2598960
            return prob
        if (rank == 9):
            prob = (2598960-20)/2598960
            return prob
        if (rank == 8):
            prob = (2598960-24)/2598960
            return prob
        if (rank == 7):
            prob = (2598960-28)/2598960
            return prob
        if (rank == 6):
            prob = (2598960-32)/2598960
            return prob
        if (rank == 5):
            prob = (2598960-36)/2598960
            return prob
        
    if (type == "Four of a Kind"):
        if (rank == 14): #A
            prob = (2598960-40-48*0)/2598960
            return prob
        if (rank == 13): #K
            prob = (2598960-40-48*1)/2598960
            return prob
        if (rank == 12): #Q
            prob = (2598960-40-48*2)/2598960
            return prob
        if (rank == 11): #J
            prob = (2598960-40-48*3)/2598960
            return prob
        if (rank == 10):
            prob = (2598960-40-48*4)/2598960
            return prob
        if (rank == 9):
            prob = (2598960-40-48*5)/2598960
            return prob
        if (rank == 8):
            prob = (2598960-40-48*6)/2598960
            return prob
        if (rank == 7):
            prob = (2598960-40-48*7)/2598960
            return prob
        if (rank == 6):
            prob = (2598960-40-48*8)/2598960
            return prob
        if (rank == 5):
            prob = (2598960-40-48*9)/2598960
            return prob
        if (rank == 4):
            prob = (2598960-40-48*10)/2598960
            return prob
        if (rank == 3):
            prob = (2598960-40-48*11)/2598960
            return prob
        if (rank == 2):
            prob = (2598960-40-48*12)/2598960
            return prob
        
    
    if (type == "Full House"):
        if (rank == 13): #A
            prob = (2598344 -(312*1))/2598960
            return prob
        if (rank == 13): #K
            prob = (2598344 -(312*2))/2598960
            return prob
        if (rank == 12): #Q
            prob = (2598344 -(312*3))/2598960
            return prob
        if (rank == 11): #J
            prob = (2598344 -(312*4))/2598960
            return prob
        if (rank == 10):
            prob = (2598344 -(312*5))/2598960
            return prob
        if (rank == 9):
            prob = (2598344 -(312*6))/2598960
            return prob
        if (rank == 8):
            prob = (2598344 -(312*7))/2598960
            return prob
        if (rank == 7):
            prob = (2598344 -(312*8))/2598960
            return prob
        if (rank == 6):
            prob = (2598344 -(312*9))/2598960
            return prob
        if (rank == 5):
            prob = (2598344 -(312*10))/2598960
            return prob
        if (rank == 4):
            prob = (2598344 -(312*11))/2598960
            return prob
        if (rank == 3):
            prob = (2598344 -(312*12))/2598960
            return prob
    #FIX
    if (type == "Flush"):
        if (rank == 13): #A
            prob = (2594600 -(572*0))/2598960
            return prob
        if (rank == 13): #K
            prob = (2594600 -(572*1))/2598960
            return prob
        if (rank == 12): #Q
            prob = (2594600 -(572*2))/2598960
            return prob
        if (rank == 11): #J
            prob = (2594600 -(572*3))/2598960
            return prob
        if (rank == 10):
            prob = (2594600 -(572*4))/2598960
            return prob
        if (rank == 9):
            prob = (2594600 -(572*5))/2598960
            return prob
        if (rank == 8):
            prob = (2594600 -(572*6))/2598960
            return prob
        if (rank == 7):
            prob = (2594600 -(572*7))/2598960
            return prob
        if (rank == 6):
            prob = (2594600 -(572*8))/2598960
            return prob
        
    
    if (type == "Straight"):
        if (rank == 13): #A
            prob = (2589444 - (1020*1))/2598960
            return prob
        if (rank == 13): #K
            prob = (2589444 - (1020*2))/2598960
            return prob
        if (rank == 12): #Q
            prob = (2589444 - (1020*3))/2598960
            return prob
        if (rank == 11): #J
            prob = (2589444 - (1020*4))/2598960
            return prob
        if (rank == 10):
            prob = (2589444 - (1020*5))/2598960
            return prob
        if (rank == 9):
            prob = (2589444 - (1020*6))/2598960
            return prob
        if (rank == 8):
            prob = (2589444 - (1020*7))/2598960
            return prob
        if (rank == 7):
            prob = (2589444 - (1020*8))/2598960
            return prob
        if (rank == 6):
            prob = (2589444 - (1020*9))/2598960
            return prob
        if (rank == 5):
            prob = (2589444 - (1020*10))/2598960
            return prob
        
    
    if (type == "Three of a Kind"):
        if (rank == 14): #A
            prob = (2579244 - (4224*1))/2598960
            return prob
        if (rank == 13): #K
            prob = (2579244 - (4224*2))/2598960
            return prob
        if (rank == 12): #Q
            prob = (2579244 - (4224*3))/2598960
            return prob
        if (rank == 11): #J
            prob = (2579244 - (4224*4))/2598960
            return prob
        if (rank == 10):
            prob = (2579244 - (4224*5))/2598960
            return prob
        if (rank == 9):
            prob = (2579244 - (4224*6))/2598960
            return prob
        if (rank == 8):
            prob = (2579244 - (4224*7))/2598960
            return prob
        if (rank == 7):
            prob = (2579244 - (4224*8))/2598960
            return prob
        if (rank == 6):
            prob = (2579244 - (4224*9))/2598960
            return prob
        if (rank == 5):
            prob = (2579244 - (4224*10))/2598960
            return prob
        if (rank == 4):
            prob = (2579244 - (4224*11))/2598960
            return prob
        if (rank == 3):
            prob = (2579244 - (4224*12))/2598960
            return prob
        if (rank == 2):
            prob = (2579244 - (4224*13))/2598960
            return prob
    
    if (type == "Two Pair"):
        if (rank == 14): #A
            prob = (2524332 - (10296*1))/2598960
            return prob
        if (rank == 13): #K
            prob = (2524332 - (10296*2))/2598960
            return prob
        if (rank == 12): #Q
            prob = (2524332 - (10296*3))/2598960
            return prob
        if (rank == 11): #J
            prob = (2524332 - (10296*4))/2598960
            return prob
        if (rank == 10):
            prob = (2524332 - (10296*5))/2598960
            return prob
        if (rank == 9):
            prob = (2524332 - (10296*6))/2598960
            return prob
        if (rank == 8):
            prob = (2524332 - (10296*7))/2598960
            return prob
        if (rank == 7):
            prob = (2524332 - (10296*8))/2598960
            return prob
        if (rank == 6):
            prob = (2524332 - (10296*9))/2598960
            return prob
        if (rank == 5):
            prob = (2524332 - (10296*10))/2598960
            return prob
        if (rank == 4):
            prob = (2524332 - (10296*11))/2598960
            return prob
        if (rank == 3):
            prob = (2524332 - (10296*12))/2598960
            return prob
        
    
    if (type == "One Pair"):
        if (rank == 14): #A
            prob = (2400780 - (84480*1))/2598960
            return prob
        if (rank == 13): #K
            prob = (2400780 - (84480*2))/2598960
            return prob
        if (rank == 12): #Q
            prob = (2400780 - (84480*3))/2598960
            return prob
        if (rank == 11): #J
            prob = (2400780 - (84480*4))/2598960
            return prob
        if (rank == 10):
            prob = (2400780 - (84480*5))/2598960
            return prob
        if (rank == 9):
            prob = (2400780 - (84480*6))/2598960
            return prob
        if (rank == 8):
            prob = (2400780 - (84480*7))/2598960
            return prob
        if (rank == 7):
            prob = (2400780 - (84480*8))/2598960
            return prob
        if (rank == 6):
            prob = (2400780 - (84480*9))/2598960
            return prob
        if (rank == 5):
            prob = (2400780 - (84480*10))/2598960
            return prob
        if (rank == 4):
            prob = (2400780 - (84480*11))/2598960
            return prob
        if (rank == 3):
            prob = (2400780 - (84480*12))/2598960
            return prob
        if (rank == 2):
            prob = (2400780 - (84480*13))/2598960
            return prob
    
    if (type == "High Card"):
        if (rank == 14): #A
            prob = (1302540 - (108545*1))/2598960
            return prob
        if (rank == 13): #K
            prob = (1302540 - (108545*2))/2598960
            return prob
        if (rank == 12): #Q
            prob = (1302540 - (108545*3))/2598960
            return prob
        if (rank == 11): #J
            prob = (1302540 - (108545*4))/2598960
            return prob
        if (rank == 10):
            prob = (1302540 - (108545*5))/2598960
            return prob
        if (rank == 9):
            prob = (1302540 - (108545*6))/2598960
            return prob
        if (rank == 8):
            prob = (1302540 - (108545*7))/2598960
            return prob
        if (rank == 7):
            prob = (1302540 - (108545*8))/2598960
            return prob
        if (rank == 6):
            prob = (1302540 - (108545*9))/2598960
            return prob
        if (rank == 5):
            prob = (1302540 - (108545*10))/2598960
            return prob
        if (rank == 4):
            prob = (1302540 - (108545*11))/2598960
            return prob
        if (rank == 3):
            prob = (1302540 - (108545*12))/2598960
            return prob
        
    