# -*- coding: utf-8 -*-
"""
Downloader for ogs5.

.. currentmodule:: ogs5py.tools.download

Downloader
^^^^^^^^^^

A downloading routine to get the OSG5 executable.

.. autosummary::
   :toctree: generated

   download_ogs
   add_exe
   reset_download
   OGS5PY_CONFIG

----
"""
import os
import platform
import shutil
import tarfile
import zipfile
from tempfile import TemporaryDirectory
from urllib.request import urlretrieve

# https://stackoverflow.com/a/53222876/6696397
OGS5PY_CONFIG = os.path.join(
    os.environ.get("APPDATA")
    or os.environ.get("XDG_CONFIG_HOME")
    or os.path.join(os.environ["HOME"], ".config"),
    "ogs5py",
)
"""str: Standard config path for ogs5py."""

RELEASE = "https://ogsstorage.blob.core.windows.net/binaries/ogs5/"

URLS = {
    "5.7": {
        "Linux": (
            RELEASE + "ogs-5.7.0-Linux-2.6.32-573.8.1.el6.x86_64-x64.tar.gz"
        ),
        "Windows": RELEASE + "ogs-5.7.0-Windows-6.1.7601-x64.zip",
        "Darwin": RELEASE + "ogs-5.7.0-Darwin-15.2.0-x64.tar.gz",
    },
    "5.7.1": {
        "Windows": (
            "https://github.com/ufz/ogs5/releases/download/5.7.1/ogs-5.7.1-Windows-x64.zip"
        )
    },
    "5.8": {
        "Linux": (
            RELEASE + "ogs-5.8-Linux-2.6.32-754.3.5.el6.x86_64-x64.tar.gz"
        ),
        "Windows": RELEASE + "ogs-5.8-Windows-x64.zip",
    },
}


def download_ogs(
    version="5.7", system=None, path=OGS5PY_CONFIG, name=None, build=None
):
    """
    Download the OGS5 executable.

    Parameters
    ----------
    version : :class:`str`, optional
        Version to download ("5.7", "5.8", "5.7.1").
        Default: "5.7"
    system : :class:`str`, optional
        Target system (Linux, Windows, Darwin). Default: platform.system()
    path : :class:`str`, optional
        Destination path. Default: :any:`OGS5PY_CONFIG`
    name : :class:`str`, optional
        Destination file name. Default "ogs[.exe]"
    build : :class:`str`, optional
        Only None and "FEM" supported.

    Returns
    -------
    dest : :class:`str`
        If an OGS5 executable was successfully downloaded, the file-path
        is returned.

    Notes
    -----
    There is only an executable on "Darwin" for version "5.7".

    Taken from:

        * https://www.opengeosys.org/ogs-5/
    """
    system = platform.system() if system is None else system
    path = os.path.abspath(path)
    if build not in [None, "FEM"]:
        raise ValueError("download_ogs: only build='FEM' supported")
    if not os.path.exists(path):
        os.makedirs(path)
    if version not in URLS:
        raise ValueError(f"'{version}': unknown version. Use: {URLS}")
    urls_version = URLS[version]
    if system not in urls_version:
        raise ValueError(
            f"'{system}': unsupported system for version '{version}'. Use: {urls_version}"
        )
    ogs_url = urls_version[system]
    print("Downloading: ", ogs_url)
    ext = ".tar.gz" if ogs_url.endswith(".tar.gz") else ".zip"
    if name is None:
        name = "ogs.exe" if system == "Windows" else "ogs"
    dest = os.path.join(path, name)
    with TemporaryDirectory() as tmpdirname:
        data_filename = os.path.join(tmpdirname, "data" + ext)
        urlretrieve(ogs_url, data_filename)
        # extract the data
        if ext == ".tar.gz":
            z_file = tarfile.open(data_filename, "r:gz")
            names = z_file.getnames()
        else:
            z_file = zipfile.ZipFile(data_filename)
            names = z_file.namelist()
        found = ""
        for file in names:
            if os.path.basename(file).startswith("ogs"):
                found = file
                break
        if found:
            z_file.extract(member=found, path=tmpdirname)
            shutil.copy(os.path.join(tmpdirname, found), dest)
        z_file.close()
    return dest if found else None


def add_exe(ogs_exe, dest_name=None):
    """
    Add an OGS5 exe to :any:`OGS5PY_CONFIG`.

    Parameters
    ----------
    ogs_exe : :class:`str`
        Path to the ogs executable to be copied.
    dest_name : :class:`str`, optional
        Destination file name. Default: basename of ogs_exe

    Returns
    -------
    dest : :class:`str`
        If an OGS5 executable was successfully copied, the file-path
        is returned.
    """
    if platform.system() == "Windows" and ogs_exe[-4:] == ".lnk":
        print("Don't use file links under windows...")
        return None
    if os.path.islink(ogs_exe):
        ogs_exe = os.path.realpath(ogs_exe)
    if os.path.exists(ogs_exe) and os.path.isfile(ogs_exe):
        dest_name = (
            os.path.basename(ogs_exe) if dest_name is None else dest_name
        )
        dest = os.path.join(OGS5PY_CONFIG, dest_name)
        shutil.copy(ogs_exe, dest)
        return dest
    print("The given ogs_exe does not exist...")
    return None


def reset_download():
    """Reset all downloads in :any:`OGS5PY_CONFIG`."""
    shutil.rmtree(OGS5PY_CONFIG, ignore_errors=True)
