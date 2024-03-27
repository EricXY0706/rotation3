#!/bin/bash

InputFolder="/home/xuyi/morphing/5yh5_5yh8_20/3-OriginalMorphing-SplitModels"
OutputFolder="/home/xuyi/morphing/5yh5_5yh8_20/4-Output-GNNRefined/"

cd /home/xuyi/morphing/GNNRefine-master/GNNRefine-master/code
for file in "$InputFolder"/*; do
    if [ -f "$file" ]; then
		echo "executing $file ..."
        python GNNRefine.py $file $OutputFolder
		echo "$file done"
    fi
done

echo "All files executed."