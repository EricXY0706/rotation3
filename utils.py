def change_serial_numbers(input_pdb, output_pdb, new_start_number):
    if input_pdb == output_pdb:
        raise ValueError("The two files can not be the same.")
    else:
        with open(input_pdb, 'r') as infile, open(output_pdb, 'a') as outfile:
            for line in infile:
                if line.startswith("ATOM") or line.startswith("HETATM"):
                    atom_serial = int(line[6:11])
                    new_serial = new_start_number + atom_serial - 1
                    modified_line = f"{line[:6]}{new_serial:5}{line[11:]}"
                    outfile.write(modified_line)
                else:
                    outfile.write(line)
def change_model_serial_number(input_pdb, output_pdb, new_start_number, space_num):
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
def split_model(input_pdb, output_dir, total_num, space_num):
    with open(input_pdb, 'r') as infile:
        headers, lines = [], infile.readlines()
        for line in lines:
            if line.startswith("ATOM") or line.startswith("HETATM"):
                break
            else:
                headers.append(line)
        for model_id in range(1, total_num+1):
            line_id_start = lines.index(f'MODEL{' '*space_num}{model_id}\n')
            line_id_end = lines.index(f'MODEL{' '*space_num}{model_id+1}\n') if model_id != total_num else -1
            model_content = lines[line_id_start:line_id_end]
            total_content = ''.join(headers)+''.join(model_content)
            with open(rf'{output_dir}/{input_pdb.split('/')[-1].split('.')[0]}_model_{model_id}.pdb', 'w') as outfile:
                outfile.write(total_content)
def merge_model(input_dir, output_pdb, total_num):
    