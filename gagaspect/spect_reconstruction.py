#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import itk
import numpy as np
import opengate as gate
import click
import json
from box import Box
import helpers_reconstruction as rh

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument("folder")
@click.option("--output", "-o", required=True, help="output file")
def go(folder, output):
    print(folder)

    # read projections file (LATER: or create)
    projections_fn = f"{folder}/a.mhd"

    # parameters
    param = Box()

    # geom
    param.geom_filename = "a.xml"
    param.geom_sid = 140  # FIXME
    param.geom_sdd = 0
    param.geom_first_angle = 0
    param.geom_nb_angles = 120  # FIXME
    param.geom_offset_x = -280.54680999999999  # FIXME
    param.geom_offset_y = -280.54680999999999  # FIXME

    # create, save and read xml geometry file
    geometry = rh.generate_rtk_geometry(param)
    # print(geometry)
    # write_xml(param.xml_filename)

    # reconstruction
    # rtk_osem_reconstruction(param)
    # if param.wite_reconstructed_img:
    #    itk.imwrite(param.reconstructed_img, param.reconstructed_img_filename)

    # flip and adjust origin


# --------------------------------------------------------------------------
if __name__ == "__main__":
    go()
