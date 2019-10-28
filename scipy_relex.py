# Some functions from the scipy.signals package to help calculate relative
# extrema. I'm including these functions manually in this file because
# KLayout's python installation doesn't include scipy. The file that these
# functions came from can be found at scipy/signal/_peak_finding.py in the
# repo https://github.com/scipy/scipy. SciPy's copyright notice is below:


# Copyright (c) 2001-2002 Enthought, Inc.  2003-2019, SciPy Developers.
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:

# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


# Revision History:
# 29 Jul 2019   Julian Sanders  Initial Revision. Just copied the relevant
#                               functions from the scipy source code.

import numpy as np
import builtins


xrange = builtins.range

def _boolrelextrema(data, comparator, axis=0, order=1, mode='clip'):
    """
    Calculate the relative extrema of `data`.
    Relative extrema are calculated by finding locations where
    ``comparator(data[n], data[n+1:n+order+1])`` is True.
    Parameters
    ----------
    data : ndarray
        Array in which to find the relative extrema.
    comparator : callable
        Function to use to compare two data points.
        Should take two arrays as arguments.
    axis : int, optional
        Axis over which to select from `data`.  Default is 0.
    order : int, optional
        How many points on each side to use for the comparison
        to consider ``comparator(n,n+x)`` to be True.
    mode : str, optional
        How the edges of the vector are treated.  'wrap' (wrap around) or
        'clip' (treat overflow as the same as the last (or first) element).
        Default 'clip'.  See numpy.take
    Returns
    -------
    extrema : ndarray
        Boolean array of the same shape as `data` that is True at an extrema,
        False otherwise.
    See also
    --------
    argrelmax, argrelmin
    Examples
    --------
    >>> testdata = np.array([1,2,3,2,1])
    >>> _boolrelextrema(testdata, np.greater, axis=0)
    array([False, False,  True, False, False], dtype=bool)
    """
    if((int(order) != order) or (order < 1)):
        raise ValueError('Order must be an int >= 1')

    datalen = data.shape[axis]
    locs = np.arange(0, datalen)

    results = np.ones(data.shape, dtype=bool)
    main = data.take(locs, axis=axis, mode=mode)
    for shift in xrange(1, order + 1):
        plus = data.take(locs + shift, axis=axis, mode=mode)
        minus = data.take(locs - shift, axis=axis, mode=mode)
        results &= comparator(main, plus)
        results &= comparator(main, minus)
        if(~results.any()):
            return results
    return results


def argrelmin(data, axis=0, order=1, mode='clip'):
    """
    Calculate the relative minima of `data`.
    Parameters
    ----------
    data : ndarray
        Array in which to find the relative minima.
    axis : int, optional
        Axis over which to select from `data`.  Default is 0.
    order : int, optional
        How many points on each side to use for the comparison
        to consider ``comparator(n, n+x)`` to be True.
    mode : str, optional
        How the edges of the vector are treated.
        Available options are 'wrap' (wrap around) or 'clip' (treat overflow
        as the same as the last (or first) element).
        Default 'clip'. See numpy.take
    Returns
    -------
    extrema : tuple of ndarrays
        Indices of the minima in arrays of integers.  ``extrema[k]`` is
        the array of indices of axis `k` of `data`.  Note that the
        return value is a tuple even when `data` is one-dimensional.
    See Also
    --------
    argrelextrema, argrelmax, find_peaks
    Notes
    -----
    This function uses `argrelextrema` with np.less as comparator. Therefore it
    requires a strict inequality on both sides of a value to consider it a
    minimum. This means flat minima (more than one sample wide) are not detected.
    In case of one-dimensional `data` `find_peaks` can be used to detect all
    local minima, including flat ones, by calling it with negated `data`.
    .. versionadded:: 0.11.0
    Examples
    --------
    >>> from scipy.signal import argrelmin
    >>> x = np.array([2, 1, 2, 3, 2, 0, 1, 0])
    >>> argrelmin(x)
    (array([1, 5]),)
    >>> y = np.array([[1, 2, 1, 2],
    ...               [2, 2, 0, 0],
    ...               [5, 3, 4, 4]])
    ...
    >>> argrelmin(y, axis=1)
    (array([0, 2]), array([2, 1]))
    """
    return argrelextrema(data, np.less, axis, order, mode)


