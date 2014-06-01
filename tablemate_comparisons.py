"""
Makes comparisons between our UKvar data and previous studies.

This module has functions that generate the answers to questions 
like "How many of our variables are previously known (a) stars or
(b) variables?",  "How many of our periodic variables are are newly
determined to be periodic?", "How do our periods compare to previously
published periods?".

These functions operate on the output table generated by tablemate_core.py 
and tablemate_script.py.

"""

from __future__ import division
import os

import numpy as np
import matplotlib.pyplot as plt

from tablemate_script import *
from period_digger import period_funcs
from official_star_counter import *
from montage_script import conf_subj_periodics, conf_subj_nonpers


# A. How many of our variables are previously known stars?
# B. How many of our variables are previously known variables?
# C. How many of our periodic variables are new period determinations?
# D. How do our periods compare to previously published periods?

# We want to do a couple things. 
# One: for a given subset of literature tables, see how many matches
#   a given source has; and to count how many sources have zero matches. 
#    (In the case of question A, the "given subset" is
#     ALL of the literature tables, plus SIMBAD. For question B, it's
#     tables that identify variables specifically. For question C, it's 
#     tables that identify periodic variables, but since some tables might
#     mix periodic and nonperiodic variables and so I'll need to also access
#     the "period" column contained therein, which requires Two.)
# Two: for input tables, access given columns in those tables corresponding
#   to an input source.

dropbox_bo_aux_catalogs = os.path.expanduser("~/Dropbox/Bo_Tom/aux_catalogs/")

# This is a table I made and then attached 
mated_ukvar = atpy.Table(dropbox_bo_aux_catalogs+"ukvar_matched_table_withSIMBAD_w1226_minusEasties_w1227_2014_04_07.fits")
ukvar_spread = atpy.Table(dropbox_bo_aux_catalogs+"UKvar_spreadsheet_withSIMBADnames_w1226_minusEasties_renamedOldONCvarColumn_w1227.fits")

def period_array_maker(spread):
    """ 
    Extracts periods from our own data (subjectives, autovars, etc).

    Parameters
    ----------
    spread : atpy.Table
        Table that contains the variables you want.

    Returns
    -------
    spread_periods : np.ndarray
        Array of periods or np.nan for each star.
        Can be glued as a new column to `spread` - it's ordered 
        like that.

    """

    spread_periods = np.zeros((len(spread)))

    for s, i in zip(spread.SOURCEID, range(len(spread))):

        if s in conf_subj_periodics.SOURCEID:
            s_per = conf_subj_periodics.best_period[
                conf_subj_periodics.SOURCEID == s]
        elif s in autovars_true_periods.SOURCEID:
            s_per = autovars_true_periods.best_period[
                autovars_true_periods.SOURCEID == s]
        elif s in autovars_true_periods_s1.SOURCEID:
            s_per = autovars_true_periods_s1.best_period[
                autovars_true_periods_s1.SOURCEID == s]
        elif s in low_periodics.SOURCEID:
            s_per = low_periodics.best_period[
                low_periodics.SOURCEID == s]
        else:
            s_per = np.NaN

        spread_periods[i] = s_per

    return spread_periods

ukvar_periods = period_array_maker(ukvar_spread)


# Builds a dict for the source. 
# the length of the dict corresponds 
# The desired table aliases are possible keys, added only if there's 
# a corresponding value in the columns. Value: Possibly a tuple of (name, index).
# Returns two lists: UKvar ID, above dict. Then you can 
# NO the above is silly. JUST TELL US HOW MANY NON-NULL MATCHES IT HAS AMONG THE GIVEN TABLES.
 



