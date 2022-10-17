#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from itk import RTK as rtk


def generate_rtk_geometry(param):
    # create geom object
    geom = rtk.ThreeDCircularProjectionGeometry.New()

    # fill with
    for i in range(param.geom_nb_angles):
        angle = param.geom_first_angle + i * 360.0 / param.geom_nb_angles
        geom.AddProjection(
            param.geom_sid,
            param.geom_sdd,
            angle,
            param.geom_offset_x,
            param.geom_offset_y,
        )

    # write xml file
    w = rtk.ThreeDCircularProjectionGeometryXMLFileWriter.New()
    w.SetFilename(param.geom_filename)
    w.SetObject(geom)
    w.WriteFile()

    return geom
