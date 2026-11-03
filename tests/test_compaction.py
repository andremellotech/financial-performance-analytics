import importlib.util
import json
import re
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))


class CompactAssetsTests(unittest.TestCase):
    def api(self, module):
        self.assertIsNotNone(importlib.util.find_spec(module), f'{module} tooling is missing')
        return __import__(module)

    def test_archive_roundtrip_preserves_bytes_and_paths_deterministically(self):
        assets = self.api('package_assets')
        contents = {'powerbi/nested/report.json': b'{"name":"original"}\r\n', 'powerbi/model.bin': bytes(range(256))}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first, second = root / 'first.zip', root / 'second.zip'
            assets.write_archive(contents, first)
            assets.write_archive(dict(reversed(list(contents.items()))), second)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            assets.extract_archive(first, root / 'extracted')
            self.assertEqual({p.relative_to(root / 'extracted').as_posix(): p.read_bytes() for p in (root / 'extracted').rglob('*') if p.is_file()}, contents)

    def test_extraction_rejects_traversal_and_preserves_local_edits(self):
        assets = self.api('package_assets')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ('../outside', '/outside', 'C:/outside', 'powerbi/../../outside', 'powerbi\\..\\outside'):
                with zipfile.ZipFile(root / 'bad.zip', 'w') as archive:
                    archive.writestr(name, b'bad')
                with self.assertRaises(ValueError, msg=name):
                    assets.extract_archive(root / 'bad.zip', root / 'out')
            assets.write_archive({'powerbi/a.txt': b'new', 'powerbi/z.txt': b'original'}, root / 'valid.zip')
            (root / 'out/powerbi').mkdir(parents=True)
            (root / 'out/powerbi/z.txt').write_bytes(b'local edit')
            with self.assertRaises(FileExistsError):
                assets.extract_archive(root / 'valid.zip', root / 'out')
            self.assertFalse((root / 'out/powerbi/a.txt').exists(), 'preflight must prevent partial extraction')
            self.assertEqual((root / 'out/powerbi/z.txt').read_bytes(), b'local edit')

    def test_extraction_preflights_parent_files_before_any_write(self):
        assets = self.api('package_assets')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            assets.write_archive({'powerbi/a.txt': b'new', 'powerbi/z/nested.txt': b'nested'}, root / 'assets.zip')
            (root / 'out/powerbi').mkdir(parents=True)
            (root / 'out/powerbi/z').write_bytes(b'local file')
            with self.assertRaises(FileExistsError):
                assets.extract_archive(root / 'assets.zip', root / 'out')
            self.assertFalse((root / 'out/powerbi/a.txt').exists(), 'conflicting parent must fail before any write')
            self.assertEqual((root / 'out/powerbi/z').read_bytes(), b'local file')

    def test_packaging_retains_report_resources_and_excludes_native_cache(self):
        assets = self.api('package_assets')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            assets.extract_archive(ROOT / 'downloads/FinancialPerformance-PowerBI.zip', root)
            image = root / 'powerbi/FinancialPerformance.Report/StaticResources/logo.png'
            image.parent.mkdir(parents=True)
            image.write_bytes(b'\x89PNG\r\noriginal resource')
            cache = root / 'powerbi/FinancialPerformance.SemanticModel/.pbi/cache.abf'
            cache.parent.mkdir(parents=True)
            cache.write_bytes(b'local cache')
            assets.package_powerbi(root)
            with zipfile.ZipFile(root / 'downloads/FinancialPerformance-PowerBI.zip') as archive:
                self.assertIn('powerbi/FinancialPerformance.Report/StaticResources/logo.png', archive.namelist())
                self.assertEqual(archive.read('powerbi/FinancialPerformance.Report/StaticResources/logo.png'), image.read_bytes())
                self.assertNotIn('powerbi/FinancialPerformance.SemanticModel/.pbi/cache.abf', archive.namelist())

    def test_native_download_is_complete_and_schema_valid(self):
        self.api('package_assets')
        from validate_powerbi import validate_powerbi
        with zipfile.ZipFile(ROOT / 'downloads/FinancialPerformance-PowerBI.zip') as archive:
            self.assertIsNone(archive.testzip())
            self.assertEqual(len(archive.namelist()), 111)
            self.assertIn('powerbi/FinancialPerformance.pbip', archive.namelist())
            self.assertIn('powerbi/FinancialPerformance.SemanticModel/definition/model.tmdl', archive.namelist())
        with tempfile.TemporaryDirectory() as directory:
            self.api('package_assets').extract_archive(ROOT / 'downloads/FinancialPerformance-PowerBI.zip', Path(directory))
            validate_powerbi(Path(directory) / 'powerbi')

    def test_pages_contains_only_runtime_downloads_and_resolves_links(self):
        site = self.api('build_site')
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / 'site'
            out.mkdir()
            (out / 'stale.txt').write_text('old artifact')
            site.build_site(ROOT, out)
            expected = {'index.html', 'preview/index.html', 'docs/user-guide.html', 'excel/FinancialPerformance.xlsx', 'data/fact_finance.csv', 'downloads/FinancialPerformance-PowerBI.zip', 'LICENSE'}
            self.assertEqual({p.relative_to(out).as_posix() for p in out.rglob('*') if p.is_file()}, expected)
            for page in out.rglob('*.html'):
                for link in re.findall(r'(?:href|src)=["\']([^"\']+)', page.read_text(encoding='utf-8')):
                    if link.startswith(('https:', 'http:', '#', 'data:', 'mailto:')):
                        continue
                    self.assertTrue((page.parent / link.split('#')[0]).resolve().is_file(), f'{page}: {link}')

    def test_docs_refresh_preserves_curated_readme_context(self):
        import build_docs
        from generate_data import build_data
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            build_data(root / 'data')
            (root / 'README.md').write_text((ROOT / 'README.md').read_text(encoding='utf-8') + '\nCurated portfolio context survives refresh.\n', encoding='utf-8')
            with patch.object(build_docs, 'ROOT', root):
                build_docs.build_docs()
            self.assertIn('Curated portfolio context survives refresh.', (root / 'README.md').read_text(encoding='utf-8'))
