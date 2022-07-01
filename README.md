Python scripts in this directory is originated form the supplementary data of Cao_2021_Nature.


### Arguments
```
parser.add_argument('--binderdir', required=False, type=str, default='./binders/', help='path to binders')
parser.add_argument('--template', required=False, type=str, default='./input/template.pdb', help='path to template file')
parser.add_argument('--phobics', required=False, type=int, default=3, help='Number of hydrophobic residues in the interface')
parser.add_argument('--patchdock', required=False, type=str, default='/opt/PatchDock/', help='path to patchdock')
parser.add_argument('--sitelist', required=False, type=str, default='./input/site.list', help='path to template file')

parser.add_argument('--np', required=False, type=int, default=8, help='num_cores')

```

```
usage: auto_rifdock.py [-h] [--binderdir BINDERDIR] [--template TEMPLATE]
                       [--phobics PHOBICS] [--patchdock PATCHDOCK]
                       [--sitelist SITELIST] [--np NP]

Script for designing protein binder

optional arguments:
  -h, --help            show this help message and exit
  --binderdir BINDERDIR
                        path to binders
  --template TEMPLATE   path to template file
  --phobics PHOBICS     Number of hydrophobic residues in the interface
  --patchdock PATCHDOCK
                        path to patchdock
  --sitelist SITELIST   path to template file
  --np NP               num_cores
```




### 폴더 구성
```
Working dir /
    input / 
        target.pdb
        res.list

    binders /
        binder_1.pdb
        binder_2.pdb
        ...

    tools / 
        chain_change.py
        prepare_run.py
        setup_patchdock_jobs.py
        setup_rifdock_commands.py
        small_sampling_10deg_by1.7_1.5A_by_0.6x
```

- input: 타겟 및 binder 결합부위 정보를 담고있는 res.list
    - res.list 에는 아래와 같이 결합부위 residue 가 나열되어 있어야 함
        ```
        1
        2
        3
        22
        23
        24
        88
        89
        90
        91
        ...
        ```
    - etc/prep_res_list.py 를 이용해 손쉽게 만들 수 있음
        ```
        python3 prep_res_list.py 
        --residues 1-10+22-80+156+167+210-240
        ```

- tools: auto_rifdock.py 스크립트가 tools 에 있는 파이썬 스크립트를 참조하므로 반드시 같이 다녀야 함

- binders: binder 후보들이 들어있는 폴더. 파일명은 별 상관 없음



```
python3 auto_rifdock.py --binderdir ./binders --template ./input/target.pdb --phobics 3 --sitelist ./input/res.list --np 20
```