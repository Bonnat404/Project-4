import logging
import os
from datetime import datetime

# Crée le dossier logs s'il n'existe pas
if not os.path.exists("logs"):
    os.makedirs("logs")

# Configuration : on écrit dans 'logs/security.log'
logging.basicConfig(
    filename='logs/security.log',
    level=logging.INFO,
    format='%(asctime)s - [AUDIT] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def log_event(user, action, details):
    msg = f"USER: {user} | ACTION: {action} | DETAILS: {details}"
    print(msg) # Affiche aussi dans la console
    logging.info(msg)
