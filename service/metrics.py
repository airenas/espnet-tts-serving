from prometheus_client import Summary


class MetricsKeeper:
    def __init__(self):
        self.load_metric = Summary('espnet_model_load_seconds', 'The ESPnet model load time', labelnames=["voice"])
        self.calc_metric = Summary('espnet_model_calc_seconds', 'The ESPnet model interference time',
                                   labelnames=["voice"])
