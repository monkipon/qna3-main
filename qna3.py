import asyncio

import aiohttp
import pyuseragents
from web3utils import *
from config import REFFERAL_CODE


class Qna3:
    def __init__(self, key, proxy: str = None):
        self.credit = None
        self.checkInDays = None
        self.todayCount = None
        self.token = None
        self.account = Web3Utils(key=key)
        self.account.define_new_provider('https://opbnb.publicnode.com', is_async=True)
        self.proxy = proxy
        if self.proxy is not None:
            self.proxy_ip = self.proxy.split('@')[1]
        else:
            self.proxy_ip = 'No Proxy'

        headers = {
            'authority': 'api.qna3.ai',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7',
            'content-type': 'application/json',
            'origin': 'https://qna3.ai',
            'sec-ch-ua-platform': '"Windows"',
            'user-agent': pyuseragents.random(),
            'x-lang': 'english',
        }

        self.session = aiohttp.ClientSession(headers=headers)

    async def get_token(self):
        try:
            msg = "AI + DYOR = Ultimate Answer to Unlock Web3 Universe"
            json_data = {
                'wallet_address': self.account.address,
                'signature': self.account.get_signed_code(msg),
                'invite_code': REFFERAL_CODE,
            }

            params = {
                'via': 'wallet',
            }

            url = "https://api.qna3.ai/api/v2/auth/login"
            response = await self.session.post(url, json=json_data, params=params, proxy=self.proxy)
            response_data = await response.json()
            self.token = response_data.get('data', {}).get('accessToken')

            if self.token:
                self.session.headers.update({'Authorization': f'Bearer {self.token}'})
            else:
                print("Error in get_token(): Access token not found in response data")

        except Exception as ex:
            print(f"Error in get_token(): {ex}")

    async def get_graphl(self):
        url = 'https://api.qna3.ai/api/v2/graphql'
        json_data = {
            'query': 'query loadUserDetail($cursored: CursoredRequestInput!) {\n  userDetail {\n    checkInStatus {\n      checkInDays\n      todayCount\n    }\n    credit\n    creditHistories(cursored: $cursored) {\n      cursorInfo {\n        endCursor\n        hasNextPage\n      }\n      items {\n        claimed\n        extra\n        id\n        score\n        signDay\n        signInId\n        txHash\n        typ\n      }\n      total\n    }\n    invitation {\n      code\n      inviteeCount\n      leftCount\n    }\n    origin {\n      email\n      id\n      internalAddress\n      userWalletAddress\n    }\n    externalCredit\n    voteHistoryOfCurrentActivity {\n      created_at\n      query\n    }\n    ambassadorProgram {\n      bonus\n      claimed\n      family {\n        checkedInUsers\n        totalUsers\n      }\n    }\n  }\n}',
            'variables': {
                'headersMapping': {
                    'x-lang': 'english',
                    'Authorization': f'Bearer {self.token}',
                },
                'cursored': {
                    'after': '',
                    'first': 20,
                },
            },
        }
        try:
            response = await self.session.post(url, json=json_data, proxy=self.proxy)
            await asyncio.sleep(3)
            response_data = await response.json()
            checkInStatus = response_data['data']['userDetail']['checkInStatus']
            self.todayCount = checkInStatus['todayCount']
            self.checkInDays = checkInStatus['checkInDays']
        except Exception as ex:
            print(f"Error in get_graphl(): {ex}")

    async def make_transaction(self):
        contract_address = '0xB342e7D33b806544609370271A8D074313B7bc30'
        data = '0xe95a644f0000000000000000000000000000000000000000000000000000000000000001'

        try:
            gas_estimate = await self.account.w3.eth.estimate_gas({
                'to': contract_address,
                'data': data
            })

            transaction = {
                'chainId': 204,
                'to': contract_address,
                'gas': gas_estimate,
                'gasPrice': await self.account.w3.eth.gas_price,
                'nonce': await self.account.w3.eth.get_transaction_count(self.account.address),
                'data': data
            }
            signed_transaction = self.account.w3.eth.account.sign_transaction(transaction, self.account.key)
            transaction_hash = await self.account.w3.eth.send_raw_transaction(signed_transaction.rawTransaction)

            transaction_receipt = await self.account.w3.eth.wait_for_transaction_receipt(transaction_hash, timeout=120)

            if transaction_receipt and transaction_receipt['status'] == 1:
                return transaction_hash.hex()
            else:
                print(
                    f"Transaction failed. Status: {transaction_receipt['status'] if transaction_receipt else 'unknown'}")
        except Exception as ex:
            print(f"Error in make_transaction(): {ex}")

    async def verify_transaction(self):
        try:
            tx_hash = await self.make_transaction()
            url = 'https://api.qna3.ai/api/v2/my/check-in'
            if tx_hash:
                json_data = {"hash": f"{tx_hash}",
                             "via": 'opbnb'}
                response = await self.session.post(url, json=json_data, proxy=self.proxy)

                if response.status == 500:
                    await asyncio.sleep(2)
                    response = await self.session.post(url, json=json_data, proxy=self.proxy)

                return await response.text()

        except Exception as ex:
            print(f"Error in verify_transaction(): {ex}")
            return None

    async def claim_all(self):
        url = 'https://api.qna3.ai/api/v2/my/claim-all'
        try:
            response = await self.session.post(url, proxy=self.proxy)
            response_data = await response.json()
            if response_data['data']:
                signature = response_data.get('data').get('signature').get('signature')
                amount = response_data.get('data').get('amount')
                nonce = response_data.get('data').get('signature').get('nonce')
                return hex(amount)[2:], signature[2:], hex(nonce)[2:]
            else:
                return None

        except Exception as ex:
            print(f"Error in claim_all(): {ex}")

    async def claim_all_tx(self):
        self.account.define_new_provider('https://rpc.ankr.com/bsc', True)
        contract_address = '0xB342e7D33b806544609370271A8D074313B7bc30'
        amount, signature, nonce = await self.claim_all()
        data = (
            f'0x624f82f5{amount:0>64}{nonce:0>64}000000000000000000000000000000000000000000000000000000'
            f'00000000600000000000000000000000000000000000000000000000000000000000000041{signature}0000000000000000'
            f'0000000000000000000000000000000000000000000000')
        # gas = await self.account.w3.eth.estimate_gas(data)

        transaction = {
            'chainId': 56,
            'to': contract_address,
            'gasPrice': self.account.w3.to_wei(1, 'gwei'),
            # тут никак не получается gas_estimate Async
            'gas': 100000,
            'nonce': await self.account.w3.eth.get_transaction_count(self.account.address),
            'data': str(data)
        }
        signed_transaction = self.account.w3.eth.account.sign_transaction(transaction, self.account.key)
        transaction_hash = await self.account.w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
        #
        transaction_receipt = await self.account.w3.eth.wait_for_transaction_receipt(transaction_hash, timeout=120)
        #
        if transaction_receipt and transaction_receipt['status'] == 1:
            return transaction_hash.hex()
        else:
            return None

    async def close_session(self):
        if self.session and not self.session.closed:
            await self.session.close()
