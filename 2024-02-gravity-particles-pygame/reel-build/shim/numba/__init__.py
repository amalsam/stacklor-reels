# Offline stand-in for numba: PyPI is blocked here, so njit just returns the plain Python function.
def njit(*a, **k):
    if a and callable(a[0]): return a[0]
    return lambda f: f
