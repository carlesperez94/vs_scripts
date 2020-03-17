#!/usr/bin/env python
"""
Program to prepare several complexes at once to run
PELEPlatform in a machine.
"""

import os
import glob
import shutil
import argparse

from Helpers import templatizer

__author__ = "Carles Perez Lopez"


def parse_arguments():
    """
        Parse user arguments
        Output: list with all the user arguments
    """
    # All the docstrings are very provisional and some of them are old, they would be changed in further steps!!
    parser = argparse.ArgumentParser(description="""Description: Program to prepare several complexes at once to run
    PELEPlatform in a machine.""")
    required_named = parser.add_argument_group('required named arguments')
    required_named.add_argument("complex_path", type=str, help="Path patter to the folder with all complexes.")
    required_named.add_argument("ifd_template", type=str, help="Path to IFD.ylm templatized.")
    required_named.add_argument("run_template", type=str, help="Path to run file templatized.")
    parser.add_argument("-o", "--out_folder", type=str, default="out",
                        help="Path to the output folder.")

    args = parser.parse_args()

    return args.complex_path, args.ifd_template, args.run_template, args.out_folder


def main(complex_path_patter, ifd_template, run_template, out_folder="."):
    complexes_paths = glob.glob(complex_path_patter)
    for compl in complexes_paths:
        name = compl.split(".pdb")[0]
        name = name.split("/")[-1]

        if not os.path.exists(out_folder):
            os.mkdir(out_folder)
        out_abs_path = os.path.abspath(out_folder)
        abs_path_cmplx = os.path.abspath(compl)

        print("Preparing {}...".format(name))
        ifd_folder = os.path.join(out_abs_path, "ifd")
        run_folder = os.path.join(out_abs_path, "run")

        ifd_temp_abspath = os.path.abspath(ifd_template)
        ifd_basename = ifd_temp_abspath.split("/")[-1]
        run_temp_abspath = os.path.abspath(run_template)
        run_basename = run_temp_abspath.split("/")[-1]

        if not os.path.exists("tmp"):
            os.mkdir("tmp")
        tmp_ifd_template = os.path.join("tmp", ifd_basename)
        tmp_run_template = os.path.join("tmp", run_basename)
        if not os.path.exists(ifd_folder):
            os.mkdir(ifd_folder)
        if not os.path.exists(run_folder):
            os.mkdir(run_folder)

        ifd_new_file = os.path.join(ifd_folder, "{}_{}.ylm".format(ifd_basename.split(".ylm")[0], name))
        run_new_file = os.path.join(run_folder, "{}_{}".format(run_basename, name))
        keywords = {"PDB": abs_path_cmplx,
                    "NAME": name,
                    "IFD_FILE": ifd_new_file}

        shutil.copyfile(ifd_temp_abspath, tmp_ifd_template)
        templatizer.TemplateBuilder(tmp_ifd_template, keywords)
        shutil.copyfile(tmp_ifd_template, ifd_new_file)
        print("IFD file saved in {} ...".format(ifd_new_file))

        shutil.copyfile(run_temp_abspath, tmp_run_template)
        templatizer.TemplateBuilder(tmp_run_template, keywords)
        shutil.copyfile(tmp_run_template, run_new_file)
        shutil.rmtree("tmp")

    print("Done!")


if __name__ == '__main__':
    complex_path, ifd_template, run_template, out = parse_arguments()
    main(complex_path, ifd_template, run_template, out)


