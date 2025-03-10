"""Plot set of TIC plots. One sample per sub-plot"""
# pylint: disable=invalid-name,too-many-arguments,too-few-public-methods,too-many-locals

import logging

from pathlib import Path
from typing import Any, List, Optional

import matplotlib
from matplotlib.ticker import MultipleLocator

from metatlas.io.metatlas_get_data_helper_fun import get_bpc
from metatlas.plots import plot_set
from metatlas.plots import utils

logger = logging.getLogger(__name__)

MetatlasDataset = List[List[Any]]  # avoiding a circular import


class Tic(plot_set.Plot):
    """TIC for a single sample"""

    def __init__(self, title: str, group_name: str, h5_file_name: str, polarity: str):
        super().__init__(title, group_name)
        self.h5_file_name = h5_file_name
        assert polarity in ["positive", "negative"]
        self.polarity = polarity

    def plot(self, ax: matplotlib.axes.Axes, back_color: utils.Color = "white") -> None:
        """Draw plot of TIC on ax"""
        super().plot(ax, back_color)
        dataset = f"ms1_{self.polarity[:3]}"
        tic_df = get_bpc(self.h5_file_name, dataset=dataset, integration="tic")
        ax.plot(tic_df["rt"], tic_df["i"])
        ax.xaxis.set_minor_locator(MultipleLocator(1))


def save_sample_tic_pdf(
    data: MetatlasDataset,
    polarity: str,
    file_name: str,
    overwrite: bool = False,
    sharey: bool = True,
    x_min: Optional[float] = None,
    x_max: Optional[float] = None,
    y_min: Optional[float] = None,
    y_max: Optional[float] = None,
    max_plots_per_page: int = 30,
) -> None:
    """Generate a PDF of TIC plots for samples within data"""
    assert polarity in ["positive", "negative"]
    file_order_tics = []
    for sample in data:
        fields = Path(sample[0]["lcmsrun"].name).stem.split("_")
        title = f"{fields[0]}_{fields[11]}_{fields[13]}_{fields[15]}"
        group_name = sample[0]["group"].short_name
        h5_file_name = sample[0]["lcmsrun"].hdf5_file
        file_order_tics.append(Tic(title, group_name, h5_file_name, polarity))
    tics = sorted(file_order_tics, key=lambda x: (x.group_name, x.title))
    with plot_set.PlotSet(tics, max_plots_per_page, x_min, x_max, y_min, y_max, sharey) as plots:
        plots.save_pdf(file_name, title="TICs", overwrite=overwrite)
