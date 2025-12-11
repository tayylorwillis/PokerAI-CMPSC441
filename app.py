from flask import Flask, render_template, jsonify, request
from game_logic import Pot, gen_card
from player import Player
from deck import Deck
from hand_evaluator import HandEvaluator
from ai_player import BaseAIPlayer
from llm_logic import GeminiBot
import os

app = Flask(__name__)

# Using GAME_STATE instead of global variables


def card_to_dict(card, hidden=False):
    if hidden:
        return {"hidden": True}
    rank_map = {1: 'A', 11: 'J', 12: 'Q', 13: 'K', 10: '0'}
    rank_code = rank_map.get(card.rank, str(card.rank))
    
    suit_map = {'hearts': 'H', 'diamonds': 'D', 'spades': 'S', 'clubs': 'C'}
    suit_letter = suit_map.get(card.suit, 'H')
    
    img_url = f"https://deckofcardsapi.com/static/img/{rank_code}{suit_letter}.png"
    return {
        "rank": card.rank,
        "suit": card.suit,
        "image": img_url,
    }
def evaluate_winner(state):
    """Evaluate winner among all active players (not folded)."""
    player = state["player"]
    opponent = state["opponent"]
    gemini = state.get("gemini_bot")
    
    # Get best hands for all players
    p_best = HandEvaluator.evaluate_hand(player.hand) if player.hand else None
    o_best = HandEvaluator.evaluate_hand(opponent.hand) if opponent.hand else None
    g_best = HandEvaluator.evaluate_hand(gemini.hand) if gemini and gemini.hand else None
    
    active_players = []
    if not player.is_folded and p_best:
        active_players.append(("player", player, p_best))
    if not opponent.is_folded and o_best:
        active_players.append(("opponent", opponent, o_best))
    if gemini and not gemini.is_folded and g_best:
        active_players.append(("gemini_bot", gemini, g_best))
    
    if len(active_players) == 0:
        return "tie", p_best, o_best, g_best
    if len(active_players) == 1:
        return active_players[0][0], p_best, o_best, g_best
    
    # Find winner by comparing hands
    best_player = active_players[0]
    for i in range(1, len(active_players)):
        result = HandEvaluator.compare_hands(best_player[1].hand, active_players[i][1].hand)
        if result == 2:  # Current player beats best
            best_player = active_players[i]
    
    return best_player[0], p_best, o_best, g_best

def make_state():
    deck = Deck()
    deck.reset()

    player = Player("You", starting_money=1000, is_bot=False)
    opponent = BaseAIPlayer("Opponent", money=1000)
    
    try:
        gemini_bot = GeminiBot("Gemini", money=1000, personality="balanced")
        print("✅ GeminiBot initialized successfully!")
    except Exception as e:
        print(f"⚠️ Could not initialize GeminiBot: {e}")
        print("Using BaseAIPlayer as fallback for third player")
        gemini_bot = BaseAIPlayer("Gemini (Fallback)", money=1000)
    
    player.receive_hand(deck.deal_hand(5))
    opponent.receive_hand(deck.deal_hand(5))
    gemini_bot.receive_hand(deck.deal_hand(5))

    state = {
        "deck": deck,
        "player": player,
        "opponent": opponent,
        "gemini_bot": gemini_bot,
        "pot": 0,
        "player_held": False,
        "opponent_held": False,
        "gemini_held": False,
        "status": "playing",
        "result": None,
    }
    return state


GAME_STATE = make_state()


def reset_hand_keep_balances():
    """Reset hand/pot but keep player balances intact."""
    global GAME_STATE
    if not GAME_STATE:
        GAME_STATE = make_state()
        return GAME_STATE

    deck = Deck()
    deck.reset()
    GAME_STATE["deck"] = deck

    player = GAME_STATE["player"]
    opponent = GAME_STATE["opponent"]
    gemini_bot = GAME_STATE.get("gemini_bot")

    player.reset_for_new_round()
    opponent.reset_for_new_round()
    if gemini_bot:
        gemini_bot.reset_for_new_round()

    GAME_STATE.update({
        "pot": 0,
        "player_held": False,
        "opponent_held": False,
        "gemini_held": False,
        "status": "playing",
        "result": None,
    })

    player.receive_hand(deck.deal_hand(5))
    opponent.receive_hand(deck.deal_hand(5))
    if gemini_bot:
        gemini_bot.receive_hand(deck.deal_hand(5))
    return GAME_STATE


