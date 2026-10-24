"""Conservative output isolation. No frozen artifacts are written here."""
from pathlib import Path


def project_path(root, relative):
    root = Path(root).resolve()
    relative = Path(relative)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("Expected project-relative path without traversal")
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError("Path escapes project")
    return path


def validate_output_dir(root, relative):
    root = Path(root).resolve()
    rel = Path(relative)
    if len(rel.parts) < 2 or rel.parts[0] not in ("staging", "reproduction"):
        raise ValueError("Output must be a run below staging/ or reproduction/")
    # Reject links/junctions even if they currently point inside the project.
    current = root
    for part in rel.parts:
        current = current / part
        if current.is_symlink() or (hasattr(current, "is_junction") and current.is_junction()):
            raise ValueError("Linked output paths are forbidden")
    path = project_path(root, relative)
    if not path.is_relative_to(root / rel.parts[0]):
        raise ValueError("Output escapes allowed root")
    if path.exists():
        raise FileExistsError(path)
    return path


def create_run_dir(root, relative):
    path = validate_output_dir(root, relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    validate_output_dir(root, relative)
    path.mkdir(exist_ok=False)
    return path


def _new_output_path(root, run_relative, filename):
    root = Path(root).resolve()
    rel = Path(run_relative)
    if len(rel.parts)<2 or rel.parts[0] not in ("staging", "reproduction"):
        raise ValueError("Forbidden output root")
    for relative in (rel, rel/Path(filename)):
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("Invalid output path")
        current=root
        for part in relative.parts:
            current/=part
            if current.is_symlink() or (hasattr(current,"is_junction") and current.is_junction()):
                raise ValueError("Linked output paths are forbidden")
    run = project_path(root, run_relative)
    if Path(filename).is_absolute() or not run.is_dir():
        raise ValueError("Expected existing isolated run and relative filename")
    path = project_path(run, filename)
    return path


def open_new_output(root, run_relative, filename):
    """Exclusive UTF-8 text writer within an existing isolated run."""
    return _new_output_path(root,run_relative,filename).open("x",encoding="utf-8")


def open_new_binary_output(root, run_relative, filename):
    """Binary persistence shares all text writer link/path/exclusivity guards."""
    return _new_output_path(root,run_relative,filename).open("xb")
