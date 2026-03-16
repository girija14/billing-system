def calculate_balance_denominations(
    balance: float, denom_counts: dict
) -> tuple[list[tuple[int, int]], int]:
    """
    Calculate the optimal denomination breakdown for change using a greedy algorithm.

    Args:
        balance: The balance amount to return to the customer.
        denom_counts: Dict of {denomination_value: available_count_in_shop}.

    Returns:
        Tuple of:
          - List of (denomination_value, count_to_give) sorted descending.
          - remaining_amount (should be 0 if exact change is possible).
    """
    balance_int = int(balance)
    result = []
    sorted_values = sorted(denom_counts.keys(), reverse=True)

    for value in sorted_values:
        if balance_int <= 0:
            break
        available = denom_counts[value]
        count_needed = balance_int // value
        count_to_use = min(count_needed, available)
        if count_to_use > 0:
            result.append((value, count_to_use))
            balance_int -= count_to_use * value

    return result, balance_int
