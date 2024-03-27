'''
1. change_model_serial_numbers:
   Change models serial numbers in a complete PDB file with multiple models
2. change_resi_serial_numbers:
   Change residues serial numbers in a complete PDB file
3. change_atom_serial_numbers:
   Change atoms serial numbers in a complete PDB file
4. modi_model_serial_number:
   Modify model serial number in a series of PDB files
5. add_model_serial_numbers:
   Add model serial number to a series of PDB files
6. choose_specific_resi_interval:
   Choose a certain range of residues in a PDB file
7. split_models:
   Split a PDB file with multiple models to files with models alone
8. merge_models/merge_models_DeepRefine:
   Merge a series of PDB files with models to a complete PDB file
9. add_line:
   Add a certain line to a specific place
10. add_model_name_initially:
   Add "MODEL 1" to a PDB file which is without "MODEL 1" tag
11. make_it_reverse:
   Add models to a PDB file with multiple models to make it smooth when end playing
'''
def change_model_serial_numbers(input_pdb, output_pdb, new_start_number, space_num):
    if input_pdb == output_pdb:
        raise ValueError("The two files can not be the same.")
    else:
        with open(input_pdb, 'r') as infile, open(output_pdb, 'a') as outfile:
            for line in infile:
                if line.startswith("MODEL"):
                    modified_line = f"{line.split(' ')[0]}{' '*space_num}{new_start_number}\n"
                    new_start_number += 1
                    outfile.write(modified_line)
                else:
                    outfile.write(line)
def change_resi_serial_numbers(input_pdb, output_pdb, new_start_number, original_start_number):
    if input_pdb == output_pdb:
        raise ValueError("The two files can not be the same.")
    else:
        with open(input_pdb, 'r') as infile, open(output_pdb, 'w') as outfile:
            for line in infile:
                if line.startswith("ATOM") or line.startswith("HETATM"):
                    atom_serial = int(line[6:11])
                    residue_serial = int(line[22:26])
                    new_serial = new_start_number + residue_serial - original_start_number
                    modified_line = f"{line[:6]}{atom_serial:5}{line[11:22]}{new_serial:4}{line[26:]}"
                    outfile.write(modified_line)
                else:
                    outfile.write(line)
def change_atom_serial_numbers(input_pdb, output_pdb, new_start_number, original_start_number):
    if input_pdb == output_pdb:
        raise ValueError("The two files can not be the same.")
    else:
        with open(input_pdb, 'r') as infile, open(output_pdb, 'a') as outfile:
            for line in infile:
                if line.startswith("ATOM") or line.startswith("HETATM"):
                    atom_serial = int(line[6:11])
                    new_serial = new_start_number + atom_serial - original_start_number
                    modified_line = f"{line[:6]}{new_serial:5}{line[11:]}"
                    outfile.write(modified_line)
                else:
                    outfile.write(line)
def modi_model_serial_number(input_dir, models_prefix, total_number, space_num):
    total_number, space_num = int(total_number), int(space_num)
    for model_id in range(1, total_number+1):
        f = open(rf'{input_dir}/{models_prefix}_{model_id}_minimized.pdb')
        lines = f.readlines()
        new_content = []
        for line in lines:
            if line.startswith("MODEL"):
                new_content.append(f'MODEL{' '*space_num}{model_id}\n')
            else:
                new_content.append(line)
        with open(rf'{input_dir}/{models_prefix}_{model_id}_minimized.pdb', 'w') as outfile:
            outfile.write(''.join(new_content))
def add_model_serial_numbers(input_dir, output_dir, model_prefix, total_num, space_num):
    for model_id in range(1, total_num+1):
        f = open(rf'{input_dir}/{model_prefix}_model_{model_id}_minimized.pdb')
        lines = f.readlines()
        model_start_id = 0
        for line_id, line in enumerate(lines):
            if line.startswith("ATOM") or line.startswith("HETATM"):
                model_start_id = line_id
                break
        new_content = lines[:model_start_id] + [f'MODEL{' '*space_num}{model_id}\n'] + lines[model_start_id:]
        with open(rf'{output_dir}/{model_prefix}_model_{model_id}_minimized.pdb', 'w') as outfile:
            outfile.write(''.join(new_content))
def choose_specific_resi_interval(input_pdb, output_pdb, start_number, end_number):
    if input_pdb == output_pdb:
        raise ValueError("The two files can not be the same.")
    else:
        with open(input_pdb, 'r') as infile, open(output_pdb, 'a') as outfile:
            for line in infile:
                if not (line.startswith("ATOM") or line.startswith("HETATM")):
                    outfile.write(line)
                else:
                    if start_number <= int(line[22:26].strip(' ')) <= end_number:
                        outfile.write(line)
                    else:
                        pass
