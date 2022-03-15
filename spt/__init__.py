from .cargo import *
from .client import *
from .errors import *
from .flight import *
from .http import *
from .ship import *
from .user import *
from .route import *

# ----------
# Disable aiohttp's warning messages
import logging

asyncio = logging.getLogger("asyncio")
asyncio.disabled = True

# Setup logging for module
with open("spacetraders.log", "w") as f:
    pass

logger = logging.getLogger("spacetraders")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("spacetraders.log")
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter("[%(name)s]  %(levelname)s - %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)

logger = logging.getLogger("spacetraders-http")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("spacetraders.log")
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter("[%(name)s]  %(levelname)s - %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)


# --------------------

try:
    import art

    print(f"\033[1;33m {art.text2art('spt')} \033[0m")

    del art

except ImportError:
    pass
