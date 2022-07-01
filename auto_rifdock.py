import os
import argparse
from multiprocessing import Pool

parser = argparse.ArgumentParser (description='Script for designing protein binder')

parser.add_argument('--binderdir', required=False, type=str, default='./binders/', help='path to binders')
parser.add_argument('--template', required=False, type=str, default='./input/template.pdb', help='path to template file')
parser.add_argument('--phobics', required=False, type=int, default=3, help='Number of hydrophobic residues in the interface')
parser.add_argument('--patchdock', required=False, type=str, default='/opt/PatchDock/', help='path to patchdock')
parser.add_argument('--sitelist', required=False, type=str, default='./input/site.list', help='path to template file')

parser.add_argument('--np', required=False, type=int, default=8, help='num_cores')



args = parser.parse_args()



def rifgen(template=args.template, sitelist=args.sitelist):

    rifgen_flag=f"""################### File I/O flags ######################################
-rifgen:target  {template}
-rifgen:target_res  {sitelist}

-rifgen:outdir rifgen_output
-rifgen:outfile rif_64_output_sca0.8_noKR.rif.gz



# Path to the rosetta database for the Rosetta you linked rifdock against
-database /home/rosetta_src_2018.09.60072_bundle/main/database/

# A cache directory. Populated on first-run and then never changes.
-rifgen:data_cache_dir    rifgen_cache


############################## RIF Flags #####################################

# What kind of RIF do you want to generate:
#                                    Normal: RotScore64
#            Normal with hbond satisfaction: RotScoreSat (RotScoreSat_2x16 if you have >255 of polar atoms)
# Hotspots:
#    I may want to use require_satisfaction: RotScoreSat_1x16
#  I don't want to use require_satisfaction: RotScore64

-rifgen::rif_type RotScore64


##################### Normal RIF Configuration ##############################

# The next three flags control how the RIF is built (hotspots are separate!!)
# Which rif residues do you want to use?
#  apores are the hydrophobics (h-bonding is not considered when placing these)
#  donres donate hydrogens to form hydrogen bonds
#  accres accept hydrogens to form hydrogen bonds
-rifgen:apores VAL ILE LEU MET PHE TRP
-rifgen:donres SER THR TYR     GLN     ASN HIS HIS_D TRP # roughly in decreasing order of sample size REMOVED
-rifgen:accres SER THR TYR GLU GLN ASP ASN HIS HIS_D


-rifgen:score_threshold -0.5  # the score a rotamer must get in order to be added to the rif (kcal/mol) 


###################### Hotspot configuration #################################
#   (use this either with or without apores, donres, and accres)

# Pick one of the two following methods for hotspot input:

# Hotspot input multiple distinct groups
# -hotspot_groups group0.pdb group1.pdb group2.pdb group3.pdb

# Hotspot input every hotspot is a group
# -hotspot_groups all_my_hotspots.pdb
# -single_file_hotspots_insertion

# -hotspot_sample_cart_bound 1.5   # How much do you want your hotspots to move left/right/up/down
# -hotspot_sample_angle_bound 15   # What angular deviation from your hotspot will you accept

# -hotspot_nsamples 100000  # How many times should the random sampling be done. 100000 - 1000000 is good

# -hotspot_score_thresh -0.5 # What score must a hotspot produce in order to be added to the RIF
# -hotspot_score_bonus -4    # Be careful, rifdock has a maximum score of -9
                             #  do not exceed this (this gets added to the hotspot score)


###################### General flags #######################################

-rifgen:hbond_weight 2.0           # max score per h-bond (kcal/mol. Rosetta is ~ 2.1)
-rifgen:upweight_multi_hbond 0.0   # extra score factor for bidentate hbonds (this is really sketchy)

# For donres and accres. What's the minimum quality h-bond where we keep the rotamers even if it doesn't pass score_threshold?
# This is on a scale from -1 to 0 where -1 represents a perfect hbond
-min_hb_quality_for_satisfaction -0.25 




###################### Experimental flags ##################################

# -use_rosetta_grid_energies true/false  # Use Frank's grid energies for donres, accres, and user hotspots



##############################################################################
##############################################################################
#################### END OF USER ADJUSTABLE SETTINGS #########################
##############################################################################
##############################################################################


-rifgen:extra_rotamers false          # actually ex1 ex2 
-rifgen:extra_rif_rotamers true       # kinda like ex2

-rif_accum_scratch_size_M 24000

-renumber_pdb

-hash_cart_resl              0.7      # rif cartesian resolution
-hash_angle_resl            14.0      # rif angle resolution

# how exactly should the rosetta energy field be calculated?
# The further down you go, the higher the resolution
# This only affects hydrophobics
-rifgen::rosetta_field_resl 0.25
-rifgen::search_resolutions 3.0 1.5 0.75
#-rifgen::rosetta_field_resl 0.125
#-rifgen::search_resolutions 4.0 2.0 1.0 0.5
#-rifgen::rosetta_field_resl 0.125
#-rifgen::search_resolutions 3.0 1.5 0.75 0.375


-rifgen:score_cut_adjust 0.8

-hbond_cart_sample_hack_range 1.00
-hbond_cart_sample_hack_resl  0.33

-rifgen:tip_tol_deg        60.0 # for now, do either 60 or 36
-rifgen:rot_samp_resl       6.0


-rifgen:rif_hbond_dump_fraction  0.000001
-rifgen:rif_apo_dump_fraction    0.000001

-add_orbitals

-rifgen:beam_size_M 10000.0
-rifgen:hash_preallocate_mult 0.125
-rifgen:max_rf_bounding_ratio 4.0

-rifgen:hash_cart_resls   16.0   8.0   4.0   2.0   1.0
-rifgen:hash_cart_bounds   512   512   512   512   512
-rifgen:lever_bounds      16.0   8.0   4.0   2.0   1.0
-rifgen:hash_ang_resls     38.8  24.4  17.2  13.6  11.8 # yes worky worky
-rifgen:lever_radii        23.6 18.785501 13.324600  8.425850  4.855575
    """

    with open ('./rifgen.flag', 'a') as file:
        file.writelines(rifgen_flag)
        file.close()

    print ('-----------------------------')
    print ('RifGen running ...')

    os.system(f'rifgen @rifgen.flag > rifgen.log 2>&1')
    os.system(f'cp ./rifgen_output/rif_64_output_sca0.8_noKR.rif.gz_target.pdb.gz ./')
    os.system(f'python3 tools/chain_change.py rif_64_output_sca0.8_noKR.rif.gz_target.pdb.gz AB')
    os.system(f'rm -rf rif_64_output_sca0.8_noKR.rif.gz_target.pdb.gz')
    os.system('rm -rf ./rifgen.flag')

    print ('Done !')


