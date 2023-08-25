import logging

import numpy

logger = logging.getLogger(__name__)


def check_alpha(speed_control_alpha: float, speed_shift: float = 1):
    res = speed_control_alpha
    if res is None:
        res = 1
    if speed_shift is not None:
        res = res * speed_shift
    if res < 0.1 or res > 10:
        logger.warning("Speed alpha %.2f is not in range [.1, 10] - set to 1" % res)
        return 1
    return res


def len_fix_np(array, speed_control_alpha):
    if check_alpha(speed_control_alpha) == 1.0:
        return array
    return numpy.round(array * speed_control_alpha, decimals=0)


def len_fix(number, speed_control_alpha):
    if check_alpha(speed_control_alpha) == 1.0:
        return number
    return int(round(number * speed_control_alpha))
