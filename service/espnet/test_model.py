from service.espnet.model import check_alpha


def test_alpha():
    assert check_alpha(None) is 1
    assert check_alpha(0) is 1
    assert check_alpha(0.2) == 0.2
    assert check_alpha(0.999) == 0.999
    assert check_alpha(2) == 2
    assert check_alpha(2, None) == 2
    assert check_alpha(2, 10) == 1
    assert check_alpha(2, 0.5) == 1
    assert check_alpha(1, 1.5) == 1.5
