from MDS import MDS_Interpolation
from SMACOF import SMACOF_Interpolation
from tqdm import *

states = ['B_5zwo_A', 'Bact_5gm6_A', 'C_5gmk_A', 'P_5ylz']
exec_types = ['intersection']
for exec_type in exec_types:
    print(f'Now executing {exec_type}')
    for state_id, state in tqdm(enumerate(states[:-1])):
        InputFile1 = rf'/home/xuyi/morphing/text_files/spliceosome_{state}_{exec_type}.pdb'
        InputFile2 = rf'/home/xuyi/morphing/text_files/spliceosome_{states[state_id+1]}_{exec_type}.pdb'
        ReferenceFile = rf'/home/xuyi/morphing/text_files/spliceosome_B_5zwo_A_{exec_type}.pdb'
        OutputFile = rf'/home/xuyi/morphing/text_files/spliceosome_{state}_{states[state_id+1]}_{exec_type}_0308.pdb'
        num_frames = 20
        MDS_Interpolation(InputFile1, InputFile2, ReferenceFile, OutputFile, num_frames)
        # SMACOF_Interpolation(InputFile1, InputFile2, ReferenceFile, OutputFile, num_frames)
    print(f'{exec_type} executed, now merging files...')
