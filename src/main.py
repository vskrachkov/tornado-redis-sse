import asyncio
import json
import time

from tornado import (
    web,
    gen,
    iostream
)

from src.application import Application
from src.sse import create_data, create_event

y_ = gen.convert_yielded

html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SSE</title>
</head>
<body>
Event list:
<ul id="events-list">

</ul>

<script>
    var evtSource = new EventSource('/events');
    evtSource.addEventListener("test-event", function(e) {
        var data = JSON.parse(e.data);
        console.log(e);
        var newElement = document.createElement("li");
        console.log(data);
        newElement.innerHTML = "ping at " + data.time + " msg: " + data.message;
        var eventList = document.getElementById('events-list');
        eventList.appendChild(newElement)
    }, false);
</script>

</body>
</html>
"""


class MainHandler(web.RequestHandler):
    def get(self):
        self.write(html)


class EventSource(web.RequestHandler):
    def initialize(self):
        self.set_header('Content-Type', 'text/event-stream')
        self.set_header('Cache-Control', 'no-cache')

    async def publish(self, data, event_name=None, event_id=None):
        try:
            if event_name:
                message = create_event(data, event_name, event_id)
            else:
                message = create_data(data)

            self.write(message)

            await y_(self.flush())
        except iostream.StreamClosedError:
            pass

    async def get(self):
        res = await self.application.redis.subscribe('channel:test')
        ch = res[0]
        while await ch.wait_message():
            try:
                data = await ch.get_json()
                await y_(self.publish(
                    json.dumps(data), 'test-event', time.time()))
            except json.JSONDecodeError:
                pass


if __name__ == "__main__":
    application = Application([
        (r'/', MainHandler),
        (r'/events', EventSource),
    ], debug=True)
    application.listen(8888)
    loop = asyncio.get_event_loop()
    application.init_with_loop(loop)
    loop.run_forever()
