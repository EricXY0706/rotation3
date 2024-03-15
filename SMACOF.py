from Bio.PDB import PDBParser, Structure, Model
from Bio.PDB.PDBIO import PDBIO
from scipy.spatial.distance import pdist, squareform
from sklearn.manifold import smacof
from tqdm import *
import warnings
import os
import numpy as np

def SMACOF_Interpolation(InputFile1, InputFile2, ReferenceFile, OutputFile, num_frames):
    warnings.filterwarnings('ignore')
    pdb_parser = PDBParser(QUIET=True)
    # Reference Structure
    structure_ref = pdb_parser.get_structure('Reference', ReferenceFile)
    model_ref = structure_ref[0]
    coordinates_ref = np.array([atom.get_coord().tolist() for atom in model_ref.get_atoms()])
    distance_ref = squareform(pdist(coordinates_ref))
    # Original Structure
    structure_start, structure_end = pdb_parser.get_structure('Start', InputFile1), pdb_parser.get_structure('End', InputFile2)
    model_start, model_end = structure_start[0], structure_end[len(structure_end)-1]
    coordinates_start, coordinates_end = np.array([atom.get_coord().tolist() for atom in model_start.get_atoms()]), np.array([atom.get_coord().tolist() for atom in model_end.get_atoms()])
    distance_matrix_start, distance_matrix_end = squareform(pdist(coordinates_start)), squareform(pdist(coordinates_end))
    d = (distance_matrix_end - distance_matrix_start) / (num_frames+1)
    # Model loading and initiation
    coordinates_start_standard = smacof(dissimilarities=distance_ref, n_components=3, metric=True, random_state=42)[0]
    # Intermediate structures computation
    new_structure = Structure.Structure("new_structure")
    for k in tqdm(range(num_frames+2)):
        # Interpolation
        distance_matrix_k = distance_matrix_start + k * d
        # non-classical MDS transformation
        coordinates_k = smacof(dissimilarities=distance_matrix_k, n_components=3, init=coordinates_start_standard, metric=True, random_state=42)[0]
        # New model building
        new_model = Model.Model(k+1)
        for chain in structure_start[0]:
            new_chain = chain.copy()
            new_model.add(new_chain)
        new_structure.add(new_model)
        for atom_index, atom in enumerate(new_structure[k+1].get_atoms()):
            atom.set_coord(coordinates_k[atom_index])
    # Output to file
    open(OutputFile, 'w') if not os.path.exists(OutputFile) else None
    pdb_io = PDBIO()
    pdb_io.set_structure(new_structure)
    pdb_io.save(OutputFile)
    with open(OutputFile, 'r') as output_file:
        original_content = output_file.read()
    new_content = []
    for l in open(InputFile1).readlines():
        if l[:5] == 'MODEL':
            break
        new_content.append(l)
    new_content = ''.join(new_content)+original_content
    with open(OutputFile, 'w') as output_file:
        output_file.write(new_content)