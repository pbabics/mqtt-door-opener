import aiohttp_jinja2



class WebHandler:

  def __init__(self, controller: 'esp_controller.Controller') -> None:
    self._controller = controller


  @aiohttp_jinja2.template('default.jinja2')
  async def handle_root(self, request) -> None:
    '''
    We have nothing to pass to default template
    '''
    pass


  async def handle_open(self, request) -> None:
    await self._controller.open_door()
    return aiohttp.web.HTTPFound('/')
