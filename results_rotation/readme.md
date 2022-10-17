

# dataset for a complete rotation 

    ./gagaspect/spect_simulation.py json/test2_gaga_garf_rotation.json -a 3e9 -t 1

run.qe2meo21
Obtained with 30 angles, 4 heads, 1 thread, 3e9 events, 5 hours (linux), with both gaga and garf. 

The final 4 images corresponds to the 4 heads, with 3 energy windows and 30 angles. They can be merged into on image per energy windows. 

    split_spect_projections ref_projection_?.mhd -o proj.mhd -e 3

There are 3 energy windows : 1) entire spectrum, 2) scatter, 3) peak


# steps for a simple reconstruction 

    cd results_rotation/run.qe2meo21/

## Step1 : generate a RTK geometry file

    rtksimulatedgeometry -o geom_120.xml -f 0 -n 120 -a 360 --sdd 0 --sid 410

The value for sid does really play a role (parallel geometry)

## Step 2 : reconstruction

A fast reconstruction can be done with: 

    rtkosem -v -g geom_120.xml -o recon_i3s10.mhd --niterations 3 --nprojpersubset 10 --path . --regexp proj_2.mhd --like ../../data/five_aligned_sources.mhd

## Step 3: 

Rotate the image (like in gate) and move the spect. FIXME still small offset !!!!

    ../../gagaspect/recon_coord_system.py recon_i3s10.mhd -o recon_i3s10_rot.mhd --ct ../../data/five_aligned_sources.mhd --tr 0 47.875 150


# Better reconstruction with corrections 

A slower one (with regularization)

    rtkosem -v -g geom_120.xml -o recon_i3s10_zeng.mhd --niterations 3 --nprojpersubset 10 --path . --regexp proj_2.mhd --like ../../data/five_aligned_sources.mhd -f Zeng -b Zeng --sigmazero 0.9 --alphapsf 0.025


