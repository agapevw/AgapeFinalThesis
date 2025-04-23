"""
May 9, 2023
Author: Mary Upshall

This script reads in the DLC h5 files, thresholds by a given likelihood, then splines and interpolates as specified.
There is also the option to overlay the splined values onto the raw video. See comments below.
"""

import glob
import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cv2
import ntpath

from scipy.signal.windows import gaussian
from scipy.ndimage import filters
from scipy.interpolate import PchipInterpolator


def slice_data(data):
    """
    Slices out all x data, all y data, and likelihood data from dlc h5 files.

    :param data: data to be sliced
    :return: x data, y data, & likelihood data
    """
    x_sliced = np.array(data.loc[:, (slice(None), slice(None), ('x'))])
    y_sliced = np.array(data.loc[:, (slice(None), slice(None), ('y'))])
    likelihood_sliced = np.array(data.loc[:, (slice(None), slice(None), ('likelihood'))])

    return x_sliced, y_sliced, likelihood_sliced


def get_file_name(file_path):
    """ Get's the file name in question without the entire base path. Useful for naming graphs.

    :param path: base path (ie. to trial folder).
    :param datafiles_list: list of datafiles (either data or pause).
    :param which_video: which video in the list to read.
    :return: file name without entire base path.
    """
    ntpath.basename(file_path)  # ntpath module (equivalent to os.path) works for all paths on all platforms.
    head, tail = ntpath.split(file_path)  # splits the file name from the base path

    return tail


def splinefish(x, y, numpts):
    """
    Estimates distance between points and gets x and y values.

    :param x: x data
    :param y: y data
    :param numpts: number of points to be splined
    :return: xs = x-splined; ys = y-splined
    """

    pts = list(zip(x, y))  # zip x and y

    distance = np.cumsum(np.sqrt(np.sum(np.diff(pts, axis=0) ** 2, axis=1)))
    distance = np.insert(distance, 0, 0) / distance[-1]  # Estimate distance between points

    spline_x = PchipInterpolator(distance, x)  # spline for each dimension
    spline_y = PchipInterpolator(distance, y)

    # Create new values
    disto = np.linspace(0, 1, numpts, endpoint=True)
    xs = spline_x(disto)
    ys = spline_y(disto)

    return xs, ys


def do_spline(spline_length, data_x, data_y, plot=False):
    """
    Applies the spline to the x and y data

    :param spline_length: # of points on the spline
    :param data_x: x data reordered
    :param data_y: y data reordered
    :param plot: plot default to false, but if true will plot x,y splined
    :return:
    """

    x_splined = np.zeros((data_x.shape[0], spline_length))  # x splined holder matrix
    y_splined = np.zeros((data_y.shape[0], spline_length))  # y splined holder matrix

    if plot:
        plt.figure()

    for ix in range(len(data_x[:, 0])):
        xs, ys = splinefish(data_x[ix, :], data_y[ix, :], spline_length)

        x_splined[ix, :] = xs
        y_splined[ix, :] = ys

        if plot:
            plt.plot(x_splined[ix], y_splined[ix])

    return x_splined, y_splined


def convolve_smooth(data, length, width):
    ff = gaussian(length, width)
    return filters.convolve1d(data, ff / ff.sum())


def interp_label_error(x, y, likelihood, interp_lim, min_likelihood):

    # threshold likely
    min_likelihood = min_likelihood
    likelihood[likelihood < min_likelihood] = 0

    # check xy values with likely
    ncols = x.shape[1]
    for i in range(1, x.shape[0]):
        if (len(np.nonzero(likelihood[i, :])) < len(likelihood[i, :])):  # check for zeros
            for j in range(ncols):
                if likelihood[i, j] == 0:
                    x[i, j] = 'NaN'  # fill with nans
                    y[i, j] = 'NaN'

    df_x = pd.DataFrame(x)
    df_y = pd.DataFrame(y)

    df_x_int = df_x.interpolate(limit=interp_lim)  # interpolate based on set interpolation limit
    df_y_int = df_y.interpolate(limit=interp_lim)

    x = np.array(df_x_int)
    y = np.array(df_y_int)

    # 3pt smooth in time Jeffrey Changing 10 to 5, 3 to 10. 4,3 seems to work alright. KEEP AT 8, 3 unless fish is too wiggly (4,3)
    for j in range(x.shape[1]):
        x[:, j] = convolve_smooth(x[:, j], 2, 3)
        y[:, j] = convolve_smooth(y[:, j], 2, 3)

    return x, y


