# Targeted HILIC/Polar Analysis Workflow

## One-time setup

### Metatlas group

Analysts need to be in the metatlas group at NERSC. You can check if you are in this group via [Iris](https://iris.nersc.gov/) -- see the 'groups' tab. If you are not currently in the metatlas group, find the interface on the right hand side of the groups web page where you can request to be added to a group and enter a request to be added the the metatlas group. You will not be able to proceed until you have been added to the metatlas group.


### RClone configuration

1. Go to [jupyter.nersc.gov](https://jupyter.nersc.gov/) and login using your NERSC account.
2. Click the 'start' button for a Cori 'Shared CPU Node' and wait for the JupyterLab interface to load.
3. From the menu bar, select 'File' -> 'New' -> 'Terminal'.
4. Copy and paste the following command into the terminal:
   ```
   /global/common/software/m2650/metatlas-repo/utils/rclone_auth.sh
   ```
5. The output from step 4 will include a URL that you should copy into and open with a web browser that is logged in to your LBL Google account.
6. You will be prompted to authorize RClone to have edit access to Google Drive. Select your lbl.gov Google Account and then click the 'Allow' button.
7. Click the clipboard icon to copy the authorization code.

![clipboard icon screen shot](google_auth_copy_button.png)

8. Go back to the JupyterLab page and paste the authorization code into the terminal and hit 'Enter'.
9. To verify you RClone configuration was successful, copy and paste the following command into the terminal:

   ```
   /global/cfs/cdirs/m342/USA/shared-envs/rclone/bin/rclone ls rclone_test:sub
   ```

   Which should yield:
   ```
   119 If_you_see_this_then_RClone_has_been_properly_configured.txt
   ```

10. If you will be working on JGI data, then check that you have access to the
   [JGI_Metabolomics_Projects Google Drive folder](https://drive.google.com/drive/folders/0B-ZDcHbPi-aqZzE5V3hOZFc0dms)
   by copying and pasting the following command into the terminal:

   ```
   /global/cfs/cdirs/m342/USA/shared-envs/rclone/bin/rclone lsd metabolomics:Analysis_uploads
   ```

   Which should yield a listing of metabolomics experiment names similar to:
   ```
             -1 2021-08-30 10:01:06        -1 20210323_JGI-AK_SS_504264_GEBA_Pantoea-final_QE-HF_HILICZ_USHXG01602
             -1 2021-08-30 12:32:39        -1 20210518_JGI-AK_IG-SS_503256_BETO_Pceleri_QE-HF_HILICZ_USHXG01602
             -1 2021-09-13 16:39:15        -1 20210721_JGI-AK_JB_504782_PseudoOphi_final_QE-139_HILICZ_USHXG01490
             -1 2021-09-13 17:40:55        -1 20210723_JGI-AK_DB-TM_506963_LemCreek_final_QE-HF_HILICZ_USHXG01494
             -1 2021-09-13 16:39:15        -1 20210728_JGI-AK_MD_507130_Bioscales_pilot2_QE-139_HILICZ_USHXG01490
             -1 2021-09-10 16:05:18        -1 20210804_JGI-AK_PA-CT_507784_Frtlzr_Set1_QE-139_HILICZ_USHXG01490
             -1 2021-09-13 16:34:45        -1 20210819_JGI-AK_MK_506588_SoilWaterRep_final_QE-139_HILICZ_USHXG01490
   ```

   If instead you see:
   ```
   ERROR : : error listing: directory not found
   Failed to lsd with 2 errors: last error was: directory not found
   ```

   then you need to request access to the
   [JGI_Metabolomics_Projects Google Drive folder](https://drive.google.com/drive/folders/0B-ZDcHbPi-aqZzE5V3hOZFc0dms).
   Please repeat step 10 after you have been granted access.


### Make a directory to store work in progress

Still within the terminal in JupyterLab, run:
```
mkdir -p ~/metabolomics_data
```

## Per-project workflow

### Perform RT correction

#### Set Parameters
The `workflow_name` parameter will be supplied by Katherine or Suzie. For JGI projects, it will likely be one of `JGI-HILIC` or `JGI-C18`.

The `experiment_name` parameter can retrieved from the [Sample Tracking and QC Checkpoints - Northen Lab](https://docs.google.com/spreadsheets/d/126t1OeXQnCCgP6e-6Pac_Ku_A1R7MQLm_tl_Dkqsv_w/edit#gid=1548851545) Google Sheet. The experiment names can be found on the 'New Extraction' sheet in either column 'N' or 'O' depending on the type of chromatography that was performed. This value will be something like `20210723_JGI-AK_DB-TM_506963_LemCreek_final_QE-HF_HILICZ_USHXG01494`.

The `rt_predict_number` parameter is an integer that you'll need to increment if you re-run the RT alignment step. It should be set to 0 initially.

#### Run `submit_slurm_job.sh`

In your JupyterLab terminal, run the following command (where you substitute the 3 parameters described above):
```
/global/common/software/m2650/metatlas-repo/papermill/submit_slurm_job.sh workflow_name experiment_name rt_predict_number
```

For example, your command with the parameters substituted in will be something like:
```
/global/common/software/m2650/metatlas-repo/papermill/submit_slurm_job.sh JGI-HILIC 20210804_JGI-AK_PA-CT_507784_Frtlzr_Set1_QE-139_HILICZ_USHXG01490 0
```

This will submit a slurm job. On Cori, you will receive an email when the job starts executing and when it has completed. On Perlmutter, the SLRUM job notifications emails are currently broken. Typical HILIC jobs take 2 to 5 hours to complete.

#### Evaluate Outputs

Once the job has completed, you should check the files generated to make sure the RT correction models look acceptable. You can find the output PDF files at `~/metabolomics_data/<experiment_name>/<user_id>_<rt_predict_number>_0/Targeted/<workflow_name>/RT_Alignment/`. One easy way to view these files is to open them from the [Jupyter](https://jupyter.nersc.gov/) file browser. In `Actual_vs_Predicted_RTs.pdf`, you want to check that the default model (median-based RT correction and polynomial model) gives a good fit. At the bottom of the `Actual_vs_Predicted_RTs.pdf`, you can find the 'FileIndex' number that corresponds to the 'median' correction. Once you have determined the 'FileIndex' for median, you want to find the plot that has 'File: \<FileIndex\>' above it. This is the plot showing the models for the median-based RT correction. On each plot, there should be a red line (linear model) and green line (polynomial model). In many cases the lines for these models will almost be right on top of each other and you might not be able to see both of the lines unless you zoom in near the line ends.

If the median-based polynomial model does not give a good fit, then you will want to re-run  `submit_slurm_jobs.sh` with additional parameters (and an incremented `rt_predict_number`). See [Passing Additional Notebook Parameters To submit_slurm_jobs.sh](#passing-additional-notebook-parameters-to-submit_slurm_jobsh) to learn how to pass the parameters. The two most relevant parameters for choosing a different model are `use_poly_model` and `dependent_data_source`. Documentation of the parameters and their possible values can be found in the first code block of the [RT_prediction.ipynb](https://github.com/biorack/metatlas/blob/main/notebooks/reference/RT_Prediction.ipynb) notebook.

### Perform ISTDsEtc Analysis

1. Launch [jupyter.nersc.gov](https://jupyter.nersc.gov/) in your web browser and start a 'Shared CPU Node' on Cori or Perlmutter.
2. Open `~/metabolomics_data/<experiment_name>/<user_id>_<rt_predict_number>_0/Targeted/<workflow_name>/<project_id>_<workflow_name>_ISTDsEtc-POS.ipynb` within JupyterLab (you no longer need to use the Classic Notebook interface). If you are prompted to select a kernel, select 'Metatlas Targeted'.
3. The first code cell of the notebook contains descriptions of the parameters and their default values. The second code cell of the notebook contain parameter values that were auto-populated from the RT correction slurm job. These values in the second code block will override the default values from the first code block. The third code block validates your parameter values and also validates that your environment is correctly configured. Execute the first 3 code cells and see if there are any errors. If you get an error message (usually error messages will be in red), you will need to correct the issue so that the cell executes without giving an error before moving on. The error messages commonly see at this point in the workflow generally include some description of what action is needed to correct the problem.
4. Execute the code blocks 4 and 5 to read in data and bring up the Annotation GUI.
5. For each of the compound-adduct pairs in your atlas, set the RT min and RT max boundaries to just contain the EIC peak that corresponds to the compound you are currently evaluating. For each compound-adduct pair, you must either select one of the MSMS-quality descriptors (upper set of radio buttons) or use the bottom set of radio buttons to mark the compound-adduct pair for removal. Failure to set either MSMS-quality descriptors or the remove state for each compound-adduct pair will result in the subsequent step throwing an error.
6. Execute the 6th code block to generate output files and upload them to Google Drive.
7. When the notebook completes, the second to last line will be a link to the location where the files have been uploaded to Google Drive. Follow this link and review your output files. The destination on Google Drive will be a sub-folder under [this Google Drive folder](https://drive.google.com/drive/folders/19Ofs5AHB3O8-NYApJUwj4YvH8TbKCGJW?usp=sharing).
8. Repeat steps 1-7 for the the corresponding NEG mode notebook.
9. Move your output folder on Google Drive into the location indicated in column 'M' of the 'New Extraction' sheet in [Sample Tracking and QC Checkpoints - Northen Lab](https://docs.google.com/spreadsheets/d/126t1OeXQnCCgP6e-6Pac_Ku_A1R7MQLm_tl_Dkqsv_w/edit#gid=1548851545) Google Sheet.
10. Email Katherine a link to the output folder so that she can review your outputs.


### Perform FinalEMA-HILIC Analysis

1. Follow the same steps as the ISTDsEtc analysis except use the notebook name `<project_id>_<workflow_name>-_EMA-POS.ipynb`.
2. Open the `POS_<project_id>_Final_Identifications.xlsx` file in the output directory on Google Drive.
3. Make sure everything looks as expected in the spreadsheet.
4. If there are any compound-adduct pairs that need to be removed at this point (because they are duplicated or you can now determine a similar compound was a better match for a given peak), you can place 'REMOVE' in columns B, M, and N. In columns B and N you should also include some description such as 'REMOVE - duplicate' or 'REMOVE - other isomer preferred (tryptophan matches MSMS reference)' or 'REMOVE - other isomer preferred (tryptophan matches reference RT)'.
5. If you are able to resolve some overlapping identifications at this point, then update the value in column B for the preferred match to no longer include the name of the molecule that is no longer considered a possible match.
6. Repeat steps 1-5 for the corresponding NEG mode notebook.
7. Move your output folder on Google Drive into the location indicated in column 'M' of the 'New Extraction' sheet in [Sample Tracking and QC Checkpoints - Northen Lab](https://docs.google.com/spreadsheets/d/126t1OeXQnCCgP6e-6Pac_Ku_A1R7MQLm_tl_Dkqsv_w/edit#gid=1548851545) Google Sheet.
8. Email Katherine a link to the output folder so that she can review your outputs.

## Using the Annotation GUI

### Key Bindings

`l` or right arrow - next compound-adduct pair

`h` or left arrow - previous compound-adduct pair

`k` or up arrow - next MSMS reference for this compound-adduct pair

`j` or down arrow - previous MSMS reference for this compound-adduct pair

`x` - sets the remove radio button

`m` - steps through the similar compound-adduct pairs and matches the RT bounds to those of the similar compound-adduct pair

`z` - steps though zoom levels of 1x, 5x, 25x on the MSMS mirror plot

`s` - toggles on/off the display of similar compounds

## Advanced Usage

### Passing Additional Notebook Parameters To `submit_slurm_job.sh`

Any of the parameters in the first code block of the `RT_Prediction.ipynb` notebook can be passed to the `submit_slurm_job.sh` script. There are two command line options that can be used to supply parameters.

The `-p` option can be used to supply a parameter that takes a single unstructured value (number, string, or boolean): `-p parameter_name=parameter_value`. The `-p` option can be supplied multiple times to the `submit_slurm_job.sh` script if needed.

The `-y` option can be used to supply multiple parameters and structured parameters (lists, dictionaries, nested data structures). The parameter names and values are passed as YAML or JSON strings: `-y "{'parameter_name1': ['list', 'of', 'values'], 'parameter_name2': 'another value'}"`.

The `-p` and `-y` options can be used at the same time.

An example usage of `-p` and `-y`:
```
/global/common/software/m2650/metatlas-repo/papermill/submit_slurm_job.sh \
    JGI-HILIC 20210804_JGI-AK_PA-CT_507784_Frtlzr_Set1_QE-139_HILICZ_USHXG01490 0 \
    -y “{'rt_min_delta': -1.5, 'rt_max_delta': 1.5, 'inchi_keys_not_in_model': [‘CZMRCDWAGMRECN-UGDNZRGBSA-N', 'ISAKRJDGNUQOIC-UHFFFAOYSA-N']}" \
    -p stop_before=atlases
```
