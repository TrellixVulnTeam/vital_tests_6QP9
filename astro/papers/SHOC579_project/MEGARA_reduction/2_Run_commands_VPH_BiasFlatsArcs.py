import numpy as np
import pandas as pd
import lime as lm
import shutil
import yaml

from pathlib import Path
from numina.user.helpers import create_datamanager, load_observations
from numina.user.baserun import run_reduce
from numina.util import context as ctx
from astropy.io import fits


def delete_task_temp_folder(ob_id, task_id, root_dir):

    for folder in ['work', 'result']:
        temp_folder = root_dir/f'obsid{ob_id}_{task_id}_{folder}'
        if temp_folder.is_dir():
            shutil.rmtree(temp_folder)

    return


def warning_messange(task_name, run_folder):

    if 'arc' in task_name:
        with open(run_folder/f'{run_id}.yml', "r") as stream:
            yml_dict = yaml.safe_load(stream)
            for fits_frame in yml_dict['frames']:
                print('-- ', fits_frame, fits.getval(run_folder/f'data/{fits_frame}', 'VPH'), fits.getval(run_folder/f'data/{fits_frame}', 'SPECLAMP'))

    return


# Configuration file
cfg_file = '../obsConf.ini'
obs_conf = lm.load_cfg(Path(cfg_file))
reduction_cfg = obs_conf['Megara_reduction']

# Data location
reduction_folder = Path(reduction_cfg['root_folder'])
data_folder = reduction_folder/'data'
rd_df_address = Path(reduction_cfg['rd_df_address'])
original_yml = Path().resolve()/'shoc579_req.yml'

# Loading project configuration file
obj_list = reduction_cfg['obj_list']
std_list = reduction_cfg['std_star_list']

# Dataframe with files list
files_DF = lm.load_lines_log(f'{rd_df_address}.txt')

# Generate the task files for each OB:
OB_list = files_DF['OB'].unique()
OB_list.sort()
idx_start = 0 # Bias
idx_finish = 5 # Arc

# Run the pipeline one OB and VPH at a time:
for OB in OB_list:

    # if OB == 'OB0003':

        idcs_OB = files_DF.OB == OB
        VPH_list = files_DF.loc[idcs_OB, 'VPH'].unique()

        for VPH in VPH_list:
            if VPH != 'MR-B':

                task_file_address = f'{reduction_folder}/{OB}_{VPH}_task_list.txt'
                task_DF = pd.read_csv(task_file_address, delim_whitespace=True, header=0, index_col=0)

                # Create clean requirements file at each run
                req_yml = reduction_folder/f'control_{OB}_{VPH}_phase1.yaml'

                # Decide tasks to run
                idcs_tasks = task_DF.index >= idx_start
                task_list = task_DF.loc[idcs_tasks].task_id.values
                task_file_list = task_DF.loc[idcs_tasks].file_name.values
                idcs_tasks = task_DF.loc[idcs_tasks].index.values

                # Delete previous runs for security
                if idx_start == 0:
                    shutil.copyfile(original_yml, req_yml)
                else:
                    print('- Deleting from previous steps')
                for i, task in enumerate(task_list):
                    delete_task_temp_folder(task, idcs_tasks[i], reduction_folder)

                # Define data manager
                dm = create_datamanager(req_yml, reduction_folder, data_folder)

                # Load the observation files
                with ctx.working_directory(reduction_folder):
                    sessions, loaded_obs = load_observations(task_file_list, is_session=False)
                    dm.backend.add_obs(loaded_obs)

                # Run the tasks
                for i, idx_task in enumerate(idcs_tasks):
                    if idx_task <= idx_finish:
                        run_id = task_list[i]
                        print(f'Running: {run_id}')
                        warning_messange(run_id, reduction_folder)

