import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def build_preview(root=ROOT):
    root=Path(root)
    from refresh_dashboard import refresh_dashboard
    data=refresh_dashboard(root/"data")
    text=(root/"scripts/templates/index.html").read_text(encoding="utf-8")
    replacements={"__DATA__":json.dumps(data,ensure_ascii=False).replace("<","\\u003c"),
                  "__STYLE__":(root/"preview/style.css").read_text(encoding="utf-8"),
                  "__FINANCE__":(root/"preview/finance.js").read_text(encoding="utf-8"),
                  "__ADVANCED__":(root/"preview/advanced.js").read_text(encoding="utf-8"),
                  "__APP__":(root/"preview/app.js").read_text(encoding="utf-8")}
    for token,value in replacements.items():text=text.replace(token,value)
    (root/"preview/index.html").write_text(text,encoding="utf-8")
    print("Prévia criada: sete perspectivas, filtros locais, dados embarcados.")
if __name__=="__main__":build_preview()
