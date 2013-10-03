"""
An easy file for selecting periodic variables, given a fully-computed
spreadsheet generated by spread3.

Parameters chosen by human experience with lightcurves.

For the record:
A periodogram power of 12 corresponds to a false-alarm probability
(FAP) of 0.0041 (less than half a percent), while a power of 15 corresponds
to a FAP of 0.0002 (0.02%).
"""

import numpy as np


def periodic_selector( spread ):
    """
    Selects real periodic variables using periodogram parameters.

    Currently only uses Lomb-Scargle input data. Soon to be fixed.

    Parameters
    ----------
    spread : atpy.Table
        Table of spreadsheet info on variable stars.

    Returns
    -------
    periodic_spread : atpy.Table
        Subset of `spread` with only "real" periodics.
    
    """

    s = spread

    r = s.where(
        ( # J, H
            (s.j_lsp_per < s.h_lsp_per * 1.05) &
            (s.j_lsp_per > s.h_lsp_per * 0.95) &
            (s.j_lsp_per < 50) &
            (s.j_lsp_pow > 12) & (s.h_lsp_pow > 12) 
            ) |
        ( # H, K
            (s.h_lsp_per < s.k_lsp_per * 1.05) &
            (s.h_lsp_per > s.k_lsp_per * 0.95) &
            (s.h_lsp_per < 50) &
            (s.h_lsp_pow > 12) & (s.k_lsp_pow > 12) 
            ) |
        ( # J, K
            (s.j_lsp_per < s.k_lsp_per * 1.05) &
            (s.j_lsp_per > s.k_lsp_per * 0.95) &
            (s.j_lsp_per < 50) &
            (s.j_lsp_pow > 12) & (s.k_lsp_pow > 12) 
            ) |
        ( #J
            (s.j_lsp_pow > 15) & (s.j_lsp_per < 50) 
            ) |
        ( #H
            (s.h_lsp_pow > 15) & (s.h_lsp_per < 50) 
            ) |
        ( #K
            (s.k_lsp_pow > 15) & (s.k_lsp_per < 50) 
            ) 
        )
    
    periodic_spread = r
    return periodic_spread

            
def best_period( periodic_spread ):
    """ 
    A function that chooses the best period of the six returned.

    Currently operates only on LSP input, just like periodic_selector.

    Parameters
    ----------
    periodic_spread : atpy.Table
        Table containing periodic variables

    Returns
    -------
    periodic_spread_updated : atpy.Table
        Input table with new "best_period" column added.

    """

    best_period = -1.*np.ones_like( periodic_spread.j_lsp_per )

    r = periodic_spread

    for i in range(len(periodic_spread)):
        # J, H
        if ((r.j_lsp_per[i] < r.h_lsp_per[i] * 1.05) and
            (r.j_lsp_per[i] > r.h_lsp_per[i] * 0.95) and
            (r.j_lsp_per[i] < 50) and
            (r.j_lsp_pow[i] > 12) and (r.h_lsp_pow[i] > 12)
            ):
            best_period[i] = r.h_lsp_per[i]
        # H, K
        elif ((r.h_lsp_per[i] < r.k_lsp_per[i] * 1.05) and
              (r.h_lsp_per[i] > r.k_lsp_per[i] * 0.95) and
              (r.h_lsp_per[i] < 50) and
              (r.h_lsp_pow[i] > 12) and (r.k_lsp_pow[i] > 12)
              ):
            best_period[i] = r.h_lsp_per[i]
        # J, K
        elif ((r.j_lsp_per[i] < r.k_lsp_per[i] * 1.05) and
              (r.j_lsp_per[i] > r.k_lsp_per[i] * 0.95) and
              (r.j_lsp_per[i] < 50) and
              (r.j_lsp_pow[i] > 12) and (r.k_lsp_pow[i] > 12)
              ):
            best_period[i] = r.k_lsp_per[i]
        # J
        elif (r.j_lsp_pow[i] > 15) and (r.j_lsp_per[i] < 50):
            best_period[i] = r.j_lsp_per[i]
        # H
        elif (r.h_lsp_pow[i] > 15) and (r.h_lsp_per[i] < 50):
            best_period[i] = r.h_lsp_per[i]
        # K
        elif (r.k_lsp_pow[i] > 15) and (r.k_lsp_per[i] < 50):
            best_period[i] = r.k_lsp_per[i]
        else:
            print "SOMETHING IS FISHY HERE"

    r.add_column("best_period", best_period)

    periodic_spread_updated = r
    return r