from django.conf.urls import url

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.generic.http import AsyncHttpConsumer

responses = dict()
class BasicHttpConsumer(AsyncHttpConsumer):
    async def handle(self, body):
        msize = int(self.scope["url_route"]["kwargs"]["msize"])

        if msize not in responses:
            responses[msize] = b'X' * msize

        await self.send_response(200, responses[msize], headers=[
            ("Content-Type", "text/plain; charset=utf-8"),
        ])


application = ProtocolTypeRouter({
    "http": URLRouter([
        url(r"^(?P<msize>\d+)$", BasicHttpConsumer),
    ]),
})