def serialize_state(state, reveal_opponent=False):
    player = state["player"]
    opponent = state["opponent"]
    gemini_bot = state.get("gemini_bot")

    if len(player.hand) == 5 and len(opponent.hand) == 5 and (not gemini_bot or len(gemini_bot.hand) == 5):
        winner, p_best, o_best, g_best = evaluate_winner(state)
    else:
        winner = None
        p_best = ("—", 0)
        o_best = ("—", 0)
        g_best = ("—", 0)

    result = {
        "pot": state["pot"],
        "status": state["status"],
        "result": state["result"],
        "player": {
            "money": player.money,
            "current_bet": player.current_bet,
            "hole": [card_to_dict(c) for c in player.hand],
            "best": {"hand": p_best[0], "rank": p_best[1]},
            "held": state.get("player_held", False),
        },
        "opponent": {
            "money": opponent.money,
            "current_bet": opponent.current_bet,
            "hole": [card_to_dict(c, hidden=not reveal_opponent) for c in opponent.hand],
            "best": {"hand": o_best[0], "rank": o_best[1]},
            "held": state.get("opponent_held", False),
        },
        "winner_preview": winner,
    }
    
    if gemini_bot:
        result["gemini_bot"] = {
            "money": gemini_bot.money,
            "current_bet": gemini_bot.current_bet,
            "hole": [card_to_dict(c, hidden=not reveal_opponent) for c in gemini_bot.hand],
            "best": {"hand": g_best[0] if g_best else "—", "rank": g_best[1] if g_best else 0},
            "held": state.get("gemini_held", False),
        }
    
    return result


@app.route('/')
def index():
    return render_template('index.html')







@app.post('/api/new-game')
def api_new_game():
    global GAME_STATE
    GAME_STATE = make_state()
    return jsonify(serialize_state(GAME_STATE))


@app.post('/api/new-hand')
def api_new_hand():
    """Start a new hand but keep player balances."""
    global GAME_STATE
    GAME_STATE = reset_hand_keep_balances()
    return jsonify(serialize_state(GAME_STATE))


@app.get('/api/state')
def api_state():
    return jsonify(serialize_state(GAME_STATE, reveal_opponent=GAME_STATE.get("status") == "finished"))

def get_highest_bet(state):
    """Get the highest current bet among all players."""
    bets = [state["player"].current_bet, state["opponent"].current_bet]
    if state.get("gemini_bot"):
        bets.append(state["gemini_bot"].current_bet)
    return max(bets)

def all_players_held_or_folded(state):
    """Check if all active players have held or folded."""
    player_done = state.get("player_held") or state["player"].is_folded
    opponent_done = state.get("opponent_held") or state["opponent"].is_folded
    gemini_done = True
    if state.get("gemini_bot"):
        gemini_done = state.get("gemini_held") or state["gemini_bot"].is_folded
    return player_done and opponent_done and gemini_done


def process_ai_turns_in_order(state, run_gemini: bool = True):
    """Always act in order: human already acted -> opponent bot -> Gemini.

    The `run_gemini` flag gates calling the Gemini API to avoid unnecessary
    calls. Set to True only when it's the bot's turn after a player action
    that advances the round (e.g., hold or raise)."""
    opponent = state["opponent"]
    gemini_bot = state.get("gemini_bot")

    highest_bet = get_highest_bet(state)

    if hasattr(opponent, 'decide_action') and not state.get("opponent_held"):
        process_ai_decision(opponent, "opponent", state, highest_bet)
        highest_bet = get_highest_bet(state)

    if run_gemini and gemini_bot and hasattr(gemini_bot, 'decide_action') and not state.get("gemini_held"):
        process_ai_decision(gemini_bot, "gemini", state, highest_bet)

