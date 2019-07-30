#!/usr/bin/env python3

import argparse
import copy
import json
import os


def balance_int(m, n):
    """Return a list L such as sum(L) == m and len(L) == n

    L is sorted in reverse order.

    Example
    -------

    >>> balance_int(3, 2)
    [2, 1]
    >>> balance_int(3, 3)
    [1, 1, 1]
    >>> balance_int(3, 5)
    [1, 1, 1, 0, 0]


    """
    if m == n:
        L = [1] * n
    if m < n:
        L = [1] * m + [0] * (n - m)
    else:
        L = [int(m / n) for _ in range(n-1)]
        L = [m - sum(L)] + L

    assert sum(L) == m
    assert len(L) == n
    assert sorted(L, reverse=True) == L
    return L


def balance_list(L, n):
    """Return a matrix M such as sum(M[:]) == L and len(M) == n

    Example
    -------

    >>> balance_list([1, 2], 2)
    [[1, 1], [0, 1]]
    >>> balance_list([1, 2], 3)
    [[1, 0], [0, 1], [0, 1]]
    >>> balance_list([1, 2], 4)
    [[1, 0], [0, 1], [0, 1]]

    """
    idx = list(range(n))
    M = [[] * n] * len(L)
    for i, l in enumerate(L):
        B = balance_int(l, n)
        M[i] = [B[k] for k in idx]
        idx = [idx[-1]] + idx[:-1]

    assert len(M) == len(L)
    assert all(len(M[i]) == n for i in range(len(L)))
    assert all(sum(M[i]) == L[i] for i in range(len(L)))
    M = [list(a) for a in zip(*M)]
    return [m for m in M if sum(m)]


def unroll_dict(D, head=[]):
    """Convert a nested dict into a pair of lists (nested keys, values)

    Example
    -------

    >>> D = {'a': {'a': 1, 'b': 2}, 'b': {'a': 3, 'b': 4}}
    >>> unroll_dict(D)
    ([['a', 'a'], ['a', 'b'], ['b', 'a'], ['b', 'b']], [1, 2, 3, 4])

    """
    keys, values = [], []
    for k, v in D.items():
        k = head + [k]
        if isinstance(v, dict):
            K, V = unroll_dict(v, head=k)
            keys += K
            values += V
        else:
            keys += [k]
            values += [v]
    return keys, values


def roll_dict(D, K, V):
    """Convert back a pair of lists (nested keys, values) as a nested dict

    Example
    -------

    >>> D = {'a': {'a': 1, 'b': 2}, 'b': {'a': 3, 'b': 4}}
    >>> K, V = unroll_dict(D)
    >>> roll_dict(D, K, V)
    {'a': {'a': 1, 'b': 2}, 'b': {'a': 3, 'b': 4}}

    """
    def _aux(D, K, V, idx):
        if len(K) == 1:
            D[K[0]] = V[idx]
            idx += 1
        else:
            D[K[0]], idx = _aux(D[K[0]], K[1:], V, idx)
        return D, idx

    D = copy.deepcopy(D)
    idx = 0
    for k in K:
        D, idx = _aux(D, k, V, idx)
    return D


def split_dict(D, n):
    """Return a list of `n` dicts [D_1, ... D_n] sharing the values of `D`

    Example
    -------

    >>> D = {'a': {'a': 1, 'b': 2}, 'b': 5}
    >>> split_json.split_dict(D, 2)
    [{'a': {'a': 1, 'b': 1}, 'b': 3}, {'a': {'a': 0, 'b': 1}, 'b': 2}]


    """
    K, V = unroll_dict(D)
    return [roll_dict(D, K, W) for W in balance_list(V, n)]


def main():
    parser = argparse.ArgumentParser(
        'Split a JSON of scenes descriptions into balanced subparts')

    parser.add_argument('json_file', help='the input JSON file to split')
    parser.add_argument('n', type=int, help="the number of splits to generate")
    parser.add_argument('output_dir', help='directory where to write JSONs')
    args = parser.parse_args()

    D = json.load(open(args.json_file, 'r'))
    for i, E in enumerate(split_dict(D, args.n), start=1):
        output_json = os.path.join(args.output_dir, '{}.json'.format(i))
        open(output_json, 'w').write(json.dumps(E, indent=4) + '\n')


if __name__ == '__main__':
    main()
