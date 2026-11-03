"""Lossless, reproducible packages for the native Power BI authoring tree."""
import argparse
from pathlib import Path, PurePosixPath
import zipfile

ROOT = Path(__file__).resolve().parents[1]
POWERBI_ARCHIVE = Path('downloads/FinancialPerformance-PowerBI.zip')


def _member_path(name):
    path = PurePosixPath(name)
    if not name or '\\' in name or ':' in name or path.is_absolute() or '..' in path.parts:
        raise ValueError(f'Unsafe archive path: {name}')
    return path


def write_archive(contents, destination):
    """Write sorted entries with fixed metadata, retaining every supplied byte."""
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(contents.items()):
            _member_path(name)
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data, compresslevel=9)


def extract_archive(source, destination):
    """Extract without replacing local edits; validate every entry before writing."""
    destination = Path(destination).resolve()
    with zipfile.ZipFile(source) as archive:
        entries = []
        seen = set()
        for entry in archive.infolist():
            member = _member_path(entry.filename)
            target = destination.joinpath(*member.parts).resolve()
            if not target.is_relative_to(destination) or target in seen:
                raise ValueError(f'Unsafe or duplicate archive path: {entry.filename}')
            seen.add(target)
            for parent in target.parents:
                if parent.exists() and not parent.is_dir():
                    raise FileExistsError(f'Local file blocks an archive directory: {parent}')
            if entry.is_dir():
                if target.exists() and not target.is_dir():
                    raise FileExistsError(f'Local file blocks an archive directory: {target}')
                continue
            data = archive.read(entry)
            if target.exists() and (not target.is_file() or target.read_bytes() != data):
                raise FileExistsError(f'Local edits preserved; extract into an empty folder: {target}')
            entries.append((target, data))
        file_targets = {target for target, _ in entries}
        if any(parent in file_targets for target in file_targets for parent in target.parents):
            raise ValueError('An archive file also occupies another entry directory.')
        for target, data in entries:
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                target.write_bytes(data)


def package_powerbi(root=ROOT, source=None):
    root = Path(root)
    source = Path(source or root / 'powerbi')
    contents = {'powerbi/' + p.relative_to(source).as_posix(): p.read_bytes() for p in source.rglob('*')
                if p.is_file() and '.pbi' not in p.relative_to(source).parts}
    if 'powerbi/FinancialPerformance.pbip' not in contents:
        raise FileNotFoundError('Build or extract the Power BI project before packaging it.')
    write_archive(contents, root / POWERBI_ARCHIVE)
    print(f'Power BI package: {len(contents)} native files, paths and bytes preserved.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['extract', 'package'])
    parser.add_argument('--archive', type=Path, default=ROOT / POWERBI_ARCHIVE)
    parser.add_argument('--destination', type=Path, default=ROOT)
    args = parser.parse_args()
    if args.action == 'extract':
        extract_archive(args.archive, args.destination)
        print(f'Extracted into {args.destination}; open powerbi/FinancialPerformance.pbip.')
    else:
        package_powerbi()