def process_ai_decision(ai_player, ai_name, state, _highest_bet):
    """Process an AI player's decision."""
    class MockBettingManager:
        def __init__(self, pot, current_bet):
            self.pot = pot
            self.current_round = type('obj', (object,), {'current_bet': current_bet})()
        
        def get_pot(self):
            return self.pot
    
    class MockGameState:
        def __init__(self, pot, current_bet):
            self.betting_manager = MockBettingManager(pot, current_bet)
    
    simple_state = {
        'pot': state["pot"],
        'player_bet': state["player"].current_bet,
        'opponent_bet': state["opponent"].current_bet
    }
    if state.get("gemini_bot"):
        simple_state['gemini_bet'] = state["gemini_bot"].current_bet
    
    current_highest_for_mock = get_highest_bet(state)
    gemini_state = MockGameState(state["pot"], current_highest_for_mock)
    
    try:
        if isinstance(ai_player, GeminiBot):
            ai_action, ai_amount = ai_player.decide_action(gemini_state, ai_player)
        else:
            ai_action, ai_amount = ai_player.decide_action(simple_state, ai_player)

        current_highest = get_highest_bet(state)

        if ai_action == "raise" and ai_amount:
            call_needed = max(0, current_highest - ai_player.current_bet)
            total_bet = call_needed + max(0, ai_amount)
            ai_bet = ai_player.place_bet(min(total_bet, ai_player.money))
            state["pot"] += ai_bet
            state[f"{ai_name}_held"] = False
            state["player_held"] = False
            state["opponent_held"] = False
            if state.get("gemini_bot"):
                state["gemini_held"] = False
            state[f"{ai_name}_held"] = False

        elif ai_action == "call":
            call_needed = max(0, current_highest - ai_player.current_bet)
            if call_needed > 0:
                call_amt = ai_player.place_bet(min(call_needed, ai_player.money))
                state["pot"] += call_amt
            state[f"{ai_name}_held"] = True

        elif ai_action == "fold":
            ai_player.is_folded = True
            state[f"{ai_name}_held"] = True

    except Exception as e:
        print(f"AI decision error for {ai_name}: {e}")
        current_highest = get_highest_bet(state)
        call_needed = max(0, current_highest - ai_player.current_bet)
        if call_needed > 0 and ai_player.money >= call_needed:
            call_amt = ai_player.place_bet(min(call_needed, ai_player.money))
            state["pot"] += call_amt
        state[f"{ai_name}_held"] = True

@app.post('/api/action')
def api_action():
    global GAME_STATE
    data = request.get_json(force=True, silent=True) or {}
    action = data.get("action")
    amount = int(data.get("amount", 0))

    if GAME_STATE["status"] != "playing":
        return jsonify(serialize_state(GAME_STATE, reveal_opponent=True))

    player = GAME_STATE["player"]
    opponent = GAME_STATE["opponent"]
    gemini_bot = GAME_STATE.get("gemini_bot")

    if action == "raise":
        bet = player.place_bet(max(0, amount))
        GAME_STATE["pot"] += bet
        GAME_STATE["player_held"] = False
        GAME_STATE["opponent_held"] = False
        GAME_STATE["gemini_held"] = False
        # After a player raise, allow bots to act; include Gemini
        process_ai_turns_in_order(GAME_STATE, run_gemini=True)
            
    elif action == "call":
        highest_bet = get_highest_bet(GAME_STATE)
        call_needed = highest_bet - player.current_bet
        if call_needed > 0:
            call_amt = player.place_bet(min(call_needed, player.money))
            GAME_STATE["pot"] += call_amt
        GAME_STATE["player_held"] = True
        # Do not immediately trigger Gemini on player call; wait for hold/raise
        
    elif action == "fold":
        player.is_folded = True
        GAME_STATE["player_held"] = True
        # Folding ends player's participation; do not trigger Gemini here
        
    elif action == "hold":
        highest_bet = get_highest_bet(GAME_STATE)
        if highest_bet > player.current_bet:
            return jsonify(serialize_state(GAME_STATE, reveal_opponent=False))
        
        GAME_STATE["player_held"] = True
        # After player holds (and is matched), let bots act; include Gemini
        process_ai_turns_in_order(GAME_STATE, run_gemini=True)
    
    if all_players_held_or_folded(GAME_STATE):
        winner, _, _, _ = evaluate_winner(GAME_STATE)
        GAME_STATE["status"] = "finished"
        GAME_STATE["result"] = winner

        if winner == "player":
            player.win_pot(GAME_STATE["pot"])
        elif winner == "opponent":
            opponent.win_pot(GAME_STATE["pot"])
        elif winner == "gemini_bot" and gemini_bot:
            gemini_bot.win_pot(GAME_STATE["pot"])
        else:  # tie
            active_count = sum([not p.is_folded for p in [player, opponent, gemini_bot] if p])
            if active_count > 0:
                share = GAME_STATE["pot"] // active_count
                if not player.is_folded:
                    player.win_pot(share)
                if not opponent.is_folded:
                    opponent.win_pot(share)
                if gemini_bot and not gemini_bot.is_folded:
                    gemini_bot.win_pot(share)
        GAME_STATE["pot"] = 0
        return jsonify(serialize_state(GAME_STATE, reveal_opponent=True))

    return jsonify(serialize_state(GAME_STATE, reveal_opponent=False))


if __name__ == '__main__':
    app.run(debug=True)
