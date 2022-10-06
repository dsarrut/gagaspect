

This repository provides tools and simulation examples to generate complete SPECT tomographic images using either brute-force Monte Carlo method or GAN-based source.  

## GARF: training dataset and train the GARF

Generate training dataset for ARF. 1e9 is about 100 MB (15 min with 4 threads).

    ./gagaspect/spect_arf_training_dataset.py  -a 1e9 -t 4 --rad Tc99m
    ./gagaspect/spect_arf_training_dataset.py  -a 5e9 -t 8 --rad Tc99m

    garf_train json/train_arf_v003.json results/run.h6r2svwa/arf_training_dataset.root pth/arf_Tc99m.pth


## GAGA source : training dataset and train the condGAN

    ./gagaspect/spect_gaga_training_dataset.py json/training_dataset_gaga_v1.json

The coordinate system is the one of Geant4, considering that the ct image is centered. 

The estimated computation time is 6 min with 4 threads for 27 MBq (mac book pro M1, 2022), about 52k PPS.
The output root file is about 2GB.
The phantom is the given CT image in the json parameters file. 
The activity distribution is automatically created with uniform activity in the CT image, for all pixels above a HU threshold value and ranging between two given slice positions (in mm). 
Main parameters in the json file can be changed on the command lines. 

Train the GAN with the training dataset. 

    gaga_train run.zd7y4brp/training_dataset.root json/train_gaga_v001.json -f pth/

The computation is about 1h45 for 60k epoch (Jean Zay GPU). 

## reference simulation (for validation)

The reference simulation is "brute force", so very long. Using the CT as phantom and a voxelized activity source. In test1, the activity is composed of 2 spheres.  

    ./gagaspect/spect_simulation.py json/ref_test1.json -o output

The computation time is about 53k PPS with 4 threads (mac book pro M1, 2022). Note that if there are several runs (angles) in a simulation the multithreading is highly inefficient and should **not** be used (because Geant4 synchronize all thread between runs).



### Using the ccin2p3 cluster

1. install software : opengate + gatetools + gagaspect repositories. Activate with python env. 
2. rsync the data with `./scripts/to_ccin2p3.sh`
3. use the submit_job script to create folder + list of sbatch commands to submit jobs

With the ccin2p3 cluster, there is a script `submit_jobs_spect_rotation3.py` to submit several jobs that perform a complete rotation. Multithreading is **not** recommended here because each simulation considers several runs. 

    ./scripts/to_ccin2p3.sh
    ./gagaspect/submit_jobs_spect_rotation.py -n 200 -j json/ref_test4.json
    ./results/run.gtvghxki/submit.sh

Once completed, all job results should be merged. The merge process 

    ./gagaspect/merge_projections.py results/run.gtvghxki

### reconstruction 

    cd results/run.gtvghxki

    ~/src/itk/build-v5.2.1-rtk.save/bin/rtksimulatedgeometry -o geom_120.xml -f 0 -n 120 -a 360 --sdd 0 --sid 410 --proj_iso_x -280.54681 --proj_iso_y -280.54681
    
    ~/src/itk/build-v5.2.1-rtk.save/bin/rtkosem -v -g geom_120.xml -o recon_i3s10.mhd --niterations 3 --nprojpersubset 10 --betaregularization 0 --path . --regexp projections.mhd --like ../../data/four_spheres.mhd -f Zeng -b Zeng --sigmazero 0.9 --alphapsf 0.025

    ../../gagaspect/recon_coord_system.py recon_i3s10.mhd --ct ../../data/291_CT_4mm.mhd -o recon_i3s10_s.mhd --tr 0 0 150

