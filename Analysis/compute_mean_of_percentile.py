import argparse
import glob

import pandas as pd


def parse_args():

    parser = argparse.ArgumentParser()
    parser.add_argument("reports", type=str,
                        help="Path pattern to report files that you want to filter by.")
    parser.add_argument("--criteria", type=str, default='Binding Energy',
                        help="Criteria we want to compute. "
                             "Must be a column of the report. i.e: Binding Energy.")
    parser.add_argument("--quantile", type=str, default=0.25,
                        help="Percentile to filter the sample. i.e: 0.25.")
    parser.add_argument("--filter_by", type=str, default=None,
                        help="Column of the report to create a subset, if needed.")
    parser.add_argument("--lim_low", type=str, default=None,
                        help="Lowest threshold value to create the subset")
    parser.add_argument("--lim_high", type=str, default=None,
                        help="Highest threshold value to create the subset")
    
    args = parser.parse_args()

    return args.reports, args.quantile, args.filter_by, args.lim_low, args.lim_high


def pele_report2pandas(path):
    """
        This function merge the content of different report for PELE simulations in a single file pandas Data Frame.
    """
    data = []
    report_list = sorted(glob.glob('{}'.format(path)))
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


def compute_mean_quantile(dataframe, column, quantile_value=0.25, limit_col=None, limit_up=None, limit_down=None):
    if limit_col:
        if not limit_up:
            raise ValueError("You must fill the argument '--limit_up'!")
        if not limit_down:
            raise ValueError("You must fill the argument '--limit_down'!")
        dataframe = dataframe[dataframe[limit_col] > float(limit_down)]
        dataframe = dataframe[dataframe[limit_col] < float(limit_up)]
    dataframe = dataframe[dataframe[column] < dataframe[column].quantile(quantile_value)]
    dataframe = dataframe[column]
    mean_subset = dataframe.mean()
    return mean_subset


def main(path, criteria, quantile=0.25, limit_col=None, limit_up=None, limit_down=None):
    df = pele_report2pandas(path)
    mean = compute_mean_quantile(df, criteria, quantile, limit_col, limit_up, limit_down)
    print(mean)

if __name__ == '__main__':
    path, criteria, quantile, limit_col, limit_up, limit_down = parse_arguments()
    main(path, criteria, quantile, limit_col, limit_up, limit_down)
    
    