def split_models(input_pdb, output_dir, total_num, space_num):
    with open(input_pdb, 'r') as infile:
        headers, lines = [], infile.readlines()
        for line in lines:
            if line.startswith("MODEL"):
                break
            else:
                headers.append(line)
        total_num, space_num = int(total_num), int(space_num)
        for model_id in range(1, total_num+1):
            line_id_start = lines.index(f'MODEL{' '*space_num}{model_id}\n')
            line_id_end = lines.index(f'MODEL{' '*space_num}{model_id+1}\n') if model_id != total_num else -1
            model_content = lines[line_id_start:line_id_end]
            total_content = ''.join(headers) + ''.join(model_content)
            with open(rf'{output_dir}/{input_pdb.split('/')[-1].split('.')[0]}_{model_id}.pdb', 'w') as outfile:
                outfile.write(total_content)
def merge_models(input_dir, models_prefix, output_pdb, total_num, space_num):
    model_start_index = -1
    with open(rf'{input_dir}/{models_prefix}_1_minimized.pdb', 'r') as infile:
        headers, lines = [], infile.readlines()
        for line in lines:
            model_start_index += 1
            if line.startswith("ATOM"):
                break
            else:
                headers.append(line)
    model_content = []
    total_num, space_num = int(total_num), int(space_num)
    for model_id in range(1, total_num+1):
        lines = open(rf'{input_dir}/{models_prefix}_{model_id}_minimized.pdb').readlines()
        model_content.append(f"MODEL{' '*space_num}{model_id}\n")
        model_content.extend(lines[model_start_index:-1])
        model_content.append("ENDMDL\n")
    model_content.append("END\n")
    total_content = ''.join(headers) + ''.join(model_content)
    with open(output_pdb, 'w') as outfile:
        outfile.write(total_content)
def merge_models_DeepRefine(input_dir, models_prefix, output_pdb, total_num, space_num):
    modi_model_serial_number(input_dir, models_prefix, total_num, space_num)
    model_start_index = -1
    with open(rf'{input_dir}/{models_prefix}_1_minimized.pdb', 'r') as infile:
        headers, lines = [], infile.readlines()
        for line in lines:
            model_start_index += 1
            if line.startswith("MODEL"):
                break
            else:
                headers.append(line)
    model_content = []
    total_num, space_num = int(total_num), int(space_num)
    for model_id in range(1, total_num+1):
        lines = open(rf'{input_dir}/{models_prefix}_{model_id}_minimized.pdb').readlines()
        # model_content.append(f"MODEL{' '*space_num}{model_id}\n")
        model_content.extend(lines[model_start_index:-1])
        # model_content.append("ENDMDL\n")
    model_content.append("END\n")
    total_content = ''.join(headers) + ''.join(model_content)
    with open(output_pdb, 'w') as outfile:
        outfile.write(total_content)
def add_line(input_dir, output_dir, models_prefix, content, line_id, total_num):
    for model_id in range(1, total_num+1):
        with open(rf'{input_dir}/{models_prefix}_{model_id}_minimized.pdb', 'r') as infile:
            lines = infile.readlines()
            if line_id < len(lines) and line_id != -1:
                lines.insert(line_id, content)
            elif line_id == len(lines) or line_id == -1:
                lines.append(content)
            else:
                raise ValueError("Insertion line id exceeds.")
            with open(rf'{output_dir}/{models_prefix}_{model_id}_minimized.pdb', 'w') as outfile:
                outfile.write(''.join(lines))
def add_model_name_initially(input_pdb, space_num):
    file = open(input_pdb, 'r')
    headers, lines = [], file.readlines()
    line_id = -1
    for line in lines:
        line_id += 1
        if line.startswith("ATOM"):
            break
        else:
            headers.append(line)
    space_num = int(space_num)
    headers.append(f'MODEL{' '*space_num}1\n')
    models = lines[line_id:]
    new_content = ''.join(headers) + ''.join(models)
    with open(input_pdb, 'w') as outfile:
        outfile.write(new_content)
def make_it_reverse(input_pdb, output_pdb, total_num, space_num):
    infile = open(rf'{input_pdb}')
    lines = infile.readlines()[:-1]
    result = lines
    for model_id in range(total_num-1, 0, -1):
        model_start_id = lines.index(f'MODEL{' '*space_num}{model_id}\n')
        model_end_id = lines.index(f'MODEL{' '*space_num}{model_id+1}\n')
        model_content = lines[model_start_id+1:model_end_id]
        result.append(f'MODEL{' '*space_num}{2*total_num-model_id}\n')
        result.extend(model_content)
    result.append("END\n")
    with open(rf'{output_pdb}', 'w') as outfile:
        outfile.write(''.join(result))
