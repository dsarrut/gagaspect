#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import itk
import numpy as np
import opengate as gate
import click
import os
import gatetools as gt
from pathlib import Path

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument("result_folder", nargs=1)
@click.option("--nb_heads", default=4, help="number of heads 1 to 4")
def go(result_folder, nb_heads):
    # loop over folder in the result folder
    job_folders = []
    for subdir, dirs, files in os.walk(result_folder):
        if 'job_' in subdir:
            job_folders.append(subdir)

    print(f'Found {len(job_folders)} job folders')

    # add results
    out_files = []
    for h in range(nb_heads):
        files = []
        output_file = f'{result_folder}/projections_{h}.mhd'
        for f in job_folders:
            file = f'{f}/ref_projection_{h}.mhd'
            f = Path(file)
            if f.is_file():
                files.append(file)
        gt.image_sum(files, output_file)
        print(f'For head {h} : {len(files)} {output_file}')
        out_files.append(output_file)

    # FIXME : add stats about jobs : PPS + time + nb particles etc -> merge stat files ?

    # read info of first image
    output = f'{result_folder}/projections.mhd'
    f = out_files[0]
    img = itk.imread(f)
    out = itk.array_view_from_image(img)

    # loop to merge the slices
    for f in out_files[1:]:
        img = itk.imread(f)
        arr = itk.array_view_from_image(img)
        out = np.concatenate((out, arr), axis=0)

    o = itk.image_from_array(out)
    o.CopyInformation(img)
    info = gate.get_info_from_image(o)

    # change the origin to center everything
    origin = -info.size / 2.0 * info.spacing + info.spacing / 2.0
    o.SetOrigin(origin)
    print(f'Change the origin to center: {origin}')

    itk.imwrite(o, output)
    print(f'Final output {output}')


# --------------------------------------------------------------------------
if __name__ == "__main__":
    go()
