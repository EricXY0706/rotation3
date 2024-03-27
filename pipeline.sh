#!/bin/sh

# Help message
SCRIPT_NAME="Morphing Computation Pipeline"
SCRIPT_DESCRIPTION="This script performs morphing computation of two conformations with given parameters."
usage() {
  echo
  echo "Usage: $SCRIPT_NAME"
  echo
  echo "Description:"
  echo "$SCRIPT_DESCRIPTION"
  echo
  echo "Options:"
  echo "-pdb1 <PDB1>        Specify the PDB file for the first conformation."
  echo "-pdb2 <PDB2>        Specify the PDB file for the last conformation."
  echo "-type <TYPE>        Specify the type of operation to the input PDB files (intersection or union)."
  echo "-frames <FRAMES>    Specify the number of frames for morphing."
  echo "-workers <WORKERS>" Specify the number of CPU to be used 
  echo "-h                  Show this help message."
  echo "--help              Show this help message."
  echo
  echo "Example: bash morphing.sh file1.pdb file2.pdb intersection 20 48"
}

if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    usage
    exit 0
fi

# Config
pdb1="4eq7_copy"
pdb2="4euo_copy"
type="intersection"
frames=0
workers=48
total_num=$((frames+2))
pdb_space_num=6
sh_path=$(pwd)
basicpath=/home/xuyi/morphing/"${pdb1}_${pdb2}_${frames}"

# Making Directories
mkdir -p ${basicpath}/0-Input
mkdir -p ${basicpath}/1-IntersectionUnion
mkdir -p ${basicpath}/2-OriginalMorphing
mkdir -p ${basicpath}/3-OriginalMorphing-SplitModels
mkdir -p ${basicpath}/4-Output-Phenix
mkdir -p ${basicpath}/4-Output-DeepRefine
mkdir -p ${basicpath}/5-FinalOutput
mkdir -p ${basicpath}/6-Molprobity
mkdir -p ${basicpath}/6-Molprobity/after_minimization_phenix
mkdir -p ${basicpath}/6-Molprobity/after_minimization_DeepRefine
mkdir -p ${basicpath}/6-Molprobity/before_minimization
mkdir -p ${basicpath}/6-Molprobity/molprobity_result

# Input
file1=${basicpath}/0-Input/"${pdb1}.pdb"
file2=${basicpath}/0-Input/"${pdb2}.pdb"
cp ./"${pdb1}.pdb" $file1
cp ./"${pdb2}.pdb" $file2
python -c "from utils import add_model_name_initially; add_model_name_initially('${file1}', ${pdb_space_num})"
python -c "from utils import add_model_name_initially; add_model_name_initially('${file2}', ${pdb_space_num})"

# Intersection & Union
python coord_process.py ${basicpath}/0-Input/"${pdb1}.pdb" ${basicpath}/0-Input/"${pdb2}.pdb"
mv ${basicpath}/0-Input/"${pdb1}_intersection.pdb" ${basicpath}/1-IntersectionUnion/"${pdb1}_intersection.pdb"
mv ${basicpath}/0-Input/"${pdb2}_intersection.pdb" ${basicpath}/1-IntersectionUnion/"${pdb2}_intersection.pdb"
mv ${basicpath}/0-Input/"${pdb1}_union.pdb" ${basicpath}/1-IntersectionUnion/"${pdb1}_union.pdb"
mv ${basicpath}/0-Input/"${pdb2}_union.pdb" ${basicpath}/1-IntersectionUnion/"${pdb2}_union.pdb"

# Original Morphing
InputFile1=${basicpath}/1-IntersectionUnion/"${pdb1}_${type}.pdb"
InputFile2=${basicpath}/1-IntersectionUnion/"${pdb2}_${type}.pdb"
ReferenceFile=${basicpath}/1-IntersectionUnion/"${pdb1}_${type}.pdb"
OutFile=${basicpath}/2-OriginalMorphing/"${pdb1}_${pdb2}_${type}_MDS_${frames}.pdb"
python MDS.py $InputFile1 $InputFile2 $ReferenceFile $OutFile $frames

# SplitModels
input_pdb=${basicpath}/2-OriginalMorphing/"${pdb1}_${pdb2}_${type}_MDS_${frames}.pdb"
output_dir=${basicpath}/3-OriginalMorphing-SplitModels
python -c "from utils import split_models; split_models('${input_pdb}', '${output_dir}', '${total_num}', '${pdb_space_num}')"

