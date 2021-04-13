from time import time
import asyncio

import requests

urls = ['https://search.naver.com/search.naver?query=' + i
        for i in ['비동기', '통신', '스크립트', '속도', '테스트', '중', '화이팅']]


async def fetch(url):
    resp = await loop.run_in_executor(None, requests.get, url)
    return [resp.status_code, url]


async def get_status_code(resp):
    yield resp.status_code


async def main():
    futures = [asyncio.ensure_future(fetch(url)) for url in urls]
    # 태스크(퓨처) 객체를 리스트로 만듦
    result = await asyncio.gather(*futures)  # 결과를 한꺼번에 가져옴
    for r in result:
        if r[0] == 200:
            print(r[1])


begin = time()
loop = asyncio.get_event_loop()  # 이벤트 루프를 얻음
loop.run_until_complete(main())  # main이 끝날 때까지 기다림
loop.close()  # 이벤트 루프를 닫음
end = time()
print('실행 시간: {0:.3f}초'.format(end - begin))
