#!/usr/bin/env python

import os
import sys
import argparse


parser = argparse.ArgumentParser()

parser.add_argument("-silent_list", type=str, default="", help="A list of silent files to use as input")

parser.add_argument("-pdb_list", type=str, default="", help="A list of pdbs to use as input")
parser.add_argument("-group_size", type=int, default=-1, help="For pdb_list. How many pdbs per job?")

parser.add_argument("-xml", type=str, default="", help="An xml file to use with rosetta_scripts")
parser.add_argument("-python_script", type=str, default="", help="A python script to run")

parser.add_argument("-flags", type=str, default="", help="Extra flags to pass to the executable")
parser.add_argument("-flags_file", type=str, default="", help="A flags file to pass to the executable")
parser.add_argument("-suffix", type=str, default="", help="A suffix for the run folder")
parser.add_argument("-no_pdb_out", action="store_true", help="When using an xml, only output the score file.")
parser.add_argument("-no_log", action="store_true", help="Don't save the log file.")
parser.add_argument("-rosetta_scripts", type=str, default="$ROSETTA/bin/rosetta_scripts", help="Path to rosetta_scripts")
parser.add_argument("-destination", type=str, default="", help="Make runs in this folder instead.")
parser.add_argument("-cao_2021_protocol", type=str, default="dirname(__file__)", help="Path to cao_2021_protocol/")
parser.add_argument("-ROSETTA_CRASH_HACK", action="store_true", help="Prevents ROSETTA_CRASH.log from being written by creating a folder"
                                                                +" with the same name. Only needed for motif graft and won't be required"
                                                                +" if the current year is 2022 or greater.")

args = parser.parse_args(sys.argv[1:])


if ( args.silent_list and args.pdb_list ):
    sys.exit("You must specify only one of: -silent_list and -pdb_list")

if ( args.xml and args.python_script ):
    sys.exit("You must specify only one of: -xml and -python_script")

if ( args.destination ):
    os.makedirs(args.destination, exist_ok=True)

if ( args.cao_2021_protocol == "dirname(__file__)" ):
    cao_2021_protocol = os.path.realpath(os.path.dirname(__file__))
else:
    cao_2021_protocol = os.path.realpath(args.cao_2021_protocol)

if ( not os.path.exists(cao_2021_protocol) ):
    sys.exit("Path to cao_2021_protocl/ doesn't exist (-cao_2021_protocol). Tried to use: %s"%cao_2021_protocol)


silent_list = None
pdb_list = None

def read_file_list(file):
    my_list = []
    with open(file) as f:
        for line in f:
            line = line.strip()
            if ( len(line) == 0 ):
                continue
            my_list.append(os.path.abspath(line))
    return my_list

if ( args.silent_list ):
    silent_list = read_file_list(args.silent_list)
if ( args.pdb_list ):
    pdb_list = read_file_list(args.pdb_list)
    if ( args.group_size <= 0 ):
        sys.exit("If using -pdb_list, you must specify -group_size")


run_name = os.path.basename( args.xml[:-len(".xml")] + args.python_script[:-len(".py")] )
run_name += args.suffix
if ( args.destination ):
    run_name = os.path.join(args.destination, run_name)

if ( not os.path.exists(run_name) ):
    os.mkdir(run_name)

# https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

pdb_chunks = None
if ( pdb_list ):
    pdb_chunks = list(chunks(pdb_list, args.group_size))

    iterations = len(pdb_chunks)
else:
    iterations = len(silent_list)

commands = []

for i in range(iterations):

    folder = os.path.join(run_name, "%05i"%i)

    if (not os.path.exists(folder)):
        os.mkdir(folder)

    if ( args.ROSETTA_CRASH_HACK ):
        crash_folder = os.path.join(folder, "ROSETTA_CRASH.log")
        if ( not os.path.exists(crash_folder) ):
            os.mkdir(crash_folder)

    if ( pdb_list ):
        with open(os.path.join(folder, "pdb.list"), "w") as f:
            for pdb in pdb_chunks[i]:
                f.write("%s\n"%pdb)

    command = "cd %s; "%os.path.abspath(folder)

    if ( args.xml ):
        command += args.rosetta_scripts 
        command += " -parser:protocol " + os.path.abspath(args.xml) 
        command += " -beta_nov16"

        if ( pdb_list ):
            command += " -l pdb.list"
        else:
            command += " -in:file:silent %s"%(silent_list[i])
            command += " -keep_input_scores False -silent_read_through_errors"

        if ( args.no_pdb_out ):
            command += " -out:file:score_only score.sc"
        else:
            if ( not pdb_list ):
                command += " -out:file:silent out.silent -out:file:silent_struct_type binary"

        # Someday this will be default
        # prevents filters from running twice
        command += " -mute protocols.rosetta_scripts.ParsedProtocol.REPORT"
        command += " -parser:script_vars CAO_2021_PROTOCOL=" + cao_2021_protocol

    else:
        command += os.path.abspath(args.python_script)

        if ( pdb_list ):
            command += " -pdb_list pdb.list"
        else:
            command += " -in:file:silent %s"%(silent_list[i])

    if ( args.flags_file ):
        command += " @%s"%os.path.abspath(args.flags_file)


    command += " " + args.flags

    if ( args.no_log ):
        command += " -mute all > /dev/null"
    else:
        command += " > log.log"

    command += " 2>&1"


    commands.append(command)


with open("%s_commands.list"%run_name, "w") as f:
    for command in commands:
        f.write("%s\n"%command)