def argrelmax(data, axis=0, order=1, mode='clip'):
    """
    Calculate the relative maxima of `data`.
    Parameters
    ----------
    data : ndarray
        Array in which to find the relative maxima.
    axis : int, optional
        Axis over which to select from `data`.  Default is 0.
    order : int, optional
        How many points on each side to use for the comparison
        to consider ``comparator(n, n+x)`` to be True.
    mode : str, optional
        How the edges of the vector are treated.
        Available options are 'wrap' (wrap around) or 'clip' (treat overflow
        as the same as the last (or first) element).
        Default 'clip'.  See `numpy.take`.
    Returns
    -------
    extrema : tuple of ndarrays
        Indices of the maxima in arrays of integers.  ``extrema[k]`` is
        the array of indices of axis `k` of `data`.  Note that the
        return value is a tuple even when `data` is one-dimensional.
    See Also
    --------
    argrelextrema, argrelmin, find_peaks
    Notes
    -----
    This function uses `argrelextrema` with np.greater as comparator. Therefore
    it  requires a strict inequality on both sides of a value to consider it a
    maximum. This means flat maxima (more than one sample wide) are not detected.
    In case of one-dimensional `data` `find_peaks` can be used to detect all
    local maxima, including flat ones.
    .. versionadded:: 0.11.0
    Examples
    --------
    >>> from scipy.signal import argrelmax
    >>> x = np.array([2, 1, 2, 3, 2, 0, 1, 0])
    >>> argrelmax(x)
    (array([3, 6]),)
    >>> y = np.array([[1, 2, 1, 2],
    ...               [2, 2, 0, 0],
    ...               [5, 3, 4, 4]])
    ...
    >>> argrelmax(y, axis=1)
    (array([0]), array([1]))
    """
    return argrelextrema(data, np.greater, axis, order, mode)


def argrelextrema(data, comparator, axis=0, order=1, mode='clip'):
    """
    Calculate the relative extrema of `data`.
    Parameters
    ----------
    data : ndarray
        Array in which to find the relative extrema.
    comparator : callable
        Function to use to compare two data points.
        Should take two arrays as arguments.
    axis : int, optional
        Axis over which to select from `data`.  Default is 0.
    order : int, optional
        How many points on each side to use for the comparison
        to consider ``comparator(n, n+x)`` to be True.
    mode : str, optional
        How the edges of the vector are treated.  'wrap' (wrap around) or
        'clip' (treat overflow as the same as the last (or first) element).
        Default is 'clip'.  See `numpy.take`.
    Returns
    -------
    extrema : tuple of ndarrays
        Indices of the maxima in arrays of integers.  ``extrema[k]`` is
        the array of indices of axis `k` of `data`.  Note that the
        return value is a tuple even when `data` is one-dimensional.
    See Also
    --------
    argrelmin, argrelmax
    Notes
    -----
    .. versionadded:: 0.11.0
    Examples
    --------
    >>> from scipy.signal import argrelextrema
    >>> x = np.array([2, 1, 2, 3, 2, 0, 1, 0])
    >>> argrelextrema(x, np.greater)
    (array([3, 6]),)
    >>> y = np.array([[1, 2, 1, 2],
    ...               [2, 2, 0, 0],
    ...               [5, 3, 4, 4]])
    ...
    >>> argrelextrema(y, np.less, axis=1)
    (array([0, 2]), array([2, 1]))
    """
    results = _boolrelextrema(data, comparator,
                              axis, order, mode)
    return np.nonzero(results)