# Minimization-Phenix
InputFolder=${basicpath}/3-OriginalMorphing-SplitModels
OutputFolder=${basicpath}/4-Output-Phenix
for file in "$InputFolder"/*; do
    if [ -f "$file" ]; then
        echo "executing $file ..."
        phenix.geometry_minimization $file silent=True write_geo_file=False directory="$OutputFolder" selection=all max_reasonable_bond_distance=50.0 allow_polymer_cross_special_position=True
        echo "$file done"
    fi
done
echo "Minimization: all files executed."

# Minimization-DeepRefine
source activate DeepRefine
cd /home/xuyi/morphing/DeepRefine
DR_DIR=$(pwd)
cd "$DR_DIR"/project
ckpt_dir="$DR_DIR"/project/checkpoints/EGR_All_Atom_Models
ckpt_name=LitPSR_EGR_AllAtomModel1_Seed42.ckpt
atom_selection_type=all_atom
seed=42
nn_type=EGR
graph_return_format=dgl
InputFolder=${basicpath}/3-OriginalMorphing-SplitModels
OutputFolder=${basicpath}/4-Output-DeepRefine/
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
python3 lit_model_predict.py --perform_pos_refinement --device_type gpu --num_devices 1 --num_compute_nodes 1 --num_workers 1 --batch_size 1 --input_dataset_dir "$DR_DIR"/project/datasets/Input/ --output_dir ${OutputFolder} --ckpt_dir "$ckpt_dir" --ckpt_name "$ckpt_name" --atom_selection_type "$atom_selection_type" --seed "$seed" --nn_type "$nn_type" --graph_return_format "$graph_return_format"
for folder in "$OutputFolder"/*; do
	if [ -r "$folder" ]; then
		filename=$(basename $folder)
		cd "${OutputFolder}/${filename}"
		cp "${filename}_refined.pdb" "${basicpath}/4-Output-DeepRefine/${filename}_minimized.pdb"
		cd ..
		rm -r "$DR_DIR"/project/datasets/Input/${filename}
		rm -r "${OutputFolder}/${filename}"
	fi
done
conda deactivate

# MergeModels
cd ${sh_path}
input_dir=${basicpath}/4-Output-Phenix
models_prefix="${pdb1}_${pdb2}_${type}_MDS_${frames}"
output_pdb=${basicpath}/5-FinalOutput/"${pdb1}_${pdb2}_${type}_MDS_${frames}_miniminzed_phenix.pdb"
python -c "from utils import merge_models; merge_models('${input_dir}', '${models_prefix}', '${output_pdb}', '${total_num}', '${pdb_space_num}')"

input_dir=${basicpath}/4-Output-DeepRefine
models_prefix="${pdb1}_${pdb2}_${type}_MDS_${frames}"
output_pdb=${basicpath}/5-FinalOutput/"${pdb1}_${pdb2}_${type}_MDS_${frames}_miniminzed_DeepRefine.pdb"
python -c "from utils import merge_models_DeepRefine; merge_models_DeepRefine('${input_dir}', '${models_prefix}', '${output_pdb}', '${total_num}', '8')"

# Molprobity
cd ${sh_path}
InputFolder1=${basicpath}/3-OriginalMorphing-SplitModels
for file in "$InputFolder1"/*; do
    if [ -f "$file" ]; then
        if [[ $file == *.pdb ]]; then
            filename=$(basename $file)
            echo "executing $filename ..."
            phenix.molprobity $file quiet=False max_reasonable_bond_distance=50.0 probe_dots=False coot=False prefix="$filename"
            echo "$filename done"
            mv ./"${filename}.out" ${basicpath}/6-Molprobity/before_minimization/"${filename}.out"
        fi
    fi
done
echo "Molprobity: before minimization, all files executed."
python molprobity.py "${basicpath}/6-Molprobity" "before_minimization" "${pdb1}_${pdb2}_${type}_MDS_${frames}" ${total_num}

InputFolder2=${basicpath}/4-Output-Phenix
for file in "$InputFolder2"/*; do
    if [ -f "$file" ]; then
        if [[ $file == *.pdb ]]; then
            filename=$(basename $file)
            echo "executing $filename ..."
            phenix.molprobity $file quiet=False max_reasonable_bond_distance=50.0 allow_polymer_cross_special_position=True probe_dots=False coot=False prefix="${filename}_phenix"
            echo "$filename done"
            mv ./"${filename}_phenix.out" ${basicpath}/6-Molprobity/after_minimization_phenix/"${filename}.out"
        fi
    fi
done
echo "Molprobity: after Phenix minimization, all files executed."
python molprobity.py "${basicpath}/6-Molprobity" "after_minimization_phenix" "${pdb1}_${pdb2}_${type}_MDS_${frames}" ${total_num}

InputFolder3=${basicpath}/4-Output-DeepRefine
for file in "$InputFolder3"/*; do
    if [ -f "$file" ]; then
        if [[ $file == *.pdb ]]; then
            filename=$(basename $file)
            echo "executing $filename ..."
            phenix.molprobity $file quiet=False max_reasonable_bond_distance=50.0 allow_polymer_cross_special_position=True probe_dots=False coot=False prefix="${filename}_DeepRefine"
            echo "$filename done"
            mv ./"${filename}_DeepRefine.out" ${basicpath}/6-Molprobity/after_minimization_DeepRefine/"${filename}.out"
        fi
    fi
done
echo "Molprobity: after Phenix minimization, all files executed."
python molprobity.py "${basicpath}/6-Molprobity" "after_minimization_DeepRefine" "${pdb1}_${pdb2}_${type}_MDS_${frames}" ${total_num}

echo
echo "Pipeline finished!"