import asyncio
from spt import Client

cli = Client('eb085f34-e8f1-4a5a-93ab-f9c337749dce', verbose = True, max_retries = 5)


async def main():
    await cli.test()
    await cli.test()
    await cli.test()
    await cli.test()
    await cli.test()
    await cli.test()
    await cli.test()

loop = asyncio.get_event_loop().run_until_complete(main())
