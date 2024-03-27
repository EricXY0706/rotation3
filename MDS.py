from Bio.PDB import PDBParser, Structure, Model
from Bio.PDB.PDBIO import PDBIO
from scipy.spatial.distance import pdist, squareform
from sklearn.manifold import MDS
from tqdm import *
import warnings
import os
import numpy as np
from joblib import Parallel, delayed

def compute_mds(data, n_components, random_state, corrd_init):
    warnings.filterwarnings('ignore')
    model = MDS(n_components=n_components, metric=True, random_state=random_state, dissimilarity="precomputed")
    return model.fit_transform(data, init=corrd_init)
def MDS_Interpolation(InputFile1, InputFile2, ReferenceFile, OutputFile, num_frames):
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
    model = MDS(n_components=3, metric=True, random_state=42, dissimilarity="precomputed")
    coordinates_start_standard = model.fit_transform(distance_ref)
    # Intermediate structures computation
    new_structure = Structure.Structure("new_structure")
    # Interpolation
    matrix = []
    for k in tqdm(range(num_frames+2)):
        distance_matrix_k = distance_matrix_start + k * d
        matrix.append(distance_matrix_k)
    # MDS transformation
    results = Parallel(n_jobs=-1)(delayed(compute_mds)(data, 3, 42, coordinates_start_standard) for data in tqdm(matrix))
    for k, coordinates_k in enumerate(results):
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

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 6:
        print("Usage: python MDS.py <InputFile1> <InputFile2> <ReferenceFile> <OutputFile> <frames>")
        sys.exit(1)

    infile1 = sys.argv[1]
    infile2 = sys.argv[2]
    ref_file = sys.argv[3]
    outfile = sys.argv[4]
    frames = int(sys.argv[5])

    MDS_Interpolation(infile1, infile2, ref_file, outfile, frames)