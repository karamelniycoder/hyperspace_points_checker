from pyuseragents import random as random_ua
from aiohttp import ClientSession
from loguru import logger
from time import sleep
import asyncio
import sys


class Proxy:
    def __init__(self, proxy_list: list):
        self.free_proxies = {proxy: True for proxy in proxy_list}
        self.lock = asyncio.Lock()


    async def get_free_proxy(self):
        async with self.lock:
            if not self.free_proxies: return None
            while True:
                if list(self.free_proxies.values()).count(True) == 0:
                    await asyncio.sleep(1)
                else:
                    for proxy in self.free_proxies:
                        if self.free_proxies[proxy]:
                            self.free_proxies[proxy] = False
                            return proxy


    async def change_ip(self, proxy: str):
        if len(proxy.split(",")) > 1:
            async with ClientSession() as session:
                while True:
                    r = await session.get(proxy.split(",")[1])
                    if r.status == 200:
                        logger.debug(f'[+] Proxy | Changed ip: {await r.text()}')
                        return True
                    logger.warning(f'[•] Proxy | Change IP error: {await r.text()} | {r.status} {r.reason}')
                    await asyncio.sleep(10)


    def free_proxy(self, proxy: str):
        self.free_proxies[proxy] = True


async def get_points(address: str, account_proxy = None):
    try:
        if not address: return None
        if not account_proxy:
            account_proxy = await proxy_manager.get_free_proxy()
            if account_proxy: await proxy_manager.change_ip(proxy=account_proxy)

        async with ClientSession() as session:
            url = 'https://mainnet-avax.hyperspace.xyz/'

            payload = {
                "operationName": "GetPointsStatForWallet",
                "variables": {
                    "address": address.lower(),
                    "season": "SEASON_TWO"
                },
                "query": "query GetPointsStatForWallet($address: String!, $rankBy: String, $season: String) {\n  getPointsStatForWallet(address: $address, rank_by: $rankBy, season: $season) {\n    points_stat {\n      user_id\n      season\n      trading_points\n      adjusted_trading_points\n      social_points\n      rank\n      user {\n        metadata\n        profile_image\n        user_wallet\n        user_twitter_id\n        user_twitter_handle\n        user_id\n        referring_user_id\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}"
            }
            headers = {
                'User-Agent': random_ua(),
                'Origin': 'https://avax.hyperspace.xyz',
                'Referer': 'https://avax.hyperspace.xyz/',
            }

            r = await session.post(url, json=payload, headers=headers)
            try:
                r_json = await r.json()
                points_stat = r_json['data']['getPointsStatForWallet']['points_stat']
                if points_stat: points = r_json['data']['getPointsStatForWallet']['points_stat'][0]['trading_points']
                else: points = 0
            except Exception as err:
                if 'Cloudflare' in str(err):
                    logger.error(f'{address} | CLOUDFLARE ERROR, SLEEPING 10 SECONDS')
                    await asyncio.sleep(10)
                    return await get_points(address=address, account_proxy=account_proxy)
                logger.error(f'get points error: {err} | {await r.text()}')
                points = 0

            logger.info(f'{address} | {points}')
            return {"address": address, "points": points}

    finally:
        if account_proxy: proxy_manager.free_proxy(proxy=account_proxy)


async def runner(addresses: list):
    results = await asyncio.gather(*[get_points(address=address) for address in addresses])

    while results.count(None) > 0: results.remove(None)

    with open('results.txt', 'a+') as f:
        f.write(str(''.join([f'{r["address"]}:{r["points"]}\n' for r in results])))


if __name__ == "__main__":
    logger.remove()
    logger.add(sys.stderr, format="<white>{time:HH:mm:ss}</white> | <level>{message}</level>")

    with open("addresses.txt") as f: addresses = f.read().splitlines()
    with open("proxies.txt") as f: proxies = f.read().splitlines()

    proxy_manager = Proxy(proxy_list=proxies)

    asyncio.run(runner(addresses=addresses))

    sleep(0.2)
    input(f'\nResults saved in `results.txt`\n > Exit...')
