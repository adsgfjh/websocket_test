import asyncio
import websockets
import threading
import functools
from time import sleep

#  This timer is a minimal simulation of the quote callback in sinopac api
#  The real situation follows: https://sinotrade.github.io/tutor/market_data/streaming/#quote-callback
#  BTW, Im not 100% sure this manifests the real situation but I think the logic and workflow are the same
class Timer:
    """ Daemon timer. Call the callback func at some time interval """

    def __init__(self, interval, max_iter=10):
        self.interval = interval
        self.max_iter = max_iter
        self.callback = None
        self.stop_event, self.timer_thread = None, None

    def set_callback(self, callback):
        """ Expect a callback func with one string arg """
        self.callback = callback

    def start(self):
        # start the timer daemon
        self.stop_event = threading.Event()
        self.timer_thread = threading.Thread(target=self._timer_loop,
                                             args=(self.stop_event,),
                                             daemon=True)
        self.timer_thread.start()

    def stop(self):
        self.stop_event.set()

    def _timer_loop(self, stop_event):
        # update first next_time
        i = 0
        while not stop_event.is_set():
            i += 1
            # callback
            msg = f'from timer: {i}'
            self.callback(msg)
            # end loop
            if i > self.max_iter:
                break
            # pause
            sleep(self.interval)


class App:
    """ Websocket server """

    # this is the part I am struggling with
    # In this app, a timer is started and the callback func should be set as well,
    # AND the expected behavior is that when the timer call the provided callback func,
    # the msg is also sent from the websocket server to the user end

    def __init__(self):
        self.callback = None
        self.timer = Timer(1)
        self.ws = None

    def _cb(self):
        def callback(msg):
            self.handler(self.ws, '', msg)
        return callback

    def start_server(self):
        bound_handler = functools.partial(self.handler, msg='')
        self.ws = websockets.serve(bound_handler, 'localhost', 5494)
        # set timer callback
        self.timer.set_callback(self._cb())

        asyncio.get_event_loop().run_until_complete(
            app.ws
        )
        # asyncio.get_event_loop().run_forever()

    def start_timer(self):
        self.timer.start()

    def stop_timer(self):
        self.timer.stop()

    async def handler(self, websocket, path, msg):
        await websocket.send(msg)


if __name__ == "__main__":

    app = App()
    app.start_server()
    print('start timer')
    app.start_timer()
    sleep(30)
    print('end timer')
    app.stop_timer()
