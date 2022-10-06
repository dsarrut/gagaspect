#!/bin/bash
#SBATCH --mem=8000                # memory in MB per default
#SBATCH --output=jobs/Seq%j.out   # job output file
#SBATCH --error=jobs/Seq%j.out    # job err file
#SBATCH --time=12:00:00           # approximated time
#SBATCH --partition=hpc           # (High-Performance Computing)
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1


date
which python
source /pbs/home/d/dsarrut/gagaspect/env/bin/activate
source /pbs/home/d/dsarrut/gagaspect/opengate/preload.sh
mkdir -p jobs
f='/pbs/home/d/dsarrut/gagaspect/results'
cd "$f" || {
  echo "Error, the folder does not exist: $f"
  exit 1
}
mkdir -p jobs
pwd

echo "List of parameters: " "$@"
python "$@"

date