def source_tablematch_counter(table, matches='All'):
    """
    Counts how many times each source has a match.

    Compares the sources in the primary table to the matched tables
    that have already been cross-matched using tablemate_script.

    Parameters
    ----------
    table : atpy.Table
        Output of tablemate_script containing desired sources.
    matches : {list of str | 'All'}, optional
        Which columns of the mated table do we want to scan?
        Default is 'All', i.e. any column that ends in _name, _ID, or _index.
 
    Returns
    -------
    n_matches : np.array
        Array of "how many matches" per source. Amenable to calling 
        histograms upon, or for finding how many sources have 
        'so many' matches, etc.

    """

    # by default, just scan all the eligible rows in table.columns.keys
    if matches == 'All':
        # "eligible" means that the column name is an index or name
        columns_list = [x for x in table.columns.keys if 
                        '_index' in x or '_name' in x]
    else:
        columns_list = matches

    # construct a return array that corresponds to the index of the table
    n_matches = np.zeros(len(table), dtype=int)

    # now start scanning through the rows and columns:
    for i in range(len(table)):

        for column in columns_list:

            # an _index mismatch is -1, a _name mismatch is ''.
            if table[column][i] != -1 and table[column][i] != '':

                n_matches[i] += 1

    return n_matches

def table_tablematch_counter(table):
    """
    Counts how many stars are matched to each input table.

    Parameters
    ----------
    table : atpy.Table
        Output of tablemate_script containing desired sources and columns.

    Returns
    -------
    match_dict : dict
        Mapping of table -> how many sources matched to that table.

    """

    match_dict = {}
    columns_list = [x for x in table.columns.keys if 
                    '_index' in x or '_name' in x]

    for column_name in columns_list:

        if '_name' in column_name:
            n_matches = len(table[column_name][table[column_name] != ''])

        else:
            n_matches = len(table[column_name][table[column_name] != -1])

        table_name = column_name.rstrip('_index').rstrip('_name')

        match_dict[table_name] = n_matches

    return match_dict


def how_many_stars_are_new():
    """
    Figures out how many stars are unknown in any previous catalog.

    Also returns who they are.
    
    """
    pass

# This one might be a special case of source_tablematch_counter!
# where we define the input tables as just those that count variables.

# But that will require scanning all of the tables by eye and seeing
# which ones are tables of variables, or have columns saying "variable?"
def how_many_variables_are_new():
    """
    Figures out how many variables were previously unknown as variables.

    """
    pass
    
def source_period_digger(table):
    """
    Extracts literature periods, if they exist, for every star.

    Returns a new table of UKvars ID, WFCAM sourceid, and periods from
    each of the following: GCVS, Carpenter 2001, YSOVAR, Herbst 2002, 
    and Parihar 2009.

    Parameters
    ----------
    table : atpy.Table
        Output of tablemate_script containing desired sources.
        Must be matched to the above period-containing catalogs.

    Returns
    -------
    period_table : atpy.Table
        Table matching sources to periods from each of the 5 
        input catalogs.

    """

    period_table = atpy.Table()

    gcvs_pers = np.zeros(len(table))
    chs01_pers = np.zeros(len(table))
    ysovar_pers = np.zeros(len(table))
    herbst_pers = np.zeros(len(table))
    parihar_pers = np.zeros(len(table))
    rl09_pers = np.zeros(len(table))
    
    period_columns = [gcvs_pers, chs01_pers, ysovar_pers, 
                      herbst_pers, parihar_pers, rl09_pers]
    
    for i in range(len(table)):
        for period_get, period_col in zip(period_funcs, period_columns):
            per = period_get(table, i)
            period_col[i] = per

    
    # build and return the table
    for j in range(3):
        period_table.add_column(table.columns.keys[j], 
                                table[table.columns.keys[j]])
    period_table.add_column("GCVS_period", gcvs_pers)
    period_table.add_column("CHS01_period", chs01_pers)
    period_table.add_column("YSOVAR_period", ysovar_pers)
    period_table.add_column("Herbst2002_period", herbst_pers)
    period_table.add_column("Parihar2009_period", parihar_pers)
    period_table.add_column("RodriguezLedesma2009_period", rl09_pers)

    return period_table

