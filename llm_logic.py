"""
Gemini-based poker bot implementation

Uses Google's Gemini API for poker decision-making.
Requires GEMINI_API_KEY environment variable to be set.
"""

import json
import os
import re
from typing import Tuple, Optional, Dict
from google import genai
from ai_player import BaseAIPlayer
from hand_evaluator import HandEvaluator


class GeminiBot(BaseAIPlayer):
    """
    Poker player powered by Google Gemini API.
    Uses gemini-2.5-flash model for fast, intelligent decisions.
    """

    SYSTEM_PROMPTS = {
        "conservative": """You are a conservative poker player. You play tight and only bet on strong hands. 
        You fold weak hands quickly and avoid risky situations. You prefer to wait for premium hands 
        before committing chips. Only raise with very strong hands (Full House or better).""",

        "balanced": """You are a balanced poker player. You mix conservative and aggressive play 
        depending on the situation. You consider pot odds, hand strength, and position. Play like a seasoned player and willing to take risks even if its a gamble.""",

        "aggressive": """You are an aggressive poker player. You bet and raise frequently to apply 
        pressure. You're willing to bluff and take risks. You use aggression to push opponents 
        out of pots. Raise with strong hands and occasionally with weaker hands as bluffs."""
    }

    def __init__(self, name: str, money: int = 1000,
                 model: str = "gemini-2.5-flash",
                 personality: str = "balanced",
                 api_key: Optional[str] = None):
        """
        Initialize Gemini-powered bot.

        Args:
            name: Bot name
            money: Starting money
            model: Gemini model to use (default: "gemini-2.5-flash")
            personality: "conservative", "balanced", or "aggressive"
            api_key: Gemini API key (if not provided, uses GEMINI_API_KEY env var)
        """
        super().__init__(name, money)
        self.model_name = model
        self.personality = personality
        self.system_prompt = self.SYSTEM_PROMPTS[personality]
        self.decision_history = []

        self._initialize_client(api_key)

    def _initialize_client(self, api_key: Optional[str] = None):
        """Initialize Gemini client with API key."""
        try:
            if api_key:
                os.environ['GEMINI_API_KEY'] = api_key

            if 'GEMINI_API_KEY' not in os.environ:
                raise ValueError(
                    "GEMINI_API_KEY not found. Please set it.\n"
                    "Or pass api_key parameter to constructor."
                )

            self.client = genai.Client()
            print(f"Gemini client initialized successfully!")

        except Exception as e:
            print(f"Error initializing Gemini client: {e}")
            print("Please ensure you have set the GEMINI_API_KEY environment variable.")
            raise

    def decide_action(self, game_state, player) -> Tuple[str, Optional[int]]:
        """
        Make a decision using Gemini API.

        Args:
            game_state: Current GameState object
            player: Current Player object

        Returns:
            Tuple of (action, amount) where action is 'call', 'raise', or 'fold'
        """
        try:
            context = self._prepare_context(game_state, player)
            prompt = self._build_prompt(context)
            response_text = self._call_gemini(prompt)
            decision = self._parse_response(response_text)
            validated_action, validated_amount = self._validate_decision(
                decision, game_state, player
            )

            self._log_decision(player, context, decision)
            return validated_action, validated_amount
        except Exception as e:
            print(f"Gemini error: {e}, using fallback strategy")
            return self._fallback_decision(game_state, player)

    def _prepare_context(self, game_state, player) -> Dict:
        """Prepare game context for Gemini."""
        hand_eval = HandEvaluator.evaluate_hand(player.hand)
        # Support both 2-tuple and 3-tuple return shapes defensively
        if isinstance(hand_eval, (list, tuple)):
            if len(hand_eval) >= 2:
                hand_name, hand_value = hand_eval[0], hand_eval[1]
            else:
                hand_name, hand_value = hand_eval[0], 0
        else:
            hand_name, hand_value = str(hand_eval), 0
        hand_ranking = HandEvaluator.HAND_RANKINGS.get(hand_name, 1)

        pot = game_state.betting_manager.get_pot()
        current_bet = game_state.betting_manager.current_round.current_bet
        amount_to_call = max(0, current_bet - player.current_bet)

        pot_odds = self._calculate_pot_odds(pot, amount_to_call) if amount_to_call > 0 else float('inf')
        available_actions = self._get_available_actions(player, current_bet)
        win_probability = self._estimate_win_probability_simple(hand_ranking)

        return {
            'hand': player.hand,
            'hand_name': hand_name,
            'hand_ranking': hand_ranking,
            'hand_value': hand_value,
            'money': player.money,
            'current_bet': player.current_bet,
            'bet_to_match': current_bet,
            'amount_to_call': amount_to_call,
            'pot': pot,
            'pot_odds': pot_odds,
            'available_actions': available_actions,
            'win_probability': win_probability
        }

    def _build_prompt(self, context: Dict) -> str:
        """Build decision prompt for Gemini."""
        hand_str = ", ".join([f"{card.get_rank_name()} of {card.suit}"
                              for card in context['hand']])

        prompt = f"""{self.system_prompt}

POKER DECISION TASK

CURRENT GAME STATE:
- Your hand: {hand_str}
- Hand type: {context['hand_name']} (strength: {context['hand_ranking']}/10)
- Your chips: ${context['money']}
- Current bet to match: ${context['bet_to_match']}
- Your current bet: ${context['current_bet']}
- Amount to call: ${context['amount_to_call']}
- Pot size: ${context['pot']}
- Pot odds: {context['pot_odds']:.2f}:1
- Estimated win probability: {context['win_probability']:.1%}
- Available actions: {', '.join(context['available_actions'])}

INSTRUCTIONS:
1. Analyze the situation based on hand strength, pot odds, and win probability
2. Decide: call, raise, or fold
3. If raising, specify an integer chip amount (no explicit maximum; stay within stack)
4. Provide brief reasoning
5. Respond ONLY with JSON in this exact format:
{"action": "call/raise/fold", "amount": 50, "reasoning": "your reasoning", "confidence": 0.8}

JSON RESPONSE:"""
        return prompt

    def _call_gemini(self, prompt: str) -> str:
        """Call Gemini API."""
        try:
            print(f"Sending request to Gemini ({self.model_name})...")

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            response_text = response.text.strip()
            print(f"✅ Received response from Gemini: {response_text}")
            return response_text

        except Exception as e:
            raise Exception(f"Gemini API call failed: {e}")

    def _parse_response(self, response_text: str) -> Dict:
        """Parse Gemini response to extract JSON decision."""
        response_text = self._clean_response(response_text)

        try:
            decision = json.loads(response_text)
        except json.JSONDecodeError:
            json_match = re.search(r'\{[^}]+\}', response_text)
            if json_match:
                try:
                    decision = json.loads(json_match.group(0))
                except:
                    raise ValueError("Could not parse JSON from response")
            else:
                raise ValueError("No JSON found in response")
        if 'action' not in decision:
            raise ValueError("Response missing 'action' field")
        if decision['action'] not in ['call', 'raise', 'fold']:
            raise ValueError(f"Invalid action: {decision['action']}")
        print(f"✅ Parsed Gemini decision: {decision}")
        return decision

    def _clean_response(self, text: str) -> str:
        """Clean Gemini response to extract JSON."""
        text = re.sub(r'```json\s*\n?', '', text, flags=re.IGNORECASE)
        text = re.sub(r'```\s*\n?', '', text)
        prefixes = [
            r'JSON RESPONSE:\s*',
            r'Response:\s*',
            r'Answer:\s*',
            r'Here is (?:the|my) (?:decision|response):\s*',
        ]
        for prefix in prefixes:
            text = re.sub(prefix, '', text, flags=re.IGNORECASE)
        json_match = re.search(r'(\{[^}]+\})', text, re.DOTALL)
        if json_match:
            text = json_match.group(1)
        return text.strip()

    def _validate_decision(self, decision: Dict, game_state, player) -> Tuple[str, Optional[int]]:
        """Validate and adjust Gemini decision to be legal."""
        action = decision['action']
        amount = decision.get('amount')
        current_bet = game_state.betting_manager.current_round.current_bet
        amount_to_call = max(0, current_bet - player.current_bet)

        stack = player.money
        pot = game_state.betting_manager.get_pot()
        hand_strength = self._get_hand_strength(player.hand)

        if action == 'raise':
            if amount is None or amount <= 0:
                amount = max(int(pot * 0.25), int(stack * 0.07), 10)
            total_needed = amount_to_call + amount
            if total_needed > stack:
                amount = stack - amount_to_call
                if amount <= 0:
                    action = 'call'
                    amount = None
        elif action == 'call':
            if hand_strength >= 7 and stack > amount_to_call + 10:
                amount = max(int(pot * 0.2), int(stack * 0.05), 10)
                action = 'raise'
            else:
                amount = None
        elif action == 'fold':
            amount = None
        return action, amount

    def _fallback_decision(self, game_state, player) -> Tuple[str, Optional[int]]:
        """Simple rule-based fallback when Gemini fails."""
        hand_strength = self._get_hand_strength(player.hand)

        if hand_strength >= 7:
            return 'raise', 50
        elif hand_strength >= 4:
            return 'call', None
        else:
            return 'fold', None

    def _log_decision(self, player, context: Dict, decision: Dict):
        """Log decision for analysis."""
        self.decision_history.append({
            'hand': context['hand_name'],
            'action': decision['action'],
            'amount': decision.get('amount'),
            'reasoning': decision.get('reasoning', ''),
            'confidence': decision.get('confidence', 0.0)
        })

    def _get_hand_strength(self, hand: list) -> int:
        """Return numeric strength (1-10) for a hand."""
        hand_eval = HandEvaluator.evaluate_hand(hand)
        hand_name = hand_eval[0] if isinstance(hand_eval, (list, tuple)) else str(hand_eval)
        return HandEvaluator.HAND_RANKINGS.get(hand_name, 1)

    def _estimate_win_probability_simple(self, hand_ranking: int) -> float:
        """Coarse win probability estimate from ranking to keep prompts grounded."""
        return max(0.05, min(0.97, hand_ranking / 10.5 + 0.05))

    def _get_available_actions(self, player, current_bet: int):
        """Return legal actions given current bet state."""
        actions = ['fold']
        amount_to_call = max(0, current_bet - player.current_bet)
        if player.money >= amount_to_call:
            actions.append('call')
        if player.money > amount_to_call:
            actions.append('raise')
        return actions

    def _calculate_pot_odds(self, pot: int, bet_to_call: int) -> float:
        """Simple pot-odds ratio; returns infinity when nothing to call."""
        if bet_to_call <= 0:
            return float('inf')
        if pot <= 0:
            return float('inf')
        return pot / bet_to_call

    def get_strategy_name(self) -> str:
        """Get strategy description."""
        return f"Gemini Bot ({self.model_name}, {self.personality})"

    def get_decision_history(self):
        """Get history of decisions for analysis."""
        return self.decision_history


def create_gemini_bot(name: str, money: int = 1000,
                      personality: str = "balanced",
                      model: str = "gemini-2.5-flash",
                      api_key: Optional[str] = None) -> GeminiBot:
    """
    Create a Gemini bot with sensible defaults.

    Args:
        name: Bot name
        money: Starting money
        personality: "conservative", "balanced", or "aggressive"
        model: Gemini model (default: gemini-2.5-flash for speed)
        api_key: Optional API key (otherwise uses GEMINI_API_KEY env var)

    Returns:
        GeminiBot instance
    """
    return GeminiBot(
        name=name,
        money=money,
        model=model,
        personality=personality,
        api_key=api_key
    )


def check_gemini_setup():
    """
    Check if Gemini API is properly set up.

    Returns:
        tuple: (is_setup: bool, message: str)
    """
    if 'GEMINI_API_KEY' not in os.environ:
        return False, "GEMINI_API_KEY not found in environment variables"
    try:
        client = genai.Client()
        return True, "Gemini API is properly configured"
    except Exception as e:
        return False, f"Error initializing Gemini: {e}"