"""Environment setup functions"""

import getpass
import json
import logging
import os
import re
import shutil

from pathlib import Path

logger = logging.getLogger(__name__)

SOURCE_NOTEBOOK = {
    "RT-Predict": "Workflow_Notebook_VS_Auto_RT_Predict_V2.ipynb",
    "ISTDsEtc": "Targeted.ipynb",
    "FinalEMA-HILIC": "Targeted.ipynb",
}

SOURCE_ATLAS_PREFIX = {
    "RT-Predict": None,
    "ISTDsEtc": "HILICz150_ANT20190824_PRD_IS_LabUnlab2_",
    "FinalEMA-HILIC": "HILICz150_ANT20190824_TPL_EMA_Unlab_",
}


def install_kernel():
    """
    Copies kernel.json from repo to active location under home directory.
    Only for use on NERC!
    """
    logger.info('Installing kernel.json for "Metatlas Targeted".')
    repo_path = Path(__file__).resolve().parent.parent.parent
    source = repo_path / "notebooks" / "kernels" / "metatlas-targeted.kernel.json"
    dest_dir = Path.home() / ".local" / "share" / "jupyter" / "kernels" / "metatlas-targeted"
    os.makedirs(dest_dir, exist_ok=True)
    shutil.copyfile(source, dest_dir / "kernel.json")
    logger.info('Kernel installation complete. Reload Jupyter notebook page to see new kernel". ')


def repo_dir():
    """Returns a string with the path to the root of the Metatlas git repo"""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def create_all_notebooks(output_type, base_output_dir, experiment_id, analysis_number):
    """
    Creates Jupyter notebooks with appropriate filename and pre-populated parameters
    inputs:
        output_type: one of 'RT-Predict', 'ISTDsEtc', 'FinalEMA-HILIC'
        base_output_dir: project directory containing the experiment directories
        experiment_id: '_' delimited experiment identifier
        analysis_number: increment to not overwrite existing analysis outputs
    """
    possible_outputs = ["RT-Predict", "ISTDsEtc", "FinalEMA-HILIC"]
    outputs = possible_outputs[: (1 + possible_outputs.index(output_type))]
    parameters = {
        "experiment": experiment_id,
        "metatlas_repo_path": repo_dir(),
        "output_directory": base_output_dir,
        "analysis_number": analysis_number,
    }
    analysis_id = f"{getpass.getuser()}{parameters['analysis_number']}"
    tokens = parameters["experiment"].split("_")
    output_dir = os.path.join(base_output_dir, experiment_id)
    os.makedirs(output_dir, exist_ok=True)
    for output in outputs:
        parameters["output_type"] = output
        for polarity in ["positive", "negative"] if output != "RT-Predict" else [None]:
            source = os.path.join(repo_dir(), "notebooks", "reference", SOURCE_NOTEBOOK[output])
            if polarity is not None:
                parameters["polarity"] = polarity
                pol = polarity[:3].upper()
                parameters["source_atlas"] = f"{SOURCE_ATLAS_PREFIX[output]}_{pol}_{tokens[3]}_{analysis_id}"
            generate_notebook(source, output_dir, parameters)


def generate_notebook(source, output_dir, parameters):
    """
    Creates a notebook from source in output_dir that has updated parameters.
    inputs:
        source: path of input Jupyter notebook
        output_dir: directory to write output Jupyter notebook
        parameters: dict of parameters to update in the notebook
    parameters must have atleast the following keys: analysis_number, experiment, output_type
    """
    if "polarity" in parameters:
        pol = parameters["polarity"][:3].upper()
        suffix = f"{parameters['output_type']}_{pol}"
    else:
        suffix = "RT-Predict"
    tokens = parameters["experiment"].split("_")
    dest = os.path.join(output_dir, "_".join(tokens[3:5] + [suffix]) + ".ipynb")
    create_notebook_with_parameters(source, dest, parameters)


def create_notebook_with_parameters(source, dest, parameters):
    """
    Copies source notebook to dest and updates parameters
    inputs:
        source: path of input notebook
        dest: path of destination notebook
        parameters: dict with name of parameter in key and new value in value
    """
    with open(source) as source_fh:
        data = json.load(source_fh)
    eq_pat = re.compile(r"^([^#= ]+)\s*=.+$")
    param_source = data["cells"][1]["source"]
    for i, line in enumerate(param_source):
        re_match = eq_pat.match(line)
        if re_match:
            param_name = re_match.group(1)
            if param_name in parameters:
                new_value = parameters[param_name]
                out_value = f"'{new_value}'" if isinstance(new_value, str) else new_value
                param_source[i] = f"{param_name} = {out_value}\n"
    with open(dest, "w") as out_fh:
        json.dump(data, out_fh)


def validate_data_dir(base_data_dir, experiment_id):
    """Raise FileNotFoundError if base_data_dir / experiment_id is not an existing directory"""
    experiment_dir = os.path.join(base_data_dir, experiment_id)
    try:
        if not os.path.isdir(experiment_dir):
            raise FileNotFoundError(f"Data directory does not exist at {experiment_dir}.")
    except FileNotFoundError as err:
        logger.exception(err)
        raise err
