#!/bin/bash

InputFolder="/home/xuyi/morphing/sodium_Ca_only/3-OriginalMorophing-SplitModels"
OutputFolder="/home/xuyi/morphing/sodium_Ca_only/4-Output-AllMinimized"

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
        sh /home/xuyi/ATOMRefine/refine.sh $file 
		echo "$file done"
    fi
done

echo "All files executed."