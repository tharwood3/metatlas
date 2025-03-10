"""Transfer files to Google Drive"""

import logging
import os

from pathlib import Path

from IPython.core.display import display, HTML

from metatlas.datastructures.analysis_identifiers import AnalysisIdentifiers
from metatlas.io import rclone

logger = logging.getLogger(__name__)

RCLONE_PATH = "/global/cfs/cdirs/m342/USA/shared-envs/rclone/bin/rclone"


def copy_outputs_to_google_drive(ids: AnalysisIdentifiers) -> None:
    """
    Recursively copy the output files to Google Drive using rclone
    Inputs:
        ids: an AnalysisIds object
    """
    logger.info("Copying output files to Google Drive")
    rci = rclone.RClone(RCLONE_PATH)
    fail_suffix = "not copying files to Google Drive"
    if rci.config_file() is None:
        logger.warning("RClone config file not found -- %s.", fail_suffix)
        return
    drive = rci.get_name_for_id(ids.google_folder)
    if drive is None:
        logger.warning(
            "RClone config file does not contain Google Drive folder ID '%s' -- %s.",
            ids.google_folder,
            fail_suffix,
        )
        return
    folders = Path(ids.output_dir).parts[-5:]
    sub_folders_string = os.path.join("Analysis_uploads", *folders)
    rci.copy_to_drive(ids.output_dir, drive, sub_folders_string, progress=True)
    logger.info("Done copying output files to Google Drive")
    path_string = f"{drive}:{sub_folders_string}"
    display(
        HTML(f'Data is now on Google Drive at <a href="{rci.path_to_url(path_string)}">{path_string}</a>')
    )
