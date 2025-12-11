"""
Ollama-based poker bot implementation
"""

import json
import requests
import re
from typing import Tuple, Optional, Dict
from ai_player import BaseAIPlayer
from hand_evaluator import HandEvaluator

model = "qwen2.5"

class OllamaBot(BaseAIPlayer):
    """
    Poker player powered by local LLM via Ollama.
    No API costs, runs completely offline.
    """

    SYSTEM_PROMPTS = {
        "conservative": """You are a conservative poker player. You play tight and only bet on strong hands. 
        You fold weak hands quickly and avoid risky situations. You prefer to wait for premium hands 
        before committing chips.""",

        "balanced": """You are a balanced poker player. You mix conservative and aggressive play 
        depending on the situation. You consider pot odds, hand strength, and position. 
        You can bluff occasionally but prefer solid play.""",

        "aggressive": """You are an aggressive poker player. You bet and raise frequently to apply 
        pressure. You're willing to bluff and take risks. You use aggression to push opponents 
        out of pots and build big stacks quickly."""
    }

    def __init__(self, name: str, money: int = 1000,
                 model: str = model,
                 personality: str = "balanced",
                 ollama_url: str = "http://localhost:11434"):
        """
        Initialize Ollama-powered bot.

        Args:
            name: Bot name
            money: Starting money
            model: Ollama model to use (e.g., "qwen2.5")
            personality: "conservative", "balanced", or "aggressive"
            ollama_url: Ollama API URL
        """
        super().__init__(name, money)
        self.model = model
        self.personality = personality
        self.ollama_url = ollama_url
        self.system_prompt = self.SYSTEM_PROMPTS[personality]
        self.decision_history = []

        # Check if Ollama is running
        self._check_ollama_connection()

    def _check_ollama_connection(self):
        """Verify Ollama is running and model is available."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]

                if not any(self.model in name for name in model_names):
                    print(f"Model '{self.model}' not found. Available models:")
                    for name in model_names:
                        print(f"    • {name}")
                    print(f"\nTo download: ollama pull {self.model}")
        except Exception as e:
            print(f"Cannot connect to Ollama: {e}")
            print("Make sure Ollama is running: https://ollama.ai")

    def decide_action(self, game_state, player) -> Tuple[str, Optional[int]]:
        """
        Make a decision using local LLM via Ollama.

        Args:
            game_state: Current GameState object
            player: Current Player object

        Returns:
            Tuple of (action, amount) where action is 'call', 'raise', or 'fold'
        """
        try:
            context = self._prepare_context(game_state, player)

            prompt = self._build_prompt(context)

            response_text = self._call_ollama(prompt)

            decision = self._parse_response(response_text)

            validated_action, validated_amount = self._validate_decision(
                decision, game_state, player
            )

            self._log_decision(player, context, decision)

            return validated_action, validated_amount

        except Exception as e:
            print(f"Ollama error: {e}, using fallback strategy")
            return self._fallback_decision(game_state, player)


    def _prepare_context(self, game_state, player) -> Dict:
        """Prepare game context for LLM."""
        # Evaluate hand
        ranking, value, name = HandEvaluator.evaluate_hand(player.hand)

        # Get betting info
        pot = game_state.betting_manager.get_pot()
        current_bet = game_state.betting_manager.current_round.current_bet
        amount_to_call = current_bet - player.current_bet

        # Calculate pot odds
        pot_odds = self._calculate_pot_odds(pot, amount_to_call) if amount_to_call > 0 else float('inf')

        # Get available actions
        available_actions = self._get_available_actions(player, current_bet)

        # Estimate win probability
        win_probability = self._estimate_win_probability(ranking)

        return {
            'hand': player.hand,
            'hand_name': name,
            'hand_ranking': ranking,
            'hand_value': value,
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
        """Build decision prompt for LLM."""
        hand_str = ", ".join([f"{card.get_rank_name()} of {card.suit}"
                              for card in context['hand']])

        prompt = f"""POKER DECISION TASK

        SYSTEM: {self.system_prompt}

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
        3. If raising, specify amount (10-100)
        4. Provide brief reasoning
        5. Respond ONLY with JSON, no other text

        JSON RESPONSE:"""

        return prompt


    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API."""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,  # Moderate creativity
                        "num_predict": 150,  # Limit response length
                        "top_p": 0.9,
                        "top_k": 40,
                        "stop": ["\n\n", "QUESTION:", "SYSTEM:", "USER:"]
                    }
                },
                timeout=30
            )

            if response.status_code != 200:
                raise Exception(f"Ollama error: {response.status_code}")

            result = response.json()
            return result['response'].strip()

        except requests.exceptions.Timeout:
            raise Exception("Ollama request timed out")
        except Exception as e:
            raise Exception(f"Ollama call failed: {e}")

    def _parse_response(self, response_text: str) -> Dict:
        """Parse LLM response to extract JSON decision."""
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

        # Validate required fields
        if 'action' not in decision:
            raise ValueError("Response missing 'action' field")

        if decision['action'] not in ['call', 'raise', 'fold']:
            raise ValueError(f"Invalid action: {decision['action']}")

        return decision

    def _clean_response(self, text: str) -> str:
        """Clean LLM response to extract JSON."""
        # Remove markdown code blocks
        text = re.sub(r'```json\s*\n?', '', text, flags=re.IGNORECASE)
        text = re.sub(r'```\s*\n?', '', text)

        # Remove common prefixes
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
        """Validate and adjust LLM decision to be legal."""
        action = decision['action']
        amount = decision.get('amount')

        current_bet = game_state.betting_manager.current_round.current_bet
        amount_to_call = current_bet - player.current_bet

        # Validate raise amount
        if action == 'raise':
            if amount is None or amount <= 0:
                # Use default raise amount
                amount = max(20, int(game_state.betting_manager.get_pot() * 0.3))

            # Ensure we can afford it
            total_needed = amount_to_call + amount
            if total_needed > player.money:
                # All-in
                amount = player.money - amount_to_call
                if amount <= 0:
                    # Can't raise, just call
                    action = 'call'
                    amount = None

        elif action == 'call':
            amount = None

        elif action == 'fold':
            amount = None

        return action, amount

    def _fallback_decision(self, game_state, player) -> Tuple[str, Optional[int]]:
        """Simple rule-based fallback when LLM fails."""
        hand_strength = self._get_hand_strength(player.hand)

        if hand_strength >= 7:
            return 'raise', 50
        elif hand_strength >= 4:
            return 'call', None
        else:
            return 'fold', None

    def _estimate_win_probability(self, hand_ranking: int) -> float:
        """Rough estimate of win probability based on hand ranking."""
        probabilities = {
            10: 0.999,  # Royal Flush
            9: 0.95,  # Straight Flush
            8: 0.90,  # Four of a Kind
            7: 0.85,  # Full House
            6: 0.75,  # Flush
            5: 0.65,  # Straight
            4: 0.55,  # Three of a Kind
            3: 0.45,  # Two Pair
            2: 0.35,  # One Pair
            1: 0.20   # High Card
        }
        return probabilities.get(hand_ranking, 0.5)

    def _log_decision(self, player, context: Dict, decision: Dict):
        """Log decision for analysis."""
        self.decision_history.append({
            'hand': context['hand_name'],
            'action': decision['action'],
            'amount': decision.get('amount'),
            'reasoning': decision.get('reasoning', ''),
            'confidence': decision.get('confidence', 0.0)
        })

    def get_strategy_name(self) -> str:
        """Get strategy description."""
        return f"Ollama Bot ({self.model}, {self.personality})"

    def get_decision_history(self):
        """Get history of decisions for analysis."""
        return self.decision_history


def check_ollama_status(ollama_url: str = "http://localhost:11434"):
    """
    Check if Ollama is running and show available models.

    Returns:
        tuple: (is_running: bool, available_models: list)
    """
    try:
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [m['name'] for m in models]
            return True, model_names
        return False, []
    except:
        return False, []


def create_ollama_bot(name: str, money: int = 1000,
                      personality: str = "balanced",
                      model: str = model) -> OllamaBot:
    """
    Create an Ollama bot with sensible defaults.

    Args:
        name: Bot name
        money: Starting money
        personality: "conservative", "balanced", or "aggressive"
        model: Ollama model (default: qwen2.5 for good balance)

    Returns:
        OllamaBot instance
    """
    return OllamaBot(
        name=name,
        money=money,
        model=model,
        personality=personality
    )
