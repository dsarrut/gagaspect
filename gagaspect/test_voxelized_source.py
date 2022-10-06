#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
import time
from helpers_voxelized_conditions import *

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument("img", nargs=1)
@click.option("-n", default='1e4', help="Number of samples")
@click.option("--version", "-v", default=1, help="Version 1 or 2")
def go(img, n, version):
    n = int(float(n))

    # read img
    img = itk.imread(img)

    # create voxelized sampling
    v = ImagePDFSampler(img, version)

    # sample (version 1 is faster)
    start = time.time()
    if version == 1:
        i, j, k = v.sample_indices(n)
    else:
        i, j, k = v.sample_indices_slower(n)
    end = time.time()
    print(f" done in {end - start:0.3f} sec")

    # write
    imga = itk.array_view_from_image(img)
    outa = np.zeros_like(imga)
    for a, b, c in zip(i, j, k):
        outa[a, b, c] += 1
    out = itk.image_from_array(outa)
    out.CopyInformation(img)
    itk.imwrite(out, "a.mhd")

    # test FIXME compare with initial image
    nn = outa[imga == 1].sum()
    zz = outa[imga == 0].sum()
    if nn != n or zz != 0:
        print('ERROR ! ', nn, zz)


# --------------------------------------------------------------------------
if __name__ == "__main__":
    go()
