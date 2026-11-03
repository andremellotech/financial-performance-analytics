"""Reconstrói os materiais de texto e valida a mesma base de entrada."""
from pathlib import Path
import tempfile
from generate_data import build_data
from validate_data import validate_dataset
from build_powerbi import build_powerbi
from validate_powerbi import validate_powerbi
from build_preview import build_preview
from build_docs import build_docs
from package_assets import package_powerbi
ROOT=Path(__file__).resolve().parents[1]
if __name__=="__main__":
    validate_dataset(ROOT/"data")
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory)/"powerbi"
        build_powerbi(ROOT/"data",output)
        validate_powerbi(output)
        package_powerbi(ROOT,output)
    build_preview(ROOT)
    build_docs()
    print("Materiais gerados e validados; Excel mantém a base/fórmulas da entrega.")
