import os
import argparse


parser = argparse.ArgumentParser (description='Script for designing protein binder')

parser.add_argument('--residues', required=True, type=str, default='1-10', help='path to binders')


args = parser.parse_args()




residues = args.residues

ls = residues.split('+')

for i in ls:
    i = i.split('-')
    # print(i)
    with open ('res.list', 'a') as file:
        if len(i) == 1:
            a = int(i[0])
            file.write(str(a) + '\n')

        else:
            a = int(i[0])
            b = int(i[1]) + 1
            for i in range (a, b):
                file.write(str(i) + '\n')         

print ('done')