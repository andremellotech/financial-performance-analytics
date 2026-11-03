"""Copy only the public site's runtime and download dependencies."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
SITE_FILES = (
    'index.html', 'preview/index.html', 'docs/user-guide.html',
    'excel/FinancialPerformance.xlsx', 'data/fact_finance.csv',
    'downloads/FinancialPerformance-PowerBI.zip', 'LICENSE',
)


def build_site(root=ROOT, destination=None):
    root = Path(root).resolve()
    destination = Path(destination or root / '_site').resolve()
    if destination == root or root.is_relative_to(destination) or any((root / name).is_relative_to(destination) for name in SITE_FILES):
        raise ValueError('Site output must not replace the repository or its parents.')
    for name in SITE_FILES:
        if not (root / name).is_file():
            raise FileNotFoundError(root / name)
    if destination.exists():
        shutil.rmtree(destination)
    for name in SITE_FILES:
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / name, target)
    print(f'Pages: {len(SITE_FILES)} files, {sum((destination / p).stat().st_size for p in SITE_FILES):,} bytes.')
    return destination


if __name__ == '__main__':
    build_site()
