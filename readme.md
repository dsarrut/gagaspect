

This repository provides tools and simulation examples to generate complete SPECT tomographic images using either brute-force Monte Carlo method or GAN-based source.  

There are command line tools to 1) generate training datasets for ARF and GAGA, and 2) perform spect simulation

Data are available here: https://www.creatis.insa-lyon.fr/~dsarrut/gagaspect_data
Can be downloaded with:

    wget -r https://www.creatis.insa-lyon.fr/~dsarrut/gagaspect_data/ -nH --cut-dirs=1


## GARF: training dataset and train the GARF

Generate training dataset for ARF. 1e9 is about 100 MB (15 min with 4 threads).

    ./gagaspect/spect_arf_training_dataset.py  -a 1e9 -t 4 --rad Tc99m
    ./gagaspect/spect_arf_training_dataset.py  -a 5e9 -t 8 --rad Tc99m

    garf_train json/train_arf_v003.json results/run.dyb0u6mp/arf_training_dataset.root pth_Tc99m/arf_Tc99m.pth



## GAGA source : training dataset and train the condGAN

    ./gagaspect/spect_gaga_training_dataset.py json/training_dataset_gaga_v1.json

The coordinate system is the one of Geant4, considering that the ct image is centered. 

The estimated computation time is 6 min with 4 threads for 27 MBq (mac book pro M1, 2022), about 52k PPS.
The output root file is about 2GB.
The phantom is the given CT image in the json parameters file. 
The activity distribution is automatically created with uniform activity in the CT image, for all pixels above a HU threshold value and ranging between two given slice positions (in mm). 
Main parameters in the json file can be changed on the command lines. 

Train the GAN with the training dataset. 

    gaga_train run.vmvmr5rv/training_dataset.root json/train_gaga_v001.json -f pth/

The computation is about 1h45 for 60k epoch (Jean Zay GPU). 



## reference simulation (for validation)

The reference simulation is "brute force", so very long. Using the CT as phantom and a voxelized activity source. In test1, the activity is composed of 4 spheres.  

    ./gagaspect/spect_simulation.py json/test1_gaga_garf.json --nogarf --nogaga -t 4 -a 1e6 -o output

The computation time is about 6k PPS with 1 threads. 

Note that if there are several runs (angles) in a simulation the multithreading is highly inefficient and should **not** be used (because Geant4 synchronize all thread between runs).
