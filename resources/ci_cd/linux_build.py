#!/usr/bin/env python3
#
# (c) 2021 Copyright, Real-Time Innovations, Inc.  All rights reserved. RTI
# grants Licensee a license to use, modify, compile, and create derivative
# works of the Software.  Licensee has the right to distribute object form only
# for use with RTI products.  The Software is provided "as is", with no
# warranty of any type, including any warranty for fitness for any purpose. RTI
# is under no obligation to maintain or support the Software.  RTI shall not be
# liable for any incidental or consequential damages arising out of the use or
# inability to use the software.
"""Build all the examples.

The environment variable RTI_PACKAGE_VERSION must be assigned to find the
correct RTIConnextDDS package version.

"""
from io import FileIO
import os
import platform
import sys
import subprocess

from pathlib import Path


def print_lines(proc: subprocess.Popen, logfile: FileIO):
    for line in proc.stdout:
        sys.stdout.write(line.decode("utf-8"))
        if logfile:
            logfile.write(line.decode("utf-8"))


def main():
    try:
        rti_installation_path = Path(
            os.getenv("RTI_INSTALLATION_PATH") or Path.home()
        ).resolve(strict=True)
    except FileNotFoundError:
        sys.exit("The RTI_INSTALLATION_PATH does not exist.")

    try:
        examples_dir = Path("examples/connext_dds").resolve(strict=True)
    except FileNotFoundError:
        sys.exit("Error: Examples directory not found.")

    logfile = None

    if len(sys.argv) > 1:
        logfile = open(sys.argv[1], "w")

    found_rti_connext_dds = list(
        rti_installation_path.glob("rti_connext_dds-?.?.?")
    )

    if not found_rti_connext_dds:
        sys.exit("Error: RTIConnextDDS not found.")

    rti_connext_dds_dir = found_rti_connext_dds[0]
    build_dir = examples_dir.joinpath("build")

    build_dir.mkdir(exist_ok=True)

    print("[RTICommunity] Generating build system...", flush=True)

    command = [
        "cmake",
        "-DSTATIC_ANALYSIS=ON",
        "-DBUILD_SHARED_LIBS=ON",
        "-DCMAKE_BUILD_TYPE=Release",
        "-DCMAKE_EXPORT_COMPILE_COMMANDS=ON",
        f"-DCONNEXTDDS_DIR={str(rti_connext_dds_dir)}",
        str(examples_dir),
    ]

    if platform.system() == "Windows":
        command += ["-G", "Visual Studio 15 2017", "-A", "x64"]

    proc = subprocess.Popen(
        command,
        cwd=build_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    print_lines(proc, logfile)

    proc.wait()

    if proc.returncode:
        sys.exit("There was some errors during generating the build system.")

    print("\n[RTICommunity] Compiling the examples...", flush=True)

    proc = subprocess.Popen(
        ["cmake", "--build", ".", "--config", "Release"],
        cwd=build_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    print_lines(proc, logfile)

    proc.wait()

    if proc.returncode:
        sys.exit("There was some errors during build.")


if __name__ == "__main__":
    main()
