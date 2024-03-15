with open(r'/home/xuyi/morphing/ideal_files/Sodium-dependent_neutral_amino_acid_transporter_6M18_6M17_MDS_30_copy.pdb', 'r') as infile:
    lines = infile.readlines()
    ls = []
    for l in lines:
        print(l)
        if l.startswith("MODEL"):
            ls.append(l)
    print(lines)
    print(lines.index(ls[0]))