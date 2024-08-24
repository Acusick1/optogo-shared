from pathlib import Path
from typing import Optional


def rmdir(directory: Path):
    """
    Pathlib rmdir, allows directory to be removed by recursively removing all files below it in the tree.

    Parameters
    ----------
    directory: Path to directory to be removed
    """
    for item in directory.iterdir():
        if item.is_dir():
            rmdir(item)
        else:
            item.unlink()

    directory.rmdir()


def move_dir(
    path: Path,
    to: Optional[Path] = None,
    name: Optional[str] = None,
    parents: bool = False,
):
    """
    Move a directory to a new location.
    Multiple use cases:
        1. Specify path and to > directory moved to new location
        2. Specify path and name > equivalent to rename
        3. Specify path, to, and name > directory moved with new name

    Parameters
    ----------
    path: Full path to directory to be moved (including directory)
    to: Desired location for directory to be moved (not including directory)
    name: Option to rename directory
    parents: See pathlib.Path.mkdir(parents)
    """
    if to is None:
        to = path

    if name is None:
        name = path.name

    new_path = to / name
    new_path.mkdir(parents=parents)
    path.rename(new_path)


def mv_parent_swap(path: Path, new_parent: Path | str, level: int = 0):
    """
    Move a file from one parent folder to another
    Note: Can be used for directories but will fail if new path already exists (i.e. trying to merge folders)

    Parameters
    ----------
    path: Current path to file
    new_parent: Parent to move file to
    level: Location of parent to swap (level 0 = parent, level 1 = grandparent etc.)

    Returns
    -------
    New path
    """

    parts = list(path.parts)
    parts[-abs(level) - 2] = new_parent

    new_path = Path(*parts)

    path.rename(new_path)

    return new_path