def polyV (binder_dir=args.binderdir):

    polyV_flag="""<ROSETTASCRIPTS>
    <SCOREFXNS>
        <ScoreFunction name="sfxn" weights="ref2015" />

    </SCOREFXNS>
    <TASKOPERATIONS>

         <RestrictAbsentCanonicalAAS name="polyV" keep_aas="V" />

    </TASKOPERATIONS>
    <MOVERS>
        <PackRotamersMover name="PackRotamers" scorefxn="sfxn" task_operations="polyV" /> 
    </MOVERS>
    <PROTOCOLS>

        <Add mover="PackRotamers" />

    </PROTOCOLS>
    <OUTPUT />
</ROSETTASCRIPTS>
"""

    with open ('./polyV.xml', 'a') as file:
        file.writelines(polyV_flag)
        file.close()

    print ('-----------------------------')
    print ('polyV-ize running ...')

    if 'polyV_binders' in os.listdir('./'):
        pass

    else:
        os.mkdir('polyV_binders')


    os.system(f"find {binder_dir} -name '*.pdb' > binders.list")

    os.system(f'rosetta_scripts.mpi.linuxgccrelease -parser:protocol polyV.xml -beta_nov16 -l binders.list -mute protocols.rosetta_scripts.ParsedProtocol.REPORT -mute protocols.rosetta_scripts.ParsedProtocol.REPORT -out:path:all ./polyV_binders > polyV_log.log 2>&1')
    os.system("find $(pwd)/polyV_binders -name '*.pdb' > polyV_scaffolds.list")
    os.system('rm -rf polyV.xml')



