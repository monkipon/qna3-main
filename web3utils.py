from eth_account import Account
from eth_account.messages import encode_defunct, SignableMessage
from web3 import Web3
from web3.eth import AsyncEth


class Web3Utils:
    def __init__(self, rpc: str = None, key: str = None, is_async: bool = False):
        self.w3 = None
        if key:
            self.mnemonic = ""
            self.account = Account.from_key(key)
            self.address = self.account.address
            self.key = key
        self.is_async = is_async
        self.define_new_provider(rpc)

    async def get_balance(self, address: str | None = None):
        if not address:
            address = self.address
        return await self.w3.eth.get_balance(account=address)

    def define_new_provider(self, http_provider: str):
        if self.is_async:
            self.w3 = Web3(Web3.AsyncHTTPProvider(http_provider), modules={'eth': (AsyncEth,)}, middlewares=[])
        else:
            self.w3 = Web3(Web3.AsyncHTTPProvider(http_provider),)

    def create_wallet(self):
        self.account, self.mnemonic = Account.create_with_mnemonic()
        return self.account, self.mnemonic

    def sign(self, encoded_msg: SignableMessage):
        return self.w3.eth.account.sign_message(encoded_msg, self.account.key)

    def get_signed_code(self, msg) -> str:
        return self.sign(encode_defunct(text=msg)).signature.hex()
