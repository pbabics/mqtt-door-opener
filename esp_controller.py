import asyncio
import contextlib
import os
import logging

from hbmqtt.client import MQTTClient, ClientException
from hbmqtt.mqtt.constants import QOS_1, QOS_2

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend



class Controller:

  def __init__(self, mqtt_server_address: str) -> None:
    self._logger = logging.getLogger(self.__class__.__name__)

    self._mqtt_server_address = mqtt_server_address
    self._mqtt_client = MQTTClient()

    self._backend = default_backend()
    self._key = os.urandom(16)
    self._iv = os.urandom(16)
    self._cipher = Cipher(
      algorithms.AES(self._key),
      modes.CBC(self._iv),
      backend = self._backend
    )
    self._message_processing = None
  

  async def start(self) -> None:
    self._logger.info('Connecting')
    await self._mqtt_client.connect(self._mqtt_server_address)

    self._logger.info('Subscribing')
    await self._mqtt_client.subscribe([
        ('/door/controller', QOS_2),
    ])
    self._message_processing = asyncio.ensure_future(self._process_message())


  async def stop(self) -> None:
    self._logger.info('Unsubscribing')
    await self._mqtt_client.unsubscribe(['/door/controller'])

    self._logger.info('Disconnecting')
    await self._mqtt_client.disconnect()

    self._logger.info('Stoppig processing loop')
    self._message_processing.cancel()
    with contextlib.suppress(asyncio.CancelledError):
      await self._message_processing


  async def _process_message(self) -> None:
    while True:
      message = await self._mqtt_client.deliver_message()
      self._logger.info('Authenticating')
      await self._mqtt_client.publish('/auth/{:s}'.format(message.data.decode()), self._key + self._iv)


  async def open_door(self) -> None:
    self._logger.info('Openning door')
    encryptor = self._cipher.encryptor()
    ct = encryptor.update(b'open_the_door   ') + encryptor.finalize()
    await self._mqtt_client.publish('/door/handle', ct)
