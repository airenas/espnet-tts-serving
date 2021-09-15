from service.espnet.model import check_alpha


def test_alpha():
    assert check_alpha(None) is None
    assert check_alpha(0) is None
    assert check_alpha(0.2) == 0.2
    assert check_alpha(0.999) == 0.999
    assert check_alpha(2) == 2
