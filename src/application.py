import aioredis
from tornado import web


class Application(web.Application):
    def __init__(self, handlers=None, default_host=None, transforms=None,
                 **settings):
        super().__init__(handlers, default_host, transforms, **settings)
        self.redis = None

    def init_with_loop(self, loop):
        self.redis = loop.run_until_complete(
            aioredis.create_redis(('localhost', 6379), loop=loop)
        )
