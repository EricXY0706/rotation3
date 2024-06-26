#!/bin/bash

cd /home/xuyi/morphing/DeepRefine
DR_DIR=$(pwd)
cd "$DR_DIR"/project
ckpt_dir="$DR_DIR"/project/checkpoints/SEGNN_Ca_Atom_Models
ckpt_name=LitPSR_SEGNN_CaAtomModel_Seed42.ckpt
atom_selection_type=ca_atom
seed=42
nn_type=SEGNN
graph_return_format=pyg

InputFolder="/home/xuyi/morphing/sodium_Ca_only/3-OriginalMorophing-SplitModels"
for file in "$InputFolder"/*; do
    if [ -f "$file" ]; then
		if [[ $file == *.pdb ]]; then
			filename=$(basename $file)
			filename=${filename%.*}
			mkdir -p "$DR_DIR"/project/datasets/Input/${filename}
			cp $file "$DR_DIR"/project/datasets/Input/${filename}/"${filename}.pdb"
		fi
    fi
done

python3 lit_model_predict.py --perform_pos_refinement --device_type gpu --num_devices 1 --num_compute_nodes 1 --num_workers 1 --batch_size 1 --input_dataset_dir /home/xuyi/morphing/DeepRefine/project/datasets/Input/ --output_dir /home/xuyi/morphing/sodium_Ca_only/4-Output-DeepRefine --ckpt_dir "$ckpt_dir" --ckpt_name "$ckpt_name" --atom_selection_type "$atom_selection_type" --seed "$seed" --nn_type "$nn_type" --graph_return_format "$graph_return_format"			
echo "All files executed."

Folder="/home/xuyi/morphing/sodium_Ca_only/4-Output-DeepRefine"
for f in "$Folder"/*; do
	if [ -r "$f" ]; then
		filename=$(basename $f)
		cd "${Folder}/${filename}"
		mv "${filename}_refined.pdb" /home/xuyi/morphing/sodium_Ca_only/4-Output-DeepRefine
		cd ..
		rm -r  "${Folder}/${filename}"
	fi
done