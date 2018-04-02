import logging
import click
import asyncio
import os

import aiohttp.web
import aiohttp_jinja2
import jinja2

import esp_controller
import web_handler


logger = logging.getLogger(__name__)



@click.command()
@click.option('--mqtt-server', required = True, envvar = 'MQTT_SERVER', type = str)
def main(mqtt_server: str) -> None:
  formatter = "[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s"
  logging.basicConfig(level=logging.INFO, format=formatter)
  loop = asyncio.get_event_loop()

  app = aiohttp.web.Application()
  aiohttp_jinja2.setup(
    app,
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates'))
  )

  controller = esp_controller.Controller(mqtt_server)
  request_handler = web_handler.WebHandler(controller)

  app.router.add_get('/', request_handler.handle_root)
  app.router.add_post('/api/v1/open', request_handler.handle_open)
  app.router.add_resource('/api/v1/open', name = 'open-command')

  aiohttp_handler = app.make_handler()
  server = loop.run_until_complete(
    loop.create_server(aiohttp_handler, '0.0.0.0', 8080)
  )

  loop.run_until_complete(controller.start())

  try:
    loop.run_forever()
  except KeyboardInterrupt:
    pass
  except:
    logger.exception('Unhandled exception')
  finally:
    server.close()
    loop.run_until_complete(controller.stop())
    loop.close()



if __name__ == '__main__':
  main()
