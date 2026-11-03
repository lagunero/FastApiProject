import logging

from fastapi import APIRouter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', filename='app.log', filemode='a')
router = APIRouter()
logger = logging.getLogger(__name__)