import glob
import argparse

def parse_args():

    parser = argparse.ArgumentParser()
    parser.add_argument("pdbs", type=str,
                        help="Path pattern to pdb files that you want to join.")
    parser.add_argument("--out", "-o", type=str, default="trajectory.pdb",
                        help="Output file of the trajectory file. i.e: 'trajectory.pdb'")

    args = parser.parse_args()

    return args.pdbs, args.out 


def read_pdb_files(pattern):
    pdbs = []
    all = glob.glob(pattern)
    print(all)
    for i in all:
        with open(i) as file:
            content = file.read()
            pdbs.append(content)
    return pdbs


def clean_pdbs(pdb_list):
    corrected_pdbs = []
    for i in pdb_list:
        lines = i.split("\n")
        lines.remove('END')
        for l in lines:
            if l.startswith("MODEL"):
                lines.remove(l)
        pdb = "\n".join(lines)
        corrected_pdbs.append(pdb)
    return corrected_pdbs


def join_pdbs(pdb_list):
    trajectory = []
    for n,i in enumerate(pdb_list):
        trajectory.append("MODEL        {}\n".format(n))
        trajectory.append(i)
    trajectory.append("END")
    trajectory = "".join(trajectory)
    return trajectory


def write_trajectory(trajectory, outputfile="trajectory.pdb"):
    with open(outputfile, "w") as out:
        out.write(trajectory)


def main(pdb_list, out="trajectory.pdb"):
    pdbs = read_pdb_files(pdb_list)
    corrected = clean_pdbs(pdbs)
    traj = join_pdbs(corrected)
    write_trajectory(traj, out)


if __name__ == "__main__":
    paths, out = parse_args()
    main(paths, out)

