import pandas as pd
import os
def mol_score(input_dir, minimization_state, file_prefix, total_num):
    scores = []
    total_num = int(total_num)
    for file_id in range(1, total_num+1):
        file = open(rf'{input_dir}/{minimization_state}/{file_prefix}_{file_id}_minimized.pdb.out') if minimization_state.startswith('after_minimization') \
            else open(rf'{input_dir}/{minimization_state}/{file_prefix}_{file_id}.pdb.out')
        lines = file.readlines()
        start_line_id = lines.index('=================================== Summary ===================================\n')
        infos = lines[start_line_id+2:] if minimization_state == 'after_minimization_phenix' else lines[start_line_id+2:-4]
        score = [file_id]
        for info in infos:
            info = info.replace(' ', '').replace('\n', '').split('=')
            score.append(info[1])
        scores.append(score)
    df = pd.DataFrame(scores)
    df.columns = ['ModelID', 'RamachandranOutliers', 'favored', 'RotamerOutliers', 'C-betaDeviations', 'ClashScore', 
                  'RMS(bonds)', 'RMS(angles)', 'MolProbityscore']
    os.mkdir(rf'{input_dir}/molprobity_result') if not os.path.exists(rf'{input_dir}/molprobity_result') else None
    df.to_csv(rf'{input_dir}/molprobity_result/{file_prefix}_{minimization_state}.csv', index=False)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 5:
        print("Usage: python molprobity.py <input_dir> <minimization_state> <file_prefix> <frames>")
        sys.exit(1)

    input_dir = sys.argv[1]
    minimization_state = sys.argv[2]
    file_prefix = sys.argv[3]
    frames = sys.argv[4]

    mol_score(input_dir, minimization_state, file_prefix, frames)