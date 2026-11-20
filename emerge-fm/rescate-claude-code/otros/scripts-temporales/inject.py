# -*- coding: utf-8 -*-
import io, json

base = "C:/Users/farid/AppData/Local/Temp/claude/C--Users-farid-Desktop-claude-code/2650f179-0c9f-4e30-b201-228e19538865/scratchpad/"

with io.open(base + "data.json", encoding="utf-8") as f:
    data = json.load(f)

slim = [{k: d[k] for k in ("nombre", "rubro", "comuna", "direccion", "telefono", "web",
                           "P", "A", "R", "A2", "C", "score", "tier", "plan", "gancho")} for d in data]

with io.open(base + "report_template.html", encoding="utf-8") as f:
    html = f.read()

payload = json.dumps(slim, ensure_ascii=False, separators=(",", ":"))
assert "/*__DATA__*/[]" in html
html = html.replace("/*__DATA__*/[]", payload)

with io.open(base + "informe.html", "w", encoding="utf-8") as f:
    f.write(html)

print("OK", len(slim), "empresas |", len(html), "chars")
