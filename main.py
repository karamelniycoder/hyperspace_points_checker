from pyuseragents import random as random_ua
from aiohttp import ClientSession
from loguru import logger
from time import sleep
import asyncio
import sys



async def get_points(address: str):
    if not address: return None

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
                return await get_points(address=address)
            logger.error(f'get points error: {err} | {await r.text()}')
            points = 0

        logger.info(f'{address} | {points}')
        return {"address": address, "points": points}


async def runner(addresses: list):
    results = await asyncio.gather(*[get_points(address=address) for address in addresses])

    while results.count(None) > 0: results.remove(None)

    with open('results.txt', 'a+') as f:
        f.write(str(''.join([f'{r["address"]}:{r["points"]}\n' for r in results])))


if __name__ == "__main__":
    with open("addresses.txt") as f: addresses = f.read().splitlines()

    logger.remove()
    logger.add(sys.stderr, format="<white>{time:HH:mm:ss:SSS}</white> | <level>{level: <8}</level> | <level>{message}</level>")

    asyncio.run(runner(addresses=addresses))

    sleep(0.2)
    input(f'\n\n > Exit...')
