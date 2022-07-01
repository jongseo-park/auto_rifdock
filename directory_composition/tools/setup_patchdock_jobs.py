#!/usr/bin/env python

import sys
import os
from argparse import ArgumentParser

def parse_arguments( argv ):
    argv_tmp = sys.argv
    sys.argv = argv
    description = "setup the patchdock protocol"
    parser = ArgumentParser( description = description )
    parser.add_argument('-target_pdb', type=str, help='the path of the target pdb file.')
    parser.add_argument('-pdb_list', type=str, help='the path of the scaffold pdb file')
    parser.add_argument('-target_res', type=str, help='the path of the target residue list file')
    parser.add_argument('-cluster_rmsd', type=float, default=3.0, help='the path of the target residue list file')
    parser.add_argument('-patchdock', type=str, default="", help='The path to the patchdock folder')
    args = parser.parse_args()
    sys.argv = argv_tmp
    return args

def write_param_file( target_pdb, scaffold_pdb, target_res, cluster_rmsd, patchdock):
    scaff_tag = scaffold_pdb.split('/')[-1].rstrip("gz").rstrip(".").rstrip("pdb").rstrip(".")
    f_out = open(scaff_tag + '.params', 'w')
    f_out.write('receptorPdb ' + target_pdb + '\n')
    f_out.write('ligandPdb ' + scaffold_pdb + '\n')
    f_out.write('protLib %s/chem.lib\n'%patchdock)
    f_out.write('log-file ' + scaff_tag + '.log\n')
    f_out.write('log-level 0\n')
    f_out.write('receptorSeg 10.0 20.0 1.5 1 0 1 0\n')
    f_out.write('ligandSeg 10.0 20.0 1.5 1 0 1 0\n')
    f_out.write('scoreParams 0.3 -5.0 0.5 0.0 0.0 1500 -8 -4 0 1 0\n')
    f_out.write('desolvationParams 500.0 1.0\n')
    f_out.write('clusterParams 0.1 4 2.0 %f\n' % cluster_rmsd)
    f_out.write('baseParams 4.0 13.0 2\n')
    f_out.write('matchingParams 1.5 1.5 0.4 0.5 0.9\n')
    f_out.write('matchAlgorithm 1\n')
    f_out.write('receptorGrid 0.5 6.0 6.0\n')
    f_out.write('ligandGrid 0.5 6.0 6.0\n')
    f_out.write('receptorMs 10.0 1.8\n')
    f_out.write('ligandMs 10.0 1.8\n')
    f_out.write('receptorActiveSite ' + target_res + '\n')

    f_out.close()


def read_file_list(file):
    my_list = []
    with open(file) as f:
        for line in f:
            line = line.strip()
            if ( len(line) == 0 ):
                continue
            my_list.append(os.path.abspath(line))
    return my_list


def main( argv ):
    args = parse_arguments( argv )

    if ( not args.patchdock ):
        sys.exit("You must give the path to the PatchDock folder with -patchdock")

    pdbs = read_file_list( args.pdb_list )

    for pdb in pdbs:
    
        scaff_tag = pdb.split('/')[-1].rstrip("gz").rstrip(".").rstrip("pdb").rstrip(".")

        write_param_file(
            os.path.abspath(args.target_pdb),
            os.path.abspath(pdb),
            os.path.abspath(args.target_res), 
            args.cluster_rmsd, 
            os.path.abspath(args.patchdock)
            )

        print("cd %s; %s/patch_dock.Linux %s.params %s.out" % ( os.getcwd(), os.path.abspath(args.patchdock), scaff_tag, scaff_tag ))






if __name__ == '__main__':
    main( sys.argv )
        
