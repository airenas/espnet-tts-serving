from prometheus_client import REGISTRY

from service.metrics import MetricsKeeper


def test_metrics():
    metrics = MetricsKeeper()
    metrics.calc_metric.observe(1)
    metrics.load_metric.observe(2)
    assert REGISTRY.get_sample_value("espnet_model_calc_seconds_sum") == 1
    assert REGISTRY.get_sample_value("espnet_model_load_seconds_sum") == 2
