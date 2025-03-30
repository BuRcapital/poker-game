import os
import time
from poker_engine import PokerGame
from crypto_integration import CryptoWallet

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_player_action(player, game):
    print(f"\n{player['name']}'s turn (Chips: {player['chips']})")
    print(f"Community cards: {' '.join(game.community_cards) if game.community_cards else 'None'}")
    print(f"Your hand: {' '.join(player['hand'])}")
    print(f"Current bet: {game.current_bet}, Your bet: {player.get('current_bet', 0)}")
    
    valid_actions = []
    print("\nAvailable actions:")
    
    # Check
    if player.get('current_bet', 0) == game.current_bet:
        print("1. Check")
        valid_actions.append('check')
    
    # Call
    if player.get('current_bet', 0) < game.current_bet:
        call_amount = game.current_bet - player.get('current_bet', 0)
        print(f"2. Call ({call_amount})")
        valid_actions.append('call')
    
    # Raise
    print("3. Raise")
    valid_actions.append('raise')
    
    # Fold
    print("4. Fold")
    valid_actions.append('fold')
    
    while True:
        choice = input("Choose action (1-4): ")
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(valid_actions):
                action = valid_actions[choice_idx]
                
                if action == 'raise':
                    min_raise = game.current_bet * 2 if game.current_bet > 0 else game.big_blind
                    max_raise = player['chips']
                    while True:
                        try:
                            amount = int(input(f"Enter raise amount ({min_raise}-{max_raise}): "))
                            if min_raise <= amount <= max_raise:
                                return action, amount
                            print("Invalid amount!")
                        except ValueError:
                            print("Please enter a number!")
                return action, 0
            print("Invalid choice!")
        except ValueError:
            print("Please enter a number!")

def main():
    clear_screen()
    print("Welcome to Texas Hold'em Poker with Crypto Integration!")
    
    # Set up players
    num_players = 0
    while num_players < 2 or num_players > 8:
        try:
            num_players = int(input("Enter number of players (2-8): "))
        except ValueError:
            print("Please enter a number!")
    
    players = []
    for i in range(num_players):
        name = input(f"Enter name for Player {i+1}: ")
        players.append({
            'name': name,
            'chips': 1000,
            'hand': [],
            'current_bet': 0,
            'folded': False,
            'all_in': False
        })
    
    # Crypto setup
    use_crypto = input("Would you like to use crypto wallets? (y/n): ").lower() == 'y'
    wallets = {}
    
    if use_crypto:
        for player in players:
            print(f"\nSetting up wallet for {player['name']}")
            use_wallet = input("Would you like to connect a wallet? (y/n): ").lower() == 'y'
            if use_wallet:
                wallet = CryptoWallet()
                private_key = input("Enter your private key (for testing only!): ")
                if wallet.connect_wallet(private_key):
                    wallets[player['name']] = wallet
                    print(f"Connected wallet with balance: {wallet.get_balance()} ETH")
                else:
                    print("Failed to connect wallet")
    
    # Game setup
    small_blind = 10
    big_blind = 20
    dealer_pos = 0
    
    while True:
        clear_screen()
        print("\nStarting new hand!")
        
        # Reset for new hand
        game = PokerGame(players, small_blind, big_blind)
        active_players = [p for p in players if p['chips'] > 0]
        
        # Post blinds
        sb_pos = (dealer_pos + 1) % len(active_players)
        bb_pos = (dealer_pos + 2) % len(active_players)
        
        sb_player = active_players[sb_pos]
        bb_player = active_players[bb_pos]
        
        sb_amount = min(small_blind, sb_player['chips'])
        bb_amount = min(big_blind, bb_player['chips'])
        
        sb_player['chips'] -= sb_amount
        sb_player['current_bet'] = sb_amount
        bb_player['chips'] -= bb_amount
        bb_player['current_bet'] = bb_amount
        
        game.current_bet = bb_amount
        game.pot = sb_amount + bb_amount
        
        # Deal hole cards
        game.deal_hole_cards()
        
        # Pre-flop betting
        print("\nPre-flop betting round:")
        current_pos = (bb_pos + 1) % len(active_players)
        betting_complete = False
        
        while not betting_complete:
            player = active_players[current_pos]
            
            if not player['folded'] and not player['all_in']:
                clear_screen()
                action, amount = get_player_action(player, game)
                
                if action == 'fold':
                    player['folded'] = True
                elif action == 'call':
                    call_amount = game.current_bet - player.get('current_bet', 0)
                    player['chips'] -= call_amount
                    player['current_bet'] = game.current_bet
                    game.pot += call_amount
                elif action == 'raise':
                    player['chips'] -= amount
                    player['current_bet'] = amount
                    game.current_bet = amount
                    game.pot += amount
                    # Reset betting for other players
                    current_pos = (current_pos + 1) % len(active_players)
                    continue
            
            current_pos = (current_pos + 1) % len(active_players)
            
            # Check if betting round is complete
            if current_pos == bb_pos:
                all_acted = True
                for p in active_players:
                    if not p['folded'] and not p['all_in'] and p['current_bet'] < game.current_bet:
                        all_acted = False
                        break
                if all_acted:
                    betting_complete = True
        
        # Flop
        remaining_players = [p for p in active_players if not p['folded']]
        if len(remaining_players) > 1:
            game.deal_flop()
            print("\nFlop:", ' '.join(game.community_cards))
            
            # Reset for new betting round
            for p in active_players:
                p['current_bet'] = 0
            game.current_bet = 0
            
            # Flop betting (similar to pre-flop)
            # ... (implementation similar to pre-flop betting)
        
        # Turn and River would follow similar pattern
        
        # Showdown
        remaining_players = [p for p in active_players if not p['folded']]
        if len(remaining_players) > 1:
            winners = game.determine_winner(remaining_players)
            print("\nShowdown!")
            for p in remaining_players:
                print(f"{p['name']}'s hand: {' '.join(p['hand'])}")
            
            if len(winners) == 1:
                winner = winners[0]
                win_amount = game.pot
                winner['chips'] += win_amount
                print(f"\n{winner['name']} wins {win_amount} chips!")
            else:
                win_amount = game.pot // len(winners)
                for winner in winners:
                    winner['chips'] += win_amount
                print(f"\nSplit pot between {', '.join(w['name'] for w in winners)} - each gets {win_amount} chips!")
        
        # Update dealer position
        dealer_pos = (dealer_pos + 1) % len(players)
        
        # Check for eliminated players
        for player in players:
            if player['chips'] <= 0:
                print(f"\n{player['name']} is out of chips!")
                if player['name'] in wallets:
                    # Withdraw remaining balance
                    wallet = wallets[player['name']]
                    balance = wallet.get_balance()
                    if balance > 0:
                        print(f"Withdrawing {balance} ETH from wallet")
                        wallet.withdraw_from_game(balance)
        
        # Continue playing?
        continue_playing = input("\nContinue playing? (y/n): ").lower() == 'y'
        if not continue_playing:
            break

if __name__ == "__main__":
    main()
