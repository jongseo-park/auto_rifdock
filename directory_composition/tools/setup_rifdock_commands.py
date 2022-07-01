#!/usr/bin/env python

import os
import sys



scaffolds_file = sys.argv[1]
patchdock_xforms = sys.argv[2]
rifdock_flags = sys.argv[3]
rif_dock_test = sys.argv[4]

groups_of = 40

if ( not os.path.exists("rifdock_logs") ):
    os.mkdir("rifdock_logs")


scaffolds = []
with open(scaffolds_file) as f:
    for line in f:
        line = line.strip()
        if (len(line) == 0):
            continue

        scaffolds.append(line)


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

scaffold_chunks = chunks(scaffolds, groups_of)

commands = []

for i, scaffs in enumerate(scaffold_chunks):
    command = "cd %s; "%os.getcwd()

    command += "%s @%s "%(os.path.abspath(rif_dock_test), os.path.abspath(rifdock_flags))

    command += "-scaffolds %s"%(" ".join(os.path.abspath(x) for x in scaffs))

    command += " -seeding_pos"
    for scaff in scaffs:
        tag = os.path.basename(scaff)
        if ( tag.endswith(".gz") ):
            tag = tag[:-len(".gz")]
        if ( tag.endswith(".pdb")):
            tag = tag[:-len(".pdb")]

        polyV_name = tag + "_0001"
        patchdock_file = os.path.join(os.path.abspath(patchdock_xforms), "%s.out"%polyV_name)

        command += " " + patchdock_file

    command += " > rifdock_logs/log%03i.log 2>&1"%i

    commands.append(command)


with open("rifdock_commands.list", "w") as f:
    f.write("\n".join(commands))
    f.write("\n")

    




