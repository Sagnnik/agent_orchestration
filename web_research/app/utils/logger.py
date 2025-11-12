import sys
from loguru import logger

logger.remove()
logger.add(
    sys.stdout, 
    format="{time:MMMM D, YYYY - HH:mm:ss} | {level} | <level>{message}</level>",
    level='INFO'
)