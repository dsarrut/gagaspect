#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import opengate as gate
import numpy as np
import pathlib
import itk
import opengate.contrib.spect_ge_nm670 as gate_spect


def make_training_dataset_simulation(param, sim=None):
    # create the simulation
    if not sim:
        sim = gate.Simulation()

    # main options
    ui = sim.user_info
    ui.g4_verbose = False
    ui.visu = param.visu
    ui.number_of_threads = param.number_of_threads
    ui.verbose_level = gate.INFO

    # convert str to pathlib
    param.output_folder = pathlib.Path(param.output_folder)

    # units
    m = gate.g4_units("m")
    mm = gate.g4_units("mm")
    Bq = gate.g4_units("Bq")

    # compute largest dimension
    length, max_len = max_length(param.ct_image)
    print(f"Maximum CT length: {max_len / mm} mm")

    # CT phantom
    ct = add_ct_image(sim, param)

    # world size
    world = sim.world
    world.size = [2 * max_len + 0.5 * m, 2 * max_len + 0.5 * m, 2 * max_len + 0.5 * m]
    world.material = "G4_Galactic"

    # cylinder for output phsp
    sph_surface = sim.add_volume("Sphere", "phase_space_sphere")
    sph_surface.rmin = max_len
    sph_surface.rmax = max_len + 1 * mm
    sph_surface.color = [0, 1, 0, 1]
    sph_surface.material = "G4_AIR"

    # physic list
    p = sim.get_physics_user_info()
    p.physics_list_name = "G4EmStandardPhysics_option4"
    sim.set_cut("world", "all", 1 * mm)

    # create a mask source
    mask = create_mask_uniform_source(param.ct_image, param.min_z, param.max_z)
    mask_filename = str(param.output_folder / "source_uniform.mhd")
    itk.imwrite(mask, mask_filename)

    # to compute activity concentration, need the volume
    m = itk.imread(mask_filename)
    info = gate.get_info_from_image(m)
    m = itk.array_view_from_image(m)
    vol = m[m == 1].sum() * np.prod(info.spacing) * 0.001
    print(f"Volume of the activity map: {vol} cc")
    print(f"Total activity            : {param.activity_bq} Bq")
    print(f"Activity concentration    : {param.activity_bq / vol} Bq/cc")

    # add the uniform voxelized source
    source = sim.add_source("Voxels", "source")
    source.mother = ct.name
    source.particle = "gamma"
    source.activity = param.activity_bq * Bq / ui.number_of_threads
    source.image = mask_filename
    source.direction.type = "iso"
    source.energy.type = "spectrum"
    gate.set_source_rad_energy_spectrum(source, param.radionuclide)

    # add stat actor
    stats = sim.add_actor("SimulationStatisticsActor", "Stats")
    stats.track_types_flag = True
    stats.output = param.output_folder / "training_dataset_stats.txt"

    # filter gamma only
    f = sim.add_filter("ParticleFilter", "f")
    f.particle = "gamma"

    # phsp
    phsp = sim.add_actor("PhaseSpaceActor", "phase_space")
    phsp.mother = "phase_space_sphere"
    phsp.attributes = [
        "KineticEnergy",
        "PrePosition",
        "PreDirection",
        "TimeFromBeginOfEvent",  # not needed ; only to test with ideal reconstruction
        # needed for gan_flag
        "EventID",
        "EventKineticEnergy",
        # for conditional :
        "EventPosition",
        "EventDirection",  # is it normalized ?
    ]
    phsp.output = param.output_folder / "training_dataset.root"
    # this option allow to store all events even if absorbed
    phsp.store_absorbed_event = True
    # filter to keep only the gammas
    phsp.filters.append(f)

    return sim


def max_length(ct_filename):
    info = gate.read_image_info(ct_filename)
    length = info.size * info.spacing
    max_len = np.max(length)
    return length, max_len


def add_ct_image(sim, param):
    ui = sim.user_info
    gcm3 = gate.g4_units("g/cm3")
    if ui.visu:
        info = gate.read_image_info(param.ct_image)
        length = info.size * info.spacing
        ct = sim.add_volume("Box", "ct")
        ct.size = length
        ct.material = "G4_AIR"
        ct.color = [0, 0, 1, 1]
    else:
        ct = sim.add_volume("Image", "ct")
        ct.image = param.ct_image
        ct.material = "G4_AIR"  # material used by default
        tol = param.density_tolerance_gcm3 * gcm3
        ct.voxel_materials, materials = gate.HounsfieldUnit_to_material(
            tol, param.table_mat, param.table_density
        )
        if param.verbose:
            print(f"Density tolerance = {gate.g4_best_unit(tol, 'Volumic Mass')}")
            print(f"Nb of materials in the CT : {len(ct.voxel_materials)} materials")
        # ct.dump_label_image = param.output_folder / "labels.mhd"
    return ct


