import asyncio
import aiohttp
import zipfile
import urllib.request as rq
from fake_useragent import UserAgent
from colorama import Fore


ua = UserAgent()


class Settings:
    MAX_THREADS = 1
    TIMEOUT = 10
    TESTING_URL = 'https://ya.ru/'


def load_proxies():
    path = 'Proxy-List-master/http.txt'
    #path = 'socks5_list-master/proxy.txt'
    out = 'proxies.zip'
    url = 'https://github.com/ShiftyTR/Proxy-List/archive/refs/heads/master.zip'
    #url = 'https://github.com/hookzof/socks5_list/archive/refs/heads/master.zip'
    print(Fore.CYAN + "Загрузка прокси: " + Fore.BLUE + url)
    rq.urlretrieve(url, out)

    with zipfile.ZipFile(out) as z:
        z.extract(path)
    print(Fore.CYAN + "Загрузка завершена\n")

    return open(path).readlines()


async def check(num, proxies_q):
    while not proxies_q.empty():
        proxy = await proxies_q.get()
        proxy = proxy.replace("\r", "").replace("\n", "")
        proxy = 'http://' + proxy
        proxy = 'http://5.253.61.235:8888'
        proxies_q.task_done()
        ag = {'Host': 'ya.ru',
              'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0',
              'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
              'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
              'Accept-Encoding': 'gzip, deflate, br',
              'Connection': 'keep-alive',
              'Upgrade-Insecure-Requests': '1',
              'Sec-Fetch-Dest': 'document',
              'Sec-Fetch-Mode': 'navigate',
              'Sec-Fetch-Site': 'None',
              'Sec-Fetch-User': '?1',
              'Cache-Control': 'max-age=0'}

        try:
            async with aiohttp.ClientSession(headers=ag) as session:
                async with session.get(url=Settings.TESTING_URL,
                                        timeout=Settings.TIMEOUT) as response:
                    code = response.status
                    text = await response.text()
                    print(text)
                    print('[' + proxy + '] ' + str(code))
        except asyncio.exceptions.TimeoutError:
            print('[' + proxy + '] Timeout')
        except BaseException as e:
            print(('[' + proxy + '] ' + str(e)))
            #continue
        exit(1)


async def main():
    proxies_q = asyncio.Queue()
    proxies = load_proxies()

    for proxy in proxies:
        await proxies_q.put(proxy.replace("\n", ""))

    tasks = []

    for num in range(Settings.MAX_THREADS):
        task = check(num, proxies_q)
        tasks.append(task)

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
