import numpy as np
from Bio.PDB import PDBParser
import pandas as pd
def table_formation(InputFiles):
    pdb_parser = PDBParser(QUIET=True)
    structures, tables = [], []
    for structure_id, file in enumerate(InputFiles):
        structures.append(pdb_parser.get_structure('structure'+str(structure_id), file))
    for structure in structures:
        result = []
        for model in structure:
            for chain in model:
                for residue in chain:
                    for atom in residue.get_atoms():
                        result.append([atom.get_serial_number(), atom.get_fullname(), residue.get_resname(), chain.id,
                                       residue.id[1], tuple(atom.get_coord()), atom.get_occupancy(), atom.get_bfactor(),
                                       atom.element])
        df = pd.DataFrame(result)
        df.columns = ['Number', 'Atom', 'Residue', 'Chain', 'Residue_id', 'Coord', 'Occupancy', 'bfactor', 'Element']
        tables.append(df)
    return tables
def intersection(InputFiles):
    tables = table_formation(InputFiles)
    sets, results_tables = [], []
    for df in tables:
        df_set = set()
        for index, row in df.iterrows():
            df_set.add((row.Atom, row.Residue, row.Chain, row.Residue_id, row.Element))
        sets.append(df_set)
    result_set = sets[0]
    for s in sets[1:]:
        result_set = result_set & s
    for df in tables:
        results_tables.append(df[df.apply(lambda row: (row['Atom'], row['Residue'], row['Chain'], row['Residue_id'], row['Element']) in result_set, axis=1)])
    return results_tables
def union(InputFiles):
    result_tables = intersection(InputFiles)
    original_tables = table_formation(InputFiles)
    special_table = pd.DataFrame(columns=original_tables[0].columns)
    for i in range(1, len(original_tables)):
        df_i_diff = original_tables[0][~original_tables[0][['Atom', 'Residue', 'Chain', 'Residue_id', 'Element']].isin(result_tables[0][['Atom', 'Residue', 'Chain', 'Residue_id', 'Element']]).all(axis=1)]
        special_table = pd.concat([special_table, df_i_diff], ignore_index=True)
    special_table.drop_duplicates(inplace=True)
    for i in range(len(result_tables)):
        result_tables[i] = pd.concat([result_tables[i], special_table], ignore_index=True)
        result_tables[i]['Coord'] = result_tables[i]['Coord'].apply(np.array)
    return result_tables
def write_pdb(file_path, table):
    with open(file_path, 'a') as pdb_file:
        for index, row in table.iterrows():
            line = f"ATOM  {row.Number:>5} {row.Atom:<4} {row.Residue:>3} {row.Chain:>1}{row.Residue_id:>4}    {row.Coord[0]:>8.3f}{row.Coord[1]:>8.3f}{row.Coord[2]:>8.3f}{row.Occupancy:>6.2f}{row.bfactor:>6.2f}          {row.Element:>2}\n"
            pdb_file.write(line)
def PDB_formation(InputFiles):
    globals()['tables_intersection'] = intersection(InputFiles)
    globals()['tables_union'] = union(InputFiles)
    exec_types = ['intersection', 'union']
    for exec_type in exec_types:
        tables = globals()['tables_'+exec_type]
        for file_id, file in enumerate(InputFiles):
            file_route = f"{file.split('.')[0]}_{exec_type}.pdb"
            table = tables[file_id]
            write_pdb(file_route, table)
            with open(file_route, 'r') as output_file:
                original_content = output_file.read()
            headers = []
            for l in open(file).readlines():
                if l[:4] == 'ATOM':
                    break
                headers.append(l)
            new_content = ''.join(headers) + original_content
            with open(file_route, 'w') as output_file:
                output_file.write(new_content)
# input_files = [r'/home/xuyi/morphing/test_files/spliceosome_B_5zwo_A.pdb',
#                r'/home/xuyi/morphing/test_files/spliceosome_Bact_5gm6_A.pdb',
#                r'/home/xuyi/morphing/test_files/spliceosome_C_5gmk_A.pdb',
#                r'/home/xuyi/morphing/test_files/spliceosome_P_5ylz.pdb']
# PDB_formation(input_files)