def how_many_periods_are_new():
    """
    Figures out how many periods are new in our dataset.

    Also counts how many of our variables we missed as periodic.
    Depends on the output of source_period_digger().

    """
    
    period_table = source_period_digger(mated_ukvar)
    pt = period_table
    # so, basically, we're scanning spd for blank rows? and counting them?
    
    # for each star in ukvars, (a) check if we found a period for it,
    # if so, (b) check how many literature periods we have for it.
    # store the results.
    
    n_new = 0
    n_old = 0
    n_missed = 0
    
    for i in range(len(ukvar_spread)):
        
        # did we think it was periodic?
        if not np.isnan(ukvar_periods[i]):
            
            # did anyone else? 
            if (np.isnan(pt.GCVS_period[i]) and 
                np.isnan(pt.CHS01_period[i]) and
                np.isnan(pt.YSOVAR_period[i]) and 
                np.isnan(pt.Herbst2002_period[i]) and
                np.isnan(pt.Parihar2009_period[i]) and 
                np.isnan(pt.RodriguezLedesma2009_period[i])):
                
                n_new += 1

            else:
                n_old += 1

        # If we didn't think it was periodic...
        else:
            
            # did anyone else? 
            if not (np.isnan(pt.GCVS_period[i]) and 
                    np.isnan(pt.CHS01_period[i]) and
                    np.isnan(pt.YSOVAR_period[i]) and 
                    np.isnan(pt.Herbst2002_period[i]) and
                    np.isnan(pt.Parihar2009_period[i]) and 
                    np.isnan(pt.RodriguezLedesma2009_period[i])):
                
                n_missed += 1
            

    print n_new, n_old, n_missed
    print "We found %d unknown periodic stars" % n_new 
    print "%d of our periodic stars are already known to be periodic" % n_old
    print "%d of our non-periodic variables were previously reported periodic" % n_missed

period_table = source_period_digger(mated_ukvar)
pt = period_table

# let's use ukvar_periods and pt

GCVS_period_ratio = ukvar_periods / pt.GCVS_period
CHS01_period_ratio = ukvar_periods / pt.CHS01_period
YSOVAR_period_ratio = ukvar_periods / pt.YSOVAR_period
Herbst2002_period_ratio = ukvar_periods / pt.Herbst2002_period
Parihar2009_period_ratio = ukvar_periods / pt.Parihar2009_period
RL2009_period_ratio = ukvar_periods / pt.RodriguezLedesma2009_period


def how_do_our_periods_compare(pretty_print=True):
    """
    Makes six histograms

    Parameters
    ----------
    pretty_print : bool, optional, default: True
        Print out a pretty, LaTeX-style table?

    """

    fig = plt.figure()
    colors = ['b', 'g', 'r', 'c', 'm', 'y']

    names = ["GCVS", "CHS01", 
             "YSOVAR", "Herbst2002", 
             "Parihar2009", "Rodriguez-Ledesma2009"]

    for ratio, n, c, name in zip([GCVS_period_ratio, CHS01_period_ratio, 
                                  YSOVAR_period_ratio, Herbst2002_period_ratio, 
                                  Parihar2009_period_ratio, 
                                  RL2009_period_ratio], np.arange(6)+1,
                                 colors, names):

        sub = fig.add_subplot(6, 1, n)

        defined_ratio = ratio[~np.isnan(ratio)]

        sub.hist(ratio[~np.isnan(ratio)], range=(0,5), bins=50, color=c, 
                 label=name)
        sub.legend()
        sub.set_xlim(0,5)

        # How many of our periods are within 10% of literature?
        agreement_fraction = (
            len(defined_ratio[np.abs(defined_ratio-1) < .1])/
            len(defined_ratio))

        if pretty_print:
            print "%s & %.2f%% & %d \\\\" % (name, 100*agreement_fraction, 
                                              len(defined_ratio))
        else:
            print agreement_fraction, "of", len(defined_ratio)
        
    plt.xlabel("ratio: 'our period / literature period'")

    plt.show()
    return fig

    
    
            
