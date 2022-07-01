Your target crystal structure must first be relaxed into the Rosetta Energy Function. The best way is to use a method that incorperates both the x-ray density and Rosetta at the same time. But this is beyond the scope of this guide.

The following uses a coordinate-constrained FastRelax to relax your target into the Rosetta force field

### ***relax***
$ROSETTA/bin/rosetta_scripts -parser:protocol $CAO_2021_PROTOCOL/paper_coord_relax.xml -beta_nov16 -s target.pdb 

target_0001.pdb is your relaxed pdb.


### ***manually trimming***
==== Target trimming ====

This step is optional but will speed up all subsquent calculations. Rosetta considers all residues of your target protein even if they are very far from the interface. For this reason, one can save time by opening the structure in a molecular viewer and deleting residues. Removing residues 20A away from the interface should be safe. The authors typically try to get the target to around 200 residues.

Trim target_0001.pdb and save the result as relaxed_trimmed_target.pdb.

==== Final target prep ====

Lastly, we need to turn your target into a single chain labeled chain A. The first command will remove all chain breaks and convert your protein to chain A. The second will renumber your protein starting at 1. (OXT atoms removed because Rosetta will sometimes interpret them as chain-breaks)

### ***chain break handling***
cat relaxed_trimmed_target.pdb | grep '^ATOM' | grep -v OXT | sed 's/./A/22' > target_chainA.pdb

### ***renumbering***
cleanpdb target_chainA.pdb A

target_ready.pdb is what we will give to RifGen
