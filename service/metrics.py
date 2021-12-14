import time

from prometheus_client import Summary


class MetricsKeeper:
    def __init__(self):
        self.load_metric = Summary('espnet_model_load_seconds', 'The ESPnet model load time', labelnames=["voice"])
        self.calc_metric = Summary('espnet_model_calc_seconds', 'The ESPnet model interference time',
                                   labelnames=["voice"])


class ElapsedLogger(object):
    def __init__(self, logger_func, msg):
        self.logger_func = logger_func
        self.msg = msg

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, *args, **kwargs):
        end = time.time()
        elapsed = (end - self.start)
        self.logger_func(self.msg + f": {elapsed:5f} s")
