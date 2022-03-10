import asyncio
import aiohttp
import zipfile
import urllib.request as rq
from fake_useragent import UserAgent
from colorama import Fore


ua = UserAgent()


class Settings:
    MAX_THREADS = 15
    TIMEOUT = 5
    TESTING_URL = 'https://tengrinews.kz/news'
    USER = 'im_not_tequila'


def load_proxies():
    out = 'proxies.zip'
    url = 'https://github.com/hookzof/socks5_list/archive/refs/heads/master.zip'
    print(Fore.CYAN + "Загрузка прокси: " + Fore.BLUE + url)
    rq.urlretrieve(url, out)

    with zipfile.ZipFile(out) as z:
        z.extract('socks5_list-master/proxy.txt')
    print(Fore.CYAN + "Загрузка завершена\n")

    return open('socks5_list-master/proxy.txt').readlines()


async def check(num, proxies_q):
    while not proxies_q.empty():
        proxy = await proxies_q.get()
        proxy = proxy.replace("\r", "").replace("\n", "")
        proxy = 'https://' + proxy
        proxies_q.task_done()

        try:
            async with aiohttp.ClientSession(headers={'User-Agent': ua.random}) as session:
                async with session.post(url=Settings.TESTING_URL,
                                        timeout=Settings.TIMEOUT) as response:
                    code = response.status
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
