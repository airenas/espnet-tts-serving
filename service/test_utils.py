import numpy

from service.utils import check_alpha, len_fix, len_fix_np, fix_duration


def test_alpha():
    assert check_alpha(None) == 1
    assert check_alpha(0) == 1
    assert check_alpha(0.2) == 0.2
    assert check_alpha(0.999) == 0.999
    assert check_alpha(2) == 2
    assert check_alpha(2, None) == 2
    assert check_alpha(2, 10) == 1
    assert check_alpha(2, 0.5) == 1
    assert check_alpha(1, 1.5) == 1.5


def test_len_fix():
    assert len_fix(10, None) == 10
    assert len_fix(10, 1) == 10
    assert len_fix(10, 0.9) == 9
    assert len_fix(15, 0.6) == 9
    assert len_fix(10, 1.55) == 16
    assert len_fix(10, 1.54) == 15


def test_len_fix_np():
    assert len_fix_np(numpy.array([10]), None).tolist() == [10]
    assert len_fix_np(numpy.array([10]), 1).tolist() == [10]
    assert len_fix_np(numpy.array([10, 9, 11, 20, 4]), 0.9).tolist() == [9, 8, 10, 18, 4]
    assert len_fix_np(numpy.array([10, 9, 11, 20]), 1.55).tolist() == [16, 14, 17, 31]
    assert len_fix_np(numpy.array([10, 9, 11, 20]), 1, 5).tolist() == [15, 9, 11, 15]
    assert len_fix_np(numpy.array([10, 9, 11, 20]), 1, -5).tolist() == [5, 9, 11, 25]
    assert len_fix_np(numpy.array([10, 9, 11, 20]), 0.51, -5).tolist() == [3, 5, 6, 13]
    assert len_fix_np(numpy.array([10, 9, 11, 20]), 0.49, -5).tolist() == [2, 4, 5, 12]


def test_fix_duration():
    assert fix_duration(numpy.array([10, 5, 5, 4]), 0).tolist() == [10, 5, 5, 4]
    assert fix_duration(numpy.array([10, 5, 5, 4]), 1).tolist() == [11, 5, 5, 3]
    assert fix_duration(numpy.array([10, 9, 11, 20, 4]), 10).tolist() == [14, 9, 11, 20, 0]
    assert fix_duration(numpy.array([10, 9, 11, 20]), 10).tolist() == [20, 9, 11, 10]
    assert fix_duration(numpy.array([10, 9, 11, 20]), -10).tolist() == [0, 9, 11, 30]
    assert fix_duration(numpy.array([5, 9, 11, 20]), -10).tolist() == [0, 9, 11, 25]