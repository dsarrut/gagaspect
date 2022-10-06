#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import opengate as gate
import click
from pathlib import Path
import os
import stat

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option("--output_folder", "-o", default="AUTO", help="output folder, auto=rnd")
@click.option("--nb_jobs", "-n", default=1, help="number of jobs to submit")
@click.option(
    "--json_file",
    "-j",
    required=True,
    help="json parameters for the spect simulation, input of spect_simulation.py",
)
@click.option(
    "--root_path",
    "-r",
    default='/pbs/home/d/dsarrut/gagaspect',
    help="root folder on ccin2p3",
)
@click.option(
    "--slurm_file",
    "-s",
    default='gagaspect/job_ccin2p3.slurm',
    help="slurm file for job submission",
)
@click.option(
    "--local",
    "-l",
    default=False,
    is_flag=True,
    help="Do not use sbatch and slurm, local execution",
)
def go(output_folder, nb_jobs, json_file, root_path, slurm_file, local):
    # initial folders
    bin_path = f"{root_path}/gagaspect"
    results_path = f"{root_path}/results"

    # files
    slurm_file = f"{root_path}/{slurm_file}"
    bin_file = f"{bin_path}/spect_simulation.py"
    json_file = f"{root_path}/{json_file}"

    # create new folder
    if output_folder == "AUTO":
        output_folder = gate.get_random_folder_name(create=False)
        output_folder = f"{results_path}/{output_folder}"
    Path(output_folder).mkdir(parents=True, exist_ok=True)

    # verbose
    print(f'Root path        {root_path}')
    print(f'Bin path         {bin_path}')
    print(f'Results path     {results_path}')
    print(f'Slurm file       {slurm_file}')
    print(f'Json param file  {json_file}')
    print(f"Output folder    {output_folder}")

    # create submit script
    submit_file = f"{output_folder}/submit.sh"
    f = open(submit_file, "w", 0o744)
    f.write(f"echo folder     = {output_folder}\n")
    f.write(f"echo Nb of jobs = {nb_jobs}\n")

    r = f"sbatch {slurm_file} "
    if local:
        r = ""

    for i in range(nb_jobs):
        output = f"{output_folder}/job_{i:03d}"
        f.write(f"mkdir -p {output}\n")
        s = f"{r} {bin_file} {json_file} -o {output} \n"
        f.write(s)

    f.close()
    st = os.stat(submit_file)
    os.chmod(submit_file, st.st_mode | stat.S_IEXEC)
    print(submit_file)


# --------------------------------------------------------------------------
if __name__ == "__main__":
    go()
