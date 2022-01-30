import numpy as np
from randtest import randtest


def get_steady_state(prices_list, batch_len=25, alpha=0.05):
    smooth_prices = []
    for i in range(0, len(prices_list), batch_len):
        smooth_prices.append(np.mean(prices_list[i:i + batch_len]))

    for i in range(1, len(smooth_prices)):
        result = randtest(smooth_prices[:i], smooth_prices[i:], num_permutations=10000)

        if result.p_value > alpha:
            return list(range(batch_len * i, len(prices_list))), prices_list[batch_len * i:]

    return list(range(len(prices_list))), prices_list
