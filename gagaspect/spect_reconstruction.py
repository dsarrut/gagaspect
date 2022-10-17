#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import opengate as gate
import click
import numpy as np
import itk
import os
import gatetools as gt

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument("inputs", nargs=-1)
@click.option("--ene", "-e", required=True, help="Number of energy windows")
@click.option("--output", "-o", required=True, help="output filename (.mhd)")
@click.option("--spacing", default=4, help="Reconstruction spacing")
@click.option("--size", default=128, help="Reconstruction size")
@click.option("--ct", required=True, help="ct filename")
@click.option(
    "--recon_param",
    default="--niterations 3 --nprojpersubset 10",
    help="Parameters for reconstruction rtkosem command line, as a string",
)
@click.option(
    "--dry",
    is_flag=True,
    default=False,
    help="Do not reconstruct, only print the cmd lines",
)
@click.option(
    "--spect_tr",
    default=(0, 0, 0),
    type=(float, float, float),
    help="spect translation (mm)",
)
def go(inputs, ene, output, spacing, size, ct, spect_tr, dry, recon_param):
    """

    Example:
    spect_reconstruction.py ref_projection_?.mhd -e 3 -o test.mhd --spacing 5 --size 128 --ct ct_5mm.mhd --spect_tr 0 0 50

    :param inputs: list of filenames with projections compute by Monte Carlo
    :param ene: number of energy windows (for Tc99m, it is 3, spectrum + scatter + primary)
    :param output: output reconstructed image filename
    :param spacing: output spacing in mm
    :param size: output size (cubic)
    :param ct: initial ct image to get the coordinate system. This image is assumed to be centered in the simulation
    :param spect_tr: translation of spect detector
    :param dry: do not compute, only write the command lines
    :param recon_param: additional parameters for the reconstruction
    :return:
    """
    # STEP 1 - split spect projection according to energy windows
    # Input = nb ene, filenames
    # Output = files + nb of angles
    # split_spect_projections -e 3 run.6h7o08l5/ref_projection_?.mhd -o run.6h7o08l5/projections.mhd
    nb_ene = int(ene)
    outputs = gate.split_spect_projections(inputs, nb_ene)
    nb_angles = outputs[0].shape[0]
    e = 0
    projection_filenames = []
    for o in outputs:
        f = output.replace(".mhd", f"_projections_{e}.mhd")
        itk.imwrite(o, f)
        projection_filenames.append(f)
        e += 1

    # STEP2 - create the geometry according to the number of angles
    # rtk geometry (or as input ?
    xml = f"geom_{nb_angles}.xml"
    cmd = f"rtksimulatedgeometry -o {xml} -f 0 -n {nb_angles} -a 360 --sdd 0 --sid 410"
    print(cmd)
    if not dry:
        os.system(f"{cmd}")
    print(f"Geometry file: {xml}")

    # STEP3 - reconstruction
    # osem. Warning lot of options -> as a str param
    recon_filenames = []
    for e in range(nb_ene):
        out1 = output.replace(".mhd", f"_recon_p{e}.mhd")
        cmd = (
            f"rtkosem -g {xml} -o {out1} --path . --regexp "
            f"{projection_filenames[e]} --spacing {spacing} --dimension {size} {recon_param}"
        )
        print(cmd)
        recon_filenames.append(out1)
        if not dry:
            os.system(f"{cmd}")

    # STEP 4 - rotate final image
    flip = np.matrix([[1.0, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]])
    m = itk.matrix_from_array(flip)
    ct_info = gate.read_image_info(ct)
    print("Read CT image : ", ct)

    for e in range(nb_ene):
        # ct center is the coordinates of the image center in the img coord system
        # because the gate world is assumed to be at the image center
        ct_center = (
            ct_info.size / 2.0 * ct_info.spacing
            + ct_info.origin
            - ct_info.spacing / 2.0
        )
        f = recon_filenames[e]
        out2 = output.replace(".mhd", f"_recon_p{e}_rot.mhd")
        img = itk.imread(f)
        img = gt.applyTransformation(input=img, force_resample=True, matrix=m)
        img_info = gate.get_info_from_image(img)
        # the img_center is the center of the reconstructed image
        # it should be aligned with the world
        img_center = img_info.size * img_info.spacing / 2.0 - img_info.spacing / 2.0
        ct_center += spect_tr
        # the origin is such that the img center has the same img coord
        # than in the initial ct
        origin = ct_center - img_center
        img.SetOrigin(origin)
        if not dry:
            itk.imwrite(img, out2)
        print(f"Final image {out2} with origin = {origin}")


# --------------------------------------------------------------------------
if __name__ == "__main__":
    go()
