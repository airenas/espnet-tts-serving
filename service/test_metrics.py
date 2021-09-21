from prometheus_client import REGISTRY

from service.metrics import MetricsKeeper


def test_metrics():
    metrics = MetricsKeeper()
    metrics.calc_metric.labels("test").observe(1)
    metrics.load_metric.labels("test").observe(2)
    assert REGISTRY.get_sample_value("espnet_model_calc_seconds_sum", labels={"voice": "test"}) == 1
    assert REGISTRY.get_sample_value("espnet_model_load_seconds_sum", labels={"voice": "test"}) == 2
