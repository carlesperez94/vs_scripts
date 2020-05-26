import re
import os
import glob
import shutil
import argparse

import pandas as pd
import mdtraj as md


def parse_args():

    parser = argparse.ArgumentParser()
    parser.add_argument("reports", type=str, 
                        help="Path pattern to report files that you want to filter by.")
    parser.add_argument("--criteria", type=str, default='Binding Energy', 
                        help="Criteria we want to rank and output the strutures for. "
                             "Must be a clumn of the report. i.e: Binding Energy.")
    parser.add_argument("--nst", "-n", type=int, default=50,
                        help="Number of produced structures. i.e: 50")
    parser.add_argument("--out", "-o", type=str, default="./selected_reports.csv", 
                        help="Output file path of the csv. i.e: './selected_reports.csv'")
    parser.add_argument("--lim_crit", "-l", type=str, default=None,
                        help="If set, name of the column to filter out non-desired values. i.e: 'sasaLig'")
    parser.add_argument("--max_lim", "-max", type=float, default=None,
                        help="Max value of the threshold.")
    parser.add_argument("--min_lim", "-min", type=float, default=None,
                        help="Min value of the threshold.")

    args = parser.parse_args()

    return args.reports, args.criteria, args.nst, args.out, args.lim_crit, args.max_lim, args.min_lim


def pele_report2pandas(path):
    """
        This function merge the content of different report for PELE simulations in a single file pandas Data Frame.
    """
    data = []
    report_list = sorted(glob.glob('{}'.format(path)))
    print(report_list)
    if not report_list:
        raise FileNotFoundError("We can not find any report in: {}".format(path))

    for report in report_list:
        tmp_data = pd.read_csv(report, sep='    ', engine='python')
        tmp_data = tmp_data.iloc[1:]  # We must discard the first row
        processor = re.findall('\d+$'.format(path), report)
        tmp_data['Processor'] = processor[0]
        tmp_data['epoch'] = report.split("/")[-2]
        data.append(tmp_data)
        traj_path = os.path.join(os.path.dirname(report), 
                                 "trajectory_{}.xtc".format(processor[0]))
        tmp_data['traj'] = traj_path
    result = pd.concat(data)
    return result


def select_lowest(dataframe, n_elements=50, criteria="Binding Energy",
                  output="./selected_reports.csv", min_lim=None,
                  max_lim=None, lim_crit=None):
    if lim_crit:
        if not max_lim:
            raise ValueError("You must fill the argument '-max'!")
        if not min_lim:
            raise ValueError("You must fill the argument '-min'!")
        dataframe = dataframe[dataframe[lim_crit] > float(max_lim)]
        dataframe = dataframe[dataframe[lim_crit] <= float(min_lim)]
    report_values = dataframe.nsmallest(n_elements, criteria)
    report_values = report_values.reset_index() 
    report_values.to_csv(output, index=False)
    return report_values


def get_structures_from_dataframe(df, traj_col="traj"):
    if os.path.exists("selected_poses"):
        shutil.rmtree("selected_poses")
    os.mkdir("selected_poses")
    for i, row in df.iterrows():
        traj = row[traj_col]
        top_path = str(os.path.join("/".join(traj.split("/")[:-2]),
                       "topologies/topology_0.pdb"))
        struct = md.load_xtc(traj, top=top_path)
        snap = row["numberOfAcceptedPeleSteps"]
        pdb_name = "{}_epoch_{}_traj_{}_model_{}.pdb".format(i, row["epoch"], 
                                                               row["Processor"], 
                                                               snap)
        struct[snap].save_pdb(os.path.join("selected_poses", pdb_name))
        print("PDB file stored in {}".format(os.path.join("selected_poses", pdb_name)))


def main(path, n_elements=50, criteria="Binding Energy", 
         outfilename="./selected_reports.csv", max_lim=None,
         min_lim=None, lim_crit=None):
    df = pele_report2pandas(path)
    subset = select_lowest(df, n_elements, criteria, outfilename, max_lim, min_lim, lim_crit) 
    get_structures_from_dataframe(subset)
    return subset


if __name__ == "__main__":
    reports, crit, nst, out, lim_crit, max_lim, min_lim= parse_args()
    main(reports, nst, crit, out, max_lim, min_lim, lim_crit)

