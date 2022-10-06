#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
import time
from helpers_voxelized_conditions import *

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument("img", nargs=1)
@click.option("-n", default='1e4', help="Number of samples")
def go(img, n):
    n = int(float(n))

    print('NOT working, not more efficient')
    exit(0)

    # read img
    img = itk.imread(img)

    # create voxelized sampling
    v = ImagePDFSampler(img)

    # sample (version 1 is faster)
    start = time.time()
    pi, pj, pk = v.sample_indices_phys(n)
    end = time.time()
    print(f" done in {end - start:0.3f} sec")

    # write
    out = gate.create_image_like(img)
    for a, b, c in zip(pi, pj, pk):
        p = [c, b, a]
        index = img.TransformPhysicalPointToIndex(p)
        # print('p', p)
        # print('index', index)
        out.SetPixel(index, img.GetPixel(index) + 1)
    itk.imwrite(out, "b.mhd")

    # test FIXME compare with initial image
    imga = itk.array_view_from_image(img)
    outa = itk.array_view_from_image(out)
    nn = outa[imga == 1].sum()
    zz = outa[imga == 0].sum()
    if nn != n or zz != 0:
        print('ERROR ! ', nn, zz)


# --------------------------------------------------------------------------
if __name__ == "__main__":
    go()