def create_mask_uniform_source(ct_filename, min_z=None, max_z=None):
    # read ct
    img = itk.imread(ct_filename)
    imga = itk.array_view_from_image(img)
    info = gate.get_info_from_image(img)

    # create a same size empty (mask) image
    mask = gate.create_3d_image(info.size, info.spacing, pixel_type="unsigned char")
    mask.SetOrigin(info.origin)
    mask.SetDirection(info.dir)
    maska = itk.array_view_from_image(mask)

    # threshold
    maska[imga > -400] = 1

    # min max slices
    if min_z:
        mins = int((min_z - info.origin[2]) / info.spacing[2])
        maska[0:mins, :, :] = 0
    # min max slices
    if max_z:
        maxs = int((max_z - info.origin[2]) / info.spacing[2])
        maska[maxs:, :, :] = 0

    return mask


def make_arf_training_dataset_simulation(param, sim=None):
    # create the simulation
    if not sim:
        sim = gate.Simulation()

    # main options
    ui = sim.user_info
    ui.g4_verbose = False
    ui.visu = param.visu
    ui.number_of_threads = param.number_of_threads
    ui.verbose_level = gate.INFO

    # convert str to pathlib
    param.output_folder = pathlib.Path(param.output_folder)

    # units
    m = gate.g4_units("m")
    mm = gate.g4_units("mm")
    nm = gate.g4_units("nm")
    cm = gate.g4_units("cm")
    Bq = gate.g4_units("Bq")
    MeV = gate.g4_units("MeV")

    # activity
    activity = param.activity_bq * Bq / ui.number_of_threads
    if ui.visu:
        activity = 1e2 * Bq
        ui.number_of_threads = 1

    # world size
    world = sim.world
    world.size = [1 * m, 1 * m, 1 * m]
    world.material = "G4_Galactic"

    # spect head
    colli_name = gate_spect.get_collimator(param.radionuclide)
    print(f'Collimator : {colli_name}')
    spect = gate_spect.add_ge_nm67_spect_head(
        sim, "spect", collimator_type=colli_name, debug=ui.visu
    )
    crystal_name = f"{spect.name}_crystal"

    # physic list
    p = sim.get_physics_user_info()
    p.physics_list_name = "G4EmStandardPhysics_option4"
    sim.set_cut("world", "all", 1 * mm)

    # detector input plane
    detector_plane = sim.add_volume("Box", "detPlane")
    detector_plane.mother = 'spect'
    detector_plane.size = [57.6 * cm, 44.6 * cm, 1 * nm]
    pos, crystal_distance, psd = gate_spect.get_plane_position_and_distance_to_crystal(
        colli_name
    )
    pos += 1 * nm
    detector_plane.translation = [0, 0, pos]
    detector_plane.material = "G4_Galactic"
    detector_plane.color = [1, 0, 0, 1]

    # source
    s1 = sim.add_source("Generic", "s1")
    s1.particle = "gamma"
    s1.activity = activity
    s1.position.type = "disc"
    s1.position.radius = 57.6 * cm / 4  # divide by 4, arbitrarily
    s1.position.translation = [0, 0, 12 * cm]
    s1.direction.type = "iso"
    s1.energy.type = "range"
    s1.energy.min_energy = 0.01 * MeV
    w, ene = gate.get_rad_energy_spectrum(param.radionuclide)
    s1.energy.max_energy = max(ene) * 1.001
    print(f'Energy spectrum {ene}')
    print(f'Max energy  {s1.energy.max_energy}')
    s1.direction.acceptance_angle.volumes = [detector_plane.name]
    s1.direction.acceptance_angle.intersection_flag = True

    # digitizer
    channels = gate_spect.get_simplified_digitizer_channels_rad(
        'spect', param.radionuclide, scatter_flag=True
    )
    cc = gate_spect.add_digitizer_energy_windows(sim, crystal_name, channels)

    # arf actor for building the training dataset
    arf = sim.add_actor("ARFTrainingDatasetActor", "ARF (training)")
    arf.mother = detector_plane.name
    arf.output = param.output_folder / "arf_training_dataset.root"
    arf.energy_windows_actor = cc.name
    arf.russian_roulette = param.russian_roulette

    # add stat actor
    stats = sim.add_actor("SimulationStatisticsActor", "Stats")
    stats.track_types_flag = True
    stats.output = param.output_folder / "arf_training_dataset_stats.txt"

    return sim
