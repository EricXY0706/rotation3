#!/bin/bash

InputFolder="/home/xuyi/morphing/spliceosome_input"
OutputFolder="/home/xuyi/morphing/spliceosome_output_"

if [ ! -d "$InputFolder" ]; then
    echo "given directory not exist: $InputFolder"
    exit 1
fi

if [ ! -d "$OutputFolder" ]; then
	mkdir -p "$OutputFolder"
fi

for file in "$InputFolder"/*; do
    if [ -f "$file" ]; then
		echo "executing $file ..."
        phenix.geometry_minimization $file silent=True write_geo_file=False directory="$OutputFolder" selection="resseq 1840:2085" max_reasonable_bond_distance=200.0
		echo "$file done"
    fi
done

echo "All files executed."