def labelvideo_fishcoordinates(input_video, splineX, splineY, output_video):
    """
    Overlays raw video with spline labels (from DLC).

    :param input_video: video to label.
    :param splineX: splined X data (can also be reordered x data).
    :param splineY: splined Y data (can also be reordered y data).
    :param output_video: output video file name.
    :return:
    """

    clip = cv2.VideoCapture(input_video)
    frame_width = int(clip.get(3))
    frame_height = int(clip.get(4))
    out = cv2.VideoWriter(output_video, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 30, (frame_width, frame_height))
    i = 0
    while (True):
        ret, frame = clip.read()
        if ret == True:
            # plot spline
            xs = splineX[i, :]
            ys = splineY[i, :]
            pts = np.array([xs.astype(int), ys.astype(int)])
            frame = cv2.polylines(frame, [pts.T], False, (0, 155, 0))  # 0,255,255
            i = i + 1
            out.write(frame)

        # Break the loop
        else:
            break

    clip.release()
    out.release()
    cv2.destroyAllWindows()


# PARAMETERS THAT CAN BE PLAYED WITH
main_path = '/Volumes/Salamander/SalKine 2023/2 Working Videos/DLC output/2024-11-20/'  # set to path where the trial folders live

min_likelihood = 0.5  # minimum likelihood to threshold your data at
interp_lim =1000  # interpolation limit in fps
#

list_of_folders = os.listdir(main_path)  # this will find all files and folders in the specified main path.
# This is best if the only folders in the directory are pertaining to this analysis.

for folder in list_of_folders:
    try:
        list_of_h5s = glob.glob(main_path + folder +'/*.h5')

        for h5 in list_of_h5s:
            file_name_full = get_file_name(h5)
            file_name = file_name_full.split("DLC")[0]  # get rid of DLC crap in file name to get base file name
            print(file_name)

            data = pd.read_hdf(h5)

            x, y, likelihood = slice_data(data)

            plot = False  # change to True if you want to plot the likelihoods for each point in the given video
            if plot:
                plt.plot(likelihood)  # check likelihood cut-offs

            x, y = interp_label_error(x, y, likelihood, interp_lim, min_likelihood)  # run interpolation function

            x, y = do_spline(101, x, y, False)  # splining x, y

            check_vid = True  # set to "True" if you want to check the spline on the video.
            # The video must be in the same folder with the same file name for this to work.
            # Warning: It will take much more computing time than just getting the spline values.
            if check_vid:
                px_calibration = 1  # 1 means no pixel calibration
                # Labels spline values over DLC labelled video, if correct then should perfectly overlap.
                x_check = x * px_calibration
                y_check = y * px_calibration
                file_extension = 'avi'
                new_vid_name = 'check_video'
                labelvideo_fishcoordinates(main_path + folder + '/' + file_name + '.' + file_extension, x_check,
                                           y_check,
                                           main_path + folder + '/' + file_name + '_' + new_vid_name + '.' + file_extension)

            # hold_xy = np.zeros((np.shape(x)[0], np.shape(x)[1] * 2))
            #
            # for i in range(0, np.shape(x)[1], 2):
            #     hold_xy[:, i] = x[:, i]
            #     hold_xy[:, i+1] = y[:, i]

            pd.DataFrame(x).to_csv(main_path + folder + '/' + file_name + '_x_splined.csv')
            pd.DataFrame(y).to_csv(main_path + folder + '/' + file_name + '_y_splined.csv')

    except:
        pass  # this is hacky; the directory that contains all the trial folders should only contain trial folders
        # which contain the h5s, otherwise they'll just get skipped.





