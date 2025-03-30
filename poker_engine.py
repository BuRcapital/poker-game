import random
from collections import Counter

class PokerGame:
    def __init__(self, players, small_blind=10, big_blind=20):
        self.players = players
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.deck = []
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.reset_deck()
        
    def reset_deck(self):
        suits = ['♠', '♥', '♦', '♣']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.deck = [f"{rank}{suit}" for suit in suits for rank in ranks]
        random.shuffle(self.deck)
        
    def deal_hole_cards(self):
        for player in self.players:
            if len(self.deck) >= 2:
                player['hand'] = [self.deck.pop(), self.deck.pop()]
                
    def deal_flop(self):
        if len(self.deck) >= 3:
            # Burn one card before flop
            self.deck.pop()
            self.community_cards = [self.deck.pop() for _ in range(3)]
            
    def deal_turn_or_river(self):
        if len(self.deck) >= 1:
            # Burn one card before turn/river
            self.deck.pop()
            self.community_cards.append(self.deck.pop())
            
    def evaluate_hand(self, hand):
        # Convert cards to numerical values
        rank_order = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, 
                     '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        
        values = sorted([rank_order[card[:-1]] for card in hand], reverse=True)
        suits = [card[-1] for card in hand]
        
        # Combine with community cards
        all_cards = hand + self.community_cards
        all_values = sorted([rank_order[card[:-1]] for card in all_cards], reverse=True)
        all_suits = [card[-1] for card in all_cards]
        
        value_counts = Counter(all_values)
        suit_counts = Counter(all_suits)
        
        # Check for flush
        flush_suit = None
        for suit, count in suit_counts.items():
            if count >= 5:
                flush_suit = suit
                break
        
        # Check for straight
        straight = False
        unique_values = sorted(list(set(all_values)), reverse=True)
        if len(unique_values) >= 5:
            for i in range(len(unique_values) - 4):
                if unique_values[i] - unique_values[i+4] == 4:
                    straight = True
                    straight_high = unique_values[i]
                    break
        
        # Check for straight flush
        if flush_suit and straight:
            flush_cards = [card for card in all_cards if card[-1] == flush_suit]
            flush_values = sorted([rank_order[card[:-1]] for card in flush_cards], reverse=True)
            unique_flush_values = sorted(list(set(flush_values)), reverse=True)
            if len(unique_flush_values) >= 5:
                for i in range(len(unique_flush_values) - 4):
                    if unique_flush_values[i] - unique_flush_values[i+4] == 4:
                        if unique_flush_values[i] == 14:  # Royal flush
                            return (10,)
                        else:  # Straight flush
                            return (9, unique_flush_values[i])
        
        # Four of a kind
        if 4 in value_counts.values():
            quad_value = [v for v, count in value_counts.items() if count == 4][0]
            kicker = max(v for v in all_values if v != quad_value)
            return (8, quad_value, kicker)
        
        # Full house
        if sorted(value_counts.values()) == [2, 3] or list(value_counts.values()).count(3) >= 2:
            trips = sorted([v for v, count in value_counts.items() if count >= 3], reverse=True)[:2]
            pairs = sorted([v for v, count in value_counts.items() if count >= 2], reverse=True)
            if len(trips) >= 2:  # Two three of a kinds
                return (7, trips[0], trips[1])
            else:
                return (7, trips[0], max(p for p in pairs if p != trips[0]))
        
        # Flush
        if flush_suit:
            flush_values = sorted([rank_order[card[:-1]] for card in all_cards if card[-1] == flush_suit], reverse=True)[:5]
            return (6,) + tuple(flush_values)
        
        # Straight
        if straight:
            return (5, straight_high)
        
        # Three of a kind
        if 3 in value_counts.values():
            trips = max(v for v, count in value_counts.items() if count == 3)
            kickers = sorted([v for v in all_values if v != trips], reverse=True)[:2]
            return (4, trips, kickers[0], kickers[1])
        
        # Two pair
        pairs = sorted([v for v, count in value_counts.items() if count == 2], reverse=True)
        if len(pairs) >= 2:
            kicker = max(v for v in all_values if v not in pairs[:2])
            return (3, pairs[0], pairs[1], kicker)
        
        # One pair
        if len(pairs) == 1:
            kickers = sorted([v for v in all_values if v != pairs[0]], reverse=True)[:3]
            return (2, pairs[0], kickers[0], kickers[1], kickers[2])
        
        # High card
        return (1,) + tuple(sorted(all_values, reverse=True)[:5])
    
    def determine_winner(self, active_players):
        best_hand = None
        winners = []
        
        for player in active_players:
            if 'hand' not in player or len(player['hand']) != 2:
                continue
                
            hand_strength = self.evaluate_hand(player['hand'])
            
            if not best_hand or hand_strength > best_hand:
                best_hand = hand_strength
                winners = [player]
            elif hand_strength == best_hand:
                winners.append(player)
        
        return winners
    
    def betting_round(self, active_players, dealer_position):
        # Implement betting logic here
        pass
