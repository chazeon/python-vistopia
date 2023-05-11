from typing import List


def range_expand(txt: str) -> List[int]:
    '''Range expansion.

    >>> range_expand('1-3,6,8,10-12')
    [1, 2, 3, 6, 8, 10, 11, 12]

    via: https://rosettacode.org/wiki/Range_expansion
    '''
    lst: List[int] = []
    for r in txt.split(','):
        if '-' in r[1:]:
            r0, r1 = r[1:].split('-', 1)
            lst += range(int(r[0] + r0), int(r1) + 1)
        else:
            lst.append(int(r))
    return lst
