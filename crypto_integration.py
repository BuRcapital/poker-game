from web3 import Web3
import json

class CryptoWallet:
    def __init__(self, provider_url="http://127.0.0.1:8545"):  # Default to local Ganache
        self.w3 = Web3(Web3.HTTPProvider(provider_url))
        self.contract = None
        self.account = None
        
    def connect_wallet(self, private_key):
        try:
            self.account = self.w3.eth.account.privateKeyToAccount(private_key)
            return True
        except:
            return False
            
    def load_contract(self, contract_address, abi_path):
        with open(abi_path) as f:
            abi = json.load(f)
        self.contract = self.w3.eth.contract(address=contract_address, abi=abi)
        
    def deposit_to_game(self, amount_eth):
        if not self.contract or not self.account:
            return False
            
        tx = self.contract.functions.deposit().buildTransaction({
            'from': self.account.address,
            'value': self.w3.toWei(amount_eth, 'ether'),
            'gas': 200000,
            'gasPrice': self.w3.toWei('50', 'gwei'),
            'nonce': self.w3.eth.getTransactionCount(self.account.address),
        })
        
        signed_tx = self.w3.eth.account.signTransaction(tx, self.account.privateKey)
        tx_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        return tx_hash.hex()
        
    def withdraw_from_game(self, amount_eth):
        if not self.contract or not self.account:
            return False
            
        tx = self.contract.functions.withdraw(self.w3.toWei(amount_eth, 'ether')).buildTransaction({
            'from': self.account.address,
            'gas': 200000,
            'gasPrice': self.w3.toWei('50', 'gwei'),
            'nonce': self.w3.eth.getTransactionCount(self.account.address),
        })
        
        signed_tx = self.w3.eth.account.signTransaction(tx, self.account.privateKey)
        tx_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        return tx_hash.hex()
    
    def get_balance(self):
        if not self.account:
            return 0
        return self.w3.fromWei(self.w3.eth.getBalance(self.account.address), 'ether')
