"""
This is a module that contains software to 'cleanse' bad nights
from a UKIRT time-series dataset. 

It currently relies on the output of 
"variability_map.count_constants_calc_ratio()" and is meant to create 
tables that can feed into anything that uses helpers3.py
(such as plot3, spread3, etc.).

Preferred function: null_cleanser_grader().

3 things in here:
1. Cleansing: refers to removing low-grade datapoints, using constant stars to measure "grade".
2. Scrubbing: refers to removing flagged data in stars whose data are predominantly *un*flagged. Uses the PPerrbits as "error flags".
3. Dusting: refers to removing points with very large error bars from the dataset. 

"""

from __future__ import division

import numpy as np

from helpers3 import data_cut, band_cut


def null_cleanser( data, nights, j_ratio, h_ratio, k_ratio, threshold=0.9,
                   null=np.double(-9.99999488e+08)):
    """
    Cleans data by nullifying.
    
    For any night with a quality lower than `threshold` in a given band,
    this function replaces all photometry in that band with `null`.

    Parameters
    ----------
    data : atpy.Table
        Table that contains all the photometry data.
    nights : np.ndarray
        Array of nights that have data.
    j_ratio, h_ratio, k_ratio : np.ndarray
        Quality ratios (0.0 - 1.0) for each night at J, H, and K bands.
    threshold : float, optional
        Data below this threshold are cleansed by nullification.
    null : float, optional
        What value to use as a 'null' when cleansing data.
        Default value -9.99999e+08 (as used by WSA).


    Returns
    -------
    cleansed_data : atpy.Table
        Table with bad data nullified and ready to go.

    """
    
    # Make a copy of the data table
    cleansed_data = data.where(data.SOURCEID != 0)

    rdict =  {'j':j_ratio, 'h':h_ratio, 'k':k_ratio}

    for band in ['j', 'h', 'k']:

        col = band.upper()+"APERMAG3"

        for i in range(len(nights)):
       
            if rdict[band][i] < threshold:
                
                # print len(cleansed_data.data[col][ 
                #     np.trunc(cleansed_data.MEANMJDOBS) == nights[i] ])

                # print np.max(cleansed_data.data[col][ 
                #     np.trunc(cleansed_data.MEANMJDOBS) == nights[i] ])
                cleansed_data.data[col][ 
                    np.trunc(cleansed_data.MEANMJDOBS) == nights[i] ] = null

                # print np.max(cleansed_data.data[col][ 
                #     np.trunc(cleansed_data.MEANMJDOBS) == nights[i] ])

                # return
                
                print( "nullified night %d %s band (quality: %.2f)" % 
                       (nights[i], band.upper(), rdict[band][i]) )

    return cleansed_data


def flag_cleanser( data, nights, j_ratio, h_ratio, k_ratio, threshold=0.9 ):
    """
    Cleans data by flagging. Not yet implemented.

    Probably not ever going to be implemented.
    
    """
    pass


def null_cleanser_grader(data, timestamps, j_ratio, h_ratio, k_ratio, 
                         threshold=0.9, null=np.double(-9.99999488e+08)):
    """
    Cleans data by nullifying, and appends quality grades onto data.
    
    For any exposure with a quality lower than `threshold` in a given band,
    this function replaces all photometry in that band with `null`.
    Also, the data is given three new columns: 
    "JGRADE", "HGRADE", and "KGRADE", which  describe a 
    given night's quality at these bands.

    Operates on individual exposure timestamps rather than nights, 
    so this function relies on the output of 
    "variability_map.exposure_grader()"

    Parameters
    ----------
    data : atpy.Table
        Table that contains all the photometry data.
    timestamps : np.ndarray
        Array of timestamps corresponding to exposure times.
    j_ratio, h_ratio, k_ratio : np.ndarray
        Quality ratios (0.0 - 1.0) for each night at J, H, and K bands.
    threshold : float, optional
        Data below this threshold are cleansed by nullification.
    null : float, optional
        What value to use as a 'null' when cleansing data.
        Default value -9.99999e+08 (as used by WSA).


    Returns
    -------
    cleansed_data : atpy.Table
        Table with bad data nullified and all data "graded"
        using new columns JGRADE, HGRADE, KGRADE.

    """
    
    # Make a copy of the data table
    cleansed_data = data.where(data.SOURCEID != 0)

    # Add columns to it!
    jgrade = -1. * np.ones_like(cleansed_data.JAPERMAG3)
    hgrade = -1. * np.ones_like(jgrade)
    kgrade = -1. * np.ones_like(jgrade)

    cleansed_data.add_column("JGRADE", jgrade)
    cleansed_data.add_column("HGRADE", hgrade)
    cleansed_data.add_column("KGRADE", kgrade)

    rdict =  {'j':j_ratio, 'h':h_ratio, 'k':k_ratio}

    for band in ['j', 'h', 'k']:

        col = band.upper()+"APERMAG3"
        grade = band.upper()+"GRADE"

        for i in range(len(timestamps)):

            # first, assign tonight's grade to all the data here
            
            cleansed_data.data[grade][
                cleansed_data.MEANMJDOBS == timestamps[i]] = rdict[band][i]

            if rdict[band][i] < threshold:

                # print len(cleansed_data.data[col][ 
                #     (cleansed_data.MEANMJDOBS) == timestamps[i] ])

                # print np.max(cleansed_data.data[col][ 
                #     (cleansed_data.MEANMJDOBS) == timestamps[i] ])
                cleansed_data.data[col][ 
                    cleansed_data.MEANMJDOBS == timestamps[i] ] = null

                # print np.max(cleansed_data.data[col][ 
                #     (cleansed_data.MEANMJDOBS) == timestamps[i] ])

                # return

                print( "nullified timestamp %f %s band (quality: %.2f)" % 
                       (timestamps[i], band.upper(), rdict[band][i]) )

    return cleansed_data


