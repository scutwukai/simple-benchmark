from django.conf.urls import url

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.generic.http import AsyncHttpConsumer

from io import BytesIO
from multipart import parse_options_header, MultipartParser



responses = dict()
class BasicHttpConsumer(AsyncHttpConsumer):
    async def handle(self, body):
        msize = int(self.scope['url_route']['kwargs']['msize'])

        if msize not in responses:
            responses[msize] = b'X' * msize

        await self.send_response(200, responses[msize], headers=[
            ('Content-Type', 'text/plain; charset=utf-8'),
        ])

class FormHttpConsumer(AsyncHttpConsumer):
    async def handle(self, body):
        ctype = dict(self.scope['headers'])[b'content-type']
        _, options = parse_options_header(ctype.decode())

        mp = MultipartParser(BytesIO(body), options['boundary'])

        content = '';
        for part in mp.parts():
            if part.filename:
                content = part.value

        await self.send_response(200, b'%d' % len(content), headers=[
            ('Content-Type', 'text/plain; charset=utf-8'),
        ])


application = ProtocolTypeRouter({
    'http': URLRouter([
        url(r'^(?P<msize>\d+)$', BasicHttpConsumer),
        url(r'^form$', FormHttpConsumer),
    ]),
})
