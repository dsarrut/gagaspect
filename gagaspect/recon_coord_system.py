#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import itk
import numpy as np
import opengate as gate
import gatetools as gt
import click

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument("mhd_filename", nargs=1)
@click.option("--ct", required=True, help="ct filename")
@click.option(
    "--tr", default=(0, 0, 0), type=(float, float, float), help="spect translation (mm)"
)
@click.option("--output", "-o", default="AUTO", help="output filename")
def go(mhd_filename, output, tr, ct):
    # open the param file

    # mhd_filename = "./recon.mhd"
    # ct_filename = "./data/291_CT_4mm.mhd"
    # output = "./recon_s.mhd"

    # read ct info7
    ct_info = gate.read_image_info(ct)
    print('CT image : ')
    gate.print_dic(ct_info)
    ct_center = ct_info.size / 2.0 * ct_info.spacing + ct_info.origin

    # read mhd
    img = itk.imread(mhd_filename)
    img_info = gate.get_info_from_image(img)
    print('Recon image : ')
    gate.print_dic(img_info)

    # fip from rtk to opengate
    flip = np.matrix([[1.0, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0], [0, 0, 0, 1]])
    m = itk.matrix_from_array(flip)

    # flip image
    img = gt.applyTransformation(input=img, force_resample=True, matrix=m)
    img_info = gate.get_info_from_image(img)

    # compute origin for the img
    img_center = img_info.size * img_info.spacing / 2.0
    ct_center += tr
    origin = ct_center - img_center

    # write
    img.SetOrigin(origin)
    itk.imwrite(img, output)

    # print
    img_info = gate.get_info_from_image(img)
    print('Final image : ')
    gate.print_dic(img_info)


# --------------------------------------------------------------------------
if __name__ == "__main__":
    go()
