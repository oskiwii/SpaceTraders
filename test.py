import asyncio
import pprint
from spt import Client

import logging
logger = logging.getLogger('spacetraders-http')
logger.setLevel(logging.INFO)
fh = logging.StreamHandler()
formatter = logging.Formatter('[%(name)s]  [%(levelname)s]  %(message)s')
fh.setFormatter(formatter)
fh.setLevel(logging.INFO)
logger.addHandler(fh)

cli = Client('eb085f34-e8f1-4a5a-93ab-f9c337749dce', verbose = True, max_retries = 5, timeout = 45)


@cli.event(event_name='on_ready')
async def on_ready():
    logger.info('Client appears ready to start!')




async def main():

    online = await cli.online
    if not online:
        raise Exception('spacetraders is not available')
    
    print((await cli.account).name)

    


    return


cli.start(main)
input('ENTER to exit: ')