def patchdock(sitelist=args.sitelist, patchdock=args.patchdock):

    with open (sitelist) as file:
        res = file.readlines()

    sitelist = sitelist.split('/')[-1].replace('.list','')

    lsname = f'{sitelist}_patchdock.list'

    for i in res:
        with open (f'./input/{lsname}', 'w') as resfile:
            i = i.strip()
            resfile.write (f'{i} B')

    os.mkdir ('patchdock_xforms')
    os.chdir ('patchdock_xforms')

    os.system(f'python3 ../tools/setup_patchdock_jobs.py -target_pdb ../rif_64_output_sca0.8_noKR.rif.gz_target_chainchanged.pdb -patchdock {patchdock} -pdb_list ../polyV_scaffolds.list -target_res ../input/{lsname} > ../patchdock_commands.list')

    os.chdir ('..')



def patchdock_multi(i):
    os.system(i)
    print ('done !')


def RifDock(phobics=args.phobics):

    xmlStr = f"""###########################################


# Fill this in with the output from RifGen


#################################################################################################################
#################################################################################################################
#################################################################################################################
#################################################################################################################
#################################################################################################################
#################################################################################################################
#################################################################################################################
#################################################################################################################
#################################################################################################################
#################################################################################################################

################################ Constant paths ##########################################

-database /home/rosetta_src_2018.09.60072_bundle/main/database/

# A cache directory. Populated on first-run and then never changes.
-rif_dock:data_cache_dir    rifdock_cache



############################### Last minute options ######################################

#-outputsilent  # Make sure you enable this for your production run. Dealing with 6M pdbs is less than ideal

-n_pdb_out_global 300                      # n_pdb_out controls how many per patchdock output. This is how many total
-rif_dock:redundancy_filter_mag 0.5       # The "RMSD" cluster threshold for the output. Smaller numbers give more, but redundant output

#################################### Flags that control output ##########################################

-rif_dock:outdir  rifdock_out             # the output folder for this run
-rif_dock:dokfile all.dok                 # the "score file" for this run

-rif_dock:n_pdb_out 30                    # max number of output pdbs

#-rif_dock:target_tag conf01              # optional tag to add to all outputs
-rif_dock:align_output_to_scaffold false  # If this is false, the output is aligned to the target

# Pick either one of the following or none
# (None)                                  # Output target + scaffold. But scaffold may be poly ALA with rifres based on scaffold_to_ala
#-output_scaffold_only                    # Output just the scaffold. But scaffold may be poly ALA with rifres based on scaffold_to_ala
-output_full_scaffold                     # Output target + scaffold. Scaffold retains input sequence plus rifres
#-output_full_scaffold_only               # Output just the scaffold. Scaffold retains input sequence plus rifres


############################ Flags that affect runtime/search space ####################################

-beam_size_M 5                            # The number of search points to using during HSearch
-hsearch_scale_factor 1.2                 # The default search resolution gets multiplied by this. People don't usually change this.

#-rif_dock:tether_to_input_position 3     # Only allow results within this "RMSD" of the input scaffold

-rif_dock:global_score_cut -8.0          # After HSearch and after HackPack, anything worse than this gets thrown out


##################### Flags that only affect the PatchDock/RifDock runs ################################
# Uncomment everything here except seeding_pos if running PatchDock/RifDock

#-rif_dock:seeding_pos ""                  # Either a single file or a list of seeding position files
-rif_dock:seeding_by_patchdock true       # If true, seeding_pos is literally the PatchDock .out file
                                           # If false, seeding_pos file is list of transforms. 
                                           #   (Each row is 12 numbers. First 9 are rotation matrix and last 3 are translation.)
-rif_dock:patchdock_min_sasa  1000        # Only take patchdock outputs with more than this sasa
-rif_dock:patchdock_top_ranks 2000        # Only take the first N patchdock outputs

-rif_dock:xform_pos tools/small_sampling_10deg_by1.7_1.5A_by_0.6.x
                                           # Which xform file do you want to use. Difference is how many degrees do you want to 
                                           #   deviate from the PatchDock outputs. Pick one from here:
                                           #                 /home1/05571/bcov/sc/scaffold_comparison/data/xform_pos_ang*



-rif_dock:cluster_score_cut -6.0          # After HackPack, what results should be thrown out before applying -keep_top_clusters_frac
-rif_dock:keep_top_clusters_frac 1.0      # After applying the cluster_score_cut, what fraction of remaining seeding positions should survive?
                                         
-rosetta_score_each_seeding_at_least 1    # When cutting down the results by rosetta_score_fraction, make sure at least this many from each 
                                           #   seeding position survive

-only_load_highest_resl                   # This will make rifdock use less ram. Highly recommended for the patchdock protocol.


##################### Advanced seeding position flags ##################################################

#-rif_dock:seed_with_these_pdbs *.pdb      # List of scaffolds floating in space above the target that you would like to use instead.
                                           #   of numeric seeding positions. The target shouldn't be present and the scaffold must match exactly
                                           #   Use this instead of -seeding_pos
#-rif_dock:seed_include_input true         # Include the input pdb as one of the pdbs for -seed_with_these_pdbs

#-rif_dock:write_seed_to_output true       # Use this if you want to know which output came from which seeding position


##################### Flags that affect how things are scored ##########################################

#-use_rosetta_grid_energies true/false     # Your choice. If True, uses Frank's grid energies during Hackpack

-hbond_weight 2.0                          # max score per hbond (Rosetta's max is 2.1)
-upweight_multi_hbond 0.0                  # extra score factor for bidentate hbonds (BrianC recommends don't do this)
-min_hb_quality_for_satisfaction -0.25     # If using require_satisfaction (or buried unsats). How good does a hydrogen bond need to be to "count"?
                                           #   The scale is from -1.0 to 0 where -1.0 is a perfect hydrogen bond.
-scaff_bb_hbond_weight 2.0                 # max score per hbond on the scaffold backbone 

-favorable_1body_multiplier 0.2            # Anything with a one-body energy less than favorable_1body_cutoff gets multiplied by this
-favorable_1body_multiplier_cutoff 4       # Anything with a one-body energy less than this gets multiplied by favorable_1body_multiplier
-favorable_2body_multiplier 5              # Anything with a two-body energy less than 0 gets multiplied by this

-user_rotamer_bonus_constant 0             # Anything that makes a hydrogen-bond, is a hotspot, or is a "requirement" gets this bonus
-user_rotamer_bonus_per_chi 0              # Anything that makes a hydrogen-bond, is a hotspot, or is a "requirement" gets this bonus * number of chis

-rif_dock:upweight_iface 2.0               # During RifDock and HackPack. rifres-target interactions are multiplied by this number


################ stuff related to picking designable and fixed positions #################

#### if you DO NOT supply scaffold_res files, this will attempt to pick which residues on the scaffold
#### can be mutated based on sasa, internal energy, and bb-sc hbonds
-scaffold_res_use_best_guess true

#### if scaffold_res is NOT used, this option will cause loop residues to be ignored
#### scaffold_res overrides this
-rif_dock::dont_use_scaffold_loops false

#### these cause the non-designable scaffold residues to still contribute sterically
#### and to the 1 body rotamer energies. use these flags if you have a fully-designed scaffold
#-rif_dock:scaffold_to_ala false
#-rif_dock:scaffold_to_ala_selonly true
#-rif_dock:replace_all_with_ala_1bre false
#### if you don't have a fully designed scaffold, treat non-designable positions as alanine
-rif_dock:scaffold_to_ala true            # Brian thinks that converting the whole scaffold to alanine works better during rosetta min
-rif_dock:scaffold_to_ala_selonly false
-rif_dock:replace_all_with_ala_1bre true



#################################### HackPack options #####################################
-hack_pack true                            # Do you want to do HackPack? (Probably a good idea)
-rif_dock:hack_pack_frac  1.0              # What fraction of your HSearch results (that passed global_score_cut) do you want to HackPack?


############################# rosetta re-scoring / min stuff ###################################

-rif_dock:rosetta_score_cut -10.0                    # After RosettaScore, anything with a score worse than this gets thrown out

-rif_dock:rosetta_score_fraction 0                   # These two flags greaty affect runtime!!!!!
-rif_dock:rosetta_min_fraction 1                     # Choose wisely, higher fractions give more, better output at the cost of runtime

-rif_dock:rosetta_min_at_least 30                    # Make sure at least this many survive the rosetta_min_fraction
-rif_dock:rosetta_min_at_most 300                    # Make sure no more than this get minned
-rif_dock:rosetta_score_at_most  3000              # Make sure that no more than this many go to rosetta score

-rif_dock:replace_orig_scaffold_res false            # If you converted to poly ALA with scaffold_to_ala, this puts the original residues
                                                     #   back before you do rosetta min.
-rif_dock:override_rosetta_pose true                 # Brian highly recommends this flag. This prevents the minimized pose from being output
-rif_dock:rosetta_min_scaffoldbb false               # Set BB movemap of scaffold to True
-rif_dock:rosetta_min_targetbb   false               # Set BB movemap of target to true
-rif_dock:rosetta_hard_min false                     # Minimize with the "hard" score function (alternative is "soft" score function)

-rif_dock:rosetta_score_rifres_rifres_weight   0.6   # When evaluating the final score, multiply rifres-rifres interactions by this
-rif_dock:rosetta_score_rifres_scaffold_weight 0.4   # When evaluating the final score, multiply rifres-scaffold interactions by this
                                                     #  These two flags only get used if the interaction is good. Bad interactions are
                                                     #    full weight.


######################### Special flags that do special things #################################

#-hack_pack_during_hsearch False           # Run HackPack during the HSearch. Doesn't usually help, but who knows.
#-require_satisfaction 4                   # Require at least this many hbonds, hotspots, or "requirements"
#-require_n_rifres  3                      # Require at least this may rifres (not perfect)

#-requirements 0,1,2,8                     # Require that certain satisfactions be required in all outputs
                                           # If one runs a standard RifDock, these will be individual hydrogen bonds to specific atoms
                                           # If one uses hotspots during rifgen, these will correspond the the hotspots groups
                                           #   However, due to some conflicts, these will also overlap with hydrogen bonds to specific atoms
                                           # Finally, if one uses a -tuning_file, these will correspond to the "requirements" set there


######################### Hydrophobic Filters ##################################################
# These are rather experimental flags. You'll have to play with the values.
# Hydrophobic ddG is roughly fa_atr + fa_rep + fa_sol for hydrophobic residues.

#-hydrophobic_ddg_cut -12                  # All outputs must have hydrophobic ddG at least this value
#-require_hydrophobic_residue_contacts len(PATCHDOCK_RESIDUES) - 1   # All outputs must make contact with at least this many target hydrophobics
-require_hydrophobic_residue_contacts {phobics-1}
#-one_hydrophobic_better_than -2           # Require that at least one rifres have a hydrophobic ddG better than this
#-two_hydrophobics_better_than -2          # Require that at least two rifres have a hydrophobic ddG better than this
#-three_hydrophobics_better_than -1        # Require that at least three rifres have a hydrophobic ddG better than this

# This next flag affects the *_hydrophobics_better_than flags. A rifres can only be counted towards those flags if it passes this one.
#-hydrophobic_ddg_per_atom_cut -0.3        # Require that hydrophobics for the *_hydrophobics_better_than flags have at least this much 
                                           #  ddG per side-chain heavy atoms.

#-hydrophobic_target_res PATCHDOCK_RESIDUES        # If you want your selection of hydrophobic residues to include only a subset of the ones
-hydrophobic_target_res {phobics}
                                           #  you selected for the target_res, place that selection here with commas.

#-count_all_contacts_as_hydrophobic        # Use this if some of your hydrophobic_target_res aren't actually hydrophobic amino acids

-hydrophobic_ddg_weight 3
######################### options to favor existing scaffold residues ##########################
-add_native_scaffold_rots_when_packing 0 # 1
-bonus_to_native_scaffold_res          0 # -0.5


################################# Twobody table caching ####################################

# RifDock caches the twobody tables so that you can save time later. If you use the same scaffolds
#  in the same directory mulitple times. This is a good idea. Otherwise, these take up quite
#  a bit of space and it might be smart to turn the caching off.

-rif_dock:cache_scaffold_data False
-rif_dock:data_cache_dir  rifdock_cache




############################################################################################
############################################################################################
############################ END OF USER ADJUSTABLE SETTINGS ###############################
############################################################################################
############################################################################################


#### to use -beta, ask will if you don't want to use -beta
-beta
-score:weights beta_soft
-add_orbitals false

#### HackPack options you probably shouldn't change
-rif_dock:pack_n_iters    2
-rif_dock:pack_iter_mult  2.0
-rif_dock:packing_use_rif_rotamers        true
-rif_dock:extra_rotamers                  false
-rif_dock:always_available_rotamers_level 0


#### details for how twobody rotamer energies are computed and stored, don't change
-rif_dock:rotrf_resl   0.25
-rif_dock:rotrf_spread 0.0
-rif_dock:rotrf_scale_atr 1.0

### Brian doesn't know what these flags do
-rif_dock::rf_resl 0.5
-rif_dock::rf_oversample 2
-rif_dock:use_scaffold_bounding_grids 0
-rif_dock:target_rf_oversample 2


 # disulfides seem to cause problems... ignoring them isn't really an issue unless
 # you do bbmin where there should be disulfides
-detect_disulf 0


-mute core.scoring.ScoreFunctionFactory
-mute core.io.pose_from_sfr.PoseFromSFRBuilder

    """

    with open ('./rifgen.log') as logf:
        ls = logf.readlines()[-14:-1]
        with open ('rifdock.flag', 'a') as dockflag:
            dockflag.writelines('########################################### what you need for docking' + '\n')
            for i in ls:
                i = i.rstrip()
                dockflag.write(i + '\n')

            dockflag.write(xmlStr)
            dockflag.close()
        logf.close()

    print ('-----------------------------')
    print ('RifDock running ...')


    os.system('python3 tools/setup_rifdock_commands.py binders.list patchdock_xforms rifdock.flag /home/rosetta_src_2018.09.60072_bundle/main/source/rifdock/build/apps/rosetta/rif_dock_test')

    with open ('./rifdock_commands.list') as file:
        ls = file.readlines()

    for i in ls:
        os.system(i)

    os.system('rm -rf rifdock.flag')



if __name__ == '__main__':
    rifgen(template=args.template, sitelist=args.sitelist)
    polyV (binder_dir=args.binderdir)
    patchdock(sitelist=args.sitelist, patchdock=args.patchdock)

    print ('-----------------------------')
    print ('Patchdock running ...')

    with open ('./patchdock_commands.list') as runcom:
        ls = runcom.readlines()
    p = Pool(processes=args.np)
    rls = p.map(patchdock_multi, ls)

    RifDock(phobics=args.phobics)

