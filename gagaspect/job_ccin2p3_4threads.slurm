#!/bin/bash
#SBATCH --mem=4000                # memory in MB per default
#SBATCH --output=jobs/Seq%j.out   # job output file
#SBATCH --cpus-per-task=4
#SBATCH --error=jobs/Seq%j.out    # job err file
#SBATCH --time=06:00:00           # approximated time

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
