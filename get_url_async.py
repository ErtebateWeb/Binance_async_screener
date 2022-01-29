import asyncio
import sys
import platform
import aiohttp
from urls import websites

urls = websites.split("\n")
num_urls = len(urls)
# print(urls)
# print(type(urls))

URLS = [
	# Insert several URLs here, e.g.:
	"https://www.python.org/ftp/python/",
	"https://github.com/python/",
	"https://www.cpan.org/src/5.0/",
	"https://aiohttp.readthedocs.io/",
	"https://example.com/",
]
# print(URLS)
# print(type(URLS))


async def main():
	async with aiohttp.ClientSession() as session:
		await asyncio.wait([fetch(session, url) for url in urls])
	print("Done.")

async def fetch(session: aiohttp.ClientSession, url: str):
	async with session.get(url):
		print(f"Requested: {url}")

if __name__ == '__main__':
	if platform.system() == 'Windows':
		asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
	# if sys.version_info[:2] == (3, 7):
	# 	asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
	loop = asyncio.get_event_loop()
	try:
		loop.run_until_complete(main())
		loop.run_until_complete(asyncio.sleep(2.0))
	finally:
		loop.close()