def selective_flag_scrubber(data, lookup, threshold=0.1, 
                             null=np.double(-9.99999488e+08)):
    """ 
    Scrubs error-flagged points from data of normally-unflagged stars.

    Replaces error-flagged data with `null`, only in stars where the 
    ratio of flagged data to all data is below `threshold`.

    Improves speed by avoiding having to loop over all stars.
    
    If a star has proportionally more flagged data than `threshold`, 
    its data is left intact. The purpose of this is to purify lightcurves
    that are polluted by just a couple of bad points.

    Parameters
    ----------
    data : atpy.Table
        Table that contains all the photometry data.
    lookup : atpy.Table
        A statistics spreadsheet (produced by spread3.py) that
        contains only stars you want to clean up, as well
        as columns for N_j_noflags, N_j_info, etc. (for all 3 bands).
    threshold : float, optional
        Upper limit on how much flagged data to remove.
        If a star has more flagged data than this, its data are 
        left untouched.
        Default: 0.1
    null : float, optional
        What value to use as a 'null' when cleansing data.
        Default value -9.99999e+08 (as used by WSA).

    Returns
    -------
    scrubbed_data : atpy.Table
        Table with selected flagged data scrubbed.

    Notes
    -----
    Formerly known as selective_flag_scrubber2().
        
    """


    # Make a copy of the data table
    scrubbed_data = data.where(data.SOURCEID != 0)

    # Calculate flag ratio arrays

    jflag_ratio = (lookup.N_j_info)/(lookup.N_j_noflag + lookup.N_j_info)
    hflag_ratio = (lookup.N_h_info)/(lookup.N_h_noflag + lookup.N_h_info)
    kflag_ratio = (lookup.N_k_info)/(lookup.N_k_noflag + lookup.N_k_info)

    rdict =  {'j':jflag_ratio, 'h':hflag_ratio, 'k':kflag_ratio}

    for band in ['j', 'h', 'k']:

        col = band.upper()+"APERMAG3"
        pperrbits = band.upper()+"PPERRBITS"

        qualified_sources = lookup.SOURCEID[ (rdict[band] < threshold) & 
                                             (rdict[band] > 0)]

        scrubbed_data.data[col][
            (scrubbed_data.data[pperrbits] > 0) & 
            np.in1d(scrubbed_data.SOURCEID, qualified_sources)] = null

        print "scrubbed %d sources at %s band" % (len(qualified_sources), 
                                                  band.upper())

    return scrubbed_data


def errorbar_duster(data, threshold=0.5, null=np.double(-9.99999488e+08)):
    """
    Removes datapoints with very bad errorbars; replaces them with `null`.
    
    A really simple function.

    Parameters
    ----------
    data : atpy.Table
        Table that contains all the photometry data.
    threshold : float, optional
        Data with error values above this threshold are dusted 
        and replaced with `null`.
    null : float, optional
        What value to use as a 'null' when dusting data.
        Default value -9.99999e+08 (as used by WSA).

    Returns
    -------
    dusted_data : atpy.Table
        Table with large-errorbar data dusted.

    """

    # Make a copy of the data table
    dusted_data = data.where(data.SOURCEID != 0)

    # Do some dusting
    dusted_data.JAPERMAG3[dusted_data.JAPERMAG3ERR > threshold] = null
    dusted_data.HAPERMAG3[dusted_data.HAPERMAG3ERR > threshold] = null
    dusted_data.KAPERMAG3[dusted_data.KAPERMAG3ERR > threshold] = null
    
    return dusted_data
