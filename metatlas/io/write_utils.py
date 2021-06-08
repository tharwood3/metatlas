""" Utility functions used in writing files"""

import filecmp
import logging
import os
import tempfile

import pandas as pd

logger = logging.getLogger(__name__)


def make_dir_for(file_path):
    """makes directories for file_path if they don't already exist"""
    directory = os.path.dirname(file_path)
    if directory != "":
        os.makedirs(directory, exist_ok=True)


def check_existing_file(file_path, overwrite=False):
    """Creates directories as needed and throws an error if file exists and overwrite is False"""
    make_dir_for(file_path)
    try:
        if not overwrite and os.path.exists(file_path):
            raise FileExistsError(f"Not overwriting {file_path}.")
    except FileExistsError as err:
        logger.exception(err)
        raise


def export_dataframe(dataframe, file_path, description, overwrite=False, **kwargs):
    """
    inputs:
        dataframe: pandas DataFrame to save
        file_path: string with path of file to create
        description: free string for logging
        overwrite: if False, raise error if file already exists
        remaining arguments are passed through to to_csv()
    """
    check_existing_file(file_path, overwrite)
    dataframe.to_csv(file_path, **kwargs)
    logger.info("Exported %s to %s.", description, file_path)


def raise_on_diff(dataframe, file_path, description, **kwargs):
    """
    inputs:
        dataframe: pandas DataFrame to save
        file_path: string with path of file to compare against
        description: free string for logging
        kwargs: passed through to to_csv()

    If file_path exists and does not match file that would be generated by
    saving dataframe to a csv, then raise ValueError
    """
    if not os.path.exists(file_path):
        return
    with tempfile.NamedTemporaryFile(delete=False) as temp_path:
        dataframe.to_csv(temp_path, **kwargs)
        same = filecmp.cmp(file_path, temp_path.name)
        os.remove(temp_path.name)
    if same:
        logger.info("Data in %s is the same as %s.", description, file_path)
    else:
        try:
            raise ValueError("Data in %s is not the same as %s." % (description, file_path))
        except ValueError as err:
            logger.exception(err)
            raise


def export_dataframe_die_on_diff(dataframe, file_path, description, **kwargs):
    """
    inputs:
        dataframe: pandas DataFrame to save
        file_path: string with path of file to create
        description: free string for logging
        kwargs: passed through to to_csv()

    If file_path does not exist then save the dataframe there
    If file_path exists and matches data in dataframe then do nothing
    If file_path exists and does not match dataframe then raise ValueError
    """
    raise_on_diff(dataframe, file_path, description, **kwargs)
    if not os.path.exists(file_path):
        export_dataframe(dataframe, file_path, description, **kwargs)
