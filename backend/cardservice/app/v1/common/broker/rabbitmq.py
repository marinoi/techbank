import os

from faststream.rabbit.fastapi import RabbitBroker

DEFAULT_BROKER_URL = os.environ["RABBITMQ_BROKER_URL"]
rabbitmq = RabbitBroker(DEFAULT_BROKER_URL)
