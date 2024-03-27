#!/bin/bash

InputFolder="/home/xuyi/morphing/5yh5_5yh8_20/4-Output-DeepRefine"

if [ ! -d "$InputFolder" ]; then
    echo "given directory not exist: $InputFolder"
    exit 1
fi

for file in "$InputFolder"/*; do
    if [ -f "$file" ]; then
		if [[ $file == *.pdb ]]; then
			filename=$(basename $file)
			echo "executing $filename ..."
			phenix.molprobity $file quiet=False max_reasonable_bond_distance=200.0 probe_dots=False coot=False prefix="$filename"
			echo "$filename done"
		fi
    fi
done

echo "All files executed."