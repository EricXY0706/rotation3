from Bio.PDB import PDBParser, Structure, Model
from Bio.PDB.PDBIO import PDBIO
from scipy.spatial.distance import pdist, squareform
from sklearn.manifold import MDS
from tqdm import *
import warnings
import os
import numpy as np
from joblib import Parallel, delayed

def MDS_Interpolation(InputFile1, InputFile2, ReferenceFile, OutputFile, num_frames):
    warnings.filterwarnings('ignore')
    pdb_parser = PDBParser(QUIET=True)
    # Reference Structure
    structure_ref = pdb_parser.get_structure('Reference', ReferenceFile)
    model_ref = structure_ref[0]
    coordinates_ref = np.array([atom.get_coord().tolist() for atom in model_ref.get_atoms()])
    print(coordinates_ref.shape,
          coordinates_ref[0, :])
MDS_Interpolation(1, 1, r'D:\Xuyi\THU\1_Science\rotation3\test_files\spliceosome_Bact_5gm6_A_intersection.pdb',
                  1, 1)