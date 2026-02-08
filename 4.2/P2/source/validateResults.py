#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
validate_p2_results.py

Valida P2 (convertNumbers) comparando:
  - ConvertionResults.txt         (tus resultados)
  - A4.2.P2.Results.txt           (esperados)

• Detecta secciones por: "=== tests/TCx.txt ... ==="
• Soporta dos layouts en resultados:
    (A) Tabla con tuberías: "line | dec | bin | hex" (una línea por registro)
    (B) Bloques de 4 líneas: line, dec, bin, hex (como versiones anteriores)
• ACEPTA 'Decimal' no numérico (p. ej., ABC/ERR/VAL) cuando BIN/HEX son "#VALUE!".
• Normaliza '#VALUE\\!' -> '#VALUE!'
• Solo reporta mismatches por TC; si todo coincide: "[TCx] OK"

Uso:
  python validate_p2_results.py [--debug]
"""

import os
import re
import sys

YOUR_RESULTS_PATH = "results/ConvertionResults.txt"
EXPECTED_PATH     = "tests/A4.2.P2.Results.txt"

DEBUG = ("--debug" in sys.argv)

def dbg(msg):
    if DEBUG:
        print(f"[DEBUG] {msg}")

# ---------------- Normalización ----------------
def norm_val(s: str) -> str:
    if s is None:
        return ""
    s = s.strip()
    s = s.replace("\\!", "!")  # '#VALUE\!' -> '#VALUE!'
    return s.upper()           # Comparar HEX en mayúsculas

# ---------------- Utilidades ----------------
def is_bin_or_value(x: str) -> bool:
    xs = x.strip().upper()
    if xs == "#VALUE!":
        return True
    return all(ch in "01" for ch in xs)

def is_hex_or_value(x: str) -> bool:
    xs = x.strip().upper()
    if xs == "#VALUE!":
        return True
    return all(ch in "0123456789ABCDEF" for ch in xs)

def is_rule_or_total_or_header_line(s: str) -> bool:
    up = s.upper()
    if up.startswith("LINE") and "DECIMAL" in up and "BINARY" in up and "HEX" in up:
        return True
    if up.startswith("TOTAL VALID ITEMS:") or up.startswith("ELAPSED TIME"):
        return True
    # línea de regla: guiones/+, | y espacios
    if set(s) <= set("-+| "):
        return True
    return False

# ---------------- Parser: tus resultados ----------------
HEADER_RE = re.compile(r"^===\s*tests/(TC\d+)\.txt.*?===\s*$", re.MULTILINE)

def parse_user_sections(text: str):
    """
    Detecta secciones por encabezado laxo y, dentro de cada una:
      1) Intenta parseo 'tabla con |'
      2) Si no hay filas, intenta parseo 'bloques de 4 líneas'
    Devuelve:
      dict[tc] = [{line:int, dec:str, bin:str, hex:str}, ...]
    """
    sections = []
    for m in HEADER_RE.finditer(text):
        sections.append((m.group(1), m.end()))
    dbg(f"Secciones detectadas en resultados: {len(sections)}")

    if not sections:
        return {}

    sections_with_end = []
    for i, (tc, start) in enumerate(sections):
        end = sections[i+1][1] if i+1 < len(sections) else len(text)
        sections_with_end.append((tc, start, end))

    results = {}
    for tc, start, end in sections_with_end:
        body = text[start:end]
        rows = parse_user_rows_pipe_table(body)
        if rows:
            results[tc] = rows
            dbg(f"{tc}: filas capturadas (tabla con |) = {len(rows)}")
            continue
        rows = parse_user_rows_block4(body)
        if rows:
            results[tc] = rows
            dbg(f"{tc}: filas capturadas (bloques x4) = {len(rows)}")
        else:
            dbg(f"{tc}: sin filas capturadas")
    return results

def parse_user_rows_pipe_table(body: str):
    """
    Parser para tabla con tuberías:
      "   1  |  6980368  |  1101...  |  6A8310"
    Ignora encabezados/reglas/totales.

    *** Cambio clave: NO exigimos que 'Decimal' sea numérico. ***
    Se permite 'ABC', 'ERR', 'VAL', etc., siempre que BIN/HEX sean válidos
    (binario o '#VALUE!'), tal como ocurre en TC4.  (ConvertionResults.txt) [1](https://tecmx-my.sharepoint.com/personal/a01796323_tec_mx/Documents/Archivos%20de%20Microsoft%C2%A0Copilot%20Chat/ConvertionResults.txt)
    """
    rows = []
    for ln in body.splitlines():
        line = ln.rstrip()
        if not line.strip():
            continue
        if is_rule_or_total_or_header_line(line.strip()):
            continue
        if "|" not in line:
            continue

        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 4:
            continue
        # Toma las 4 últimas columnas por robustez
        a, b, c, d = [p.strip() for p in parts[-4:]]

        # Validaciones:
        # - 'Line' sí debe ser entero
        if not a.lstrip("+-").isdigit():
            continue
        # - 'Decimal' puede ser numérico o no (ABC/ERR/VAL…), así que NO filtramos.
        # - 'Binary' y 'Hex' deben ser binarios o '#VALUE!'
        if not is_bin_or_value(c):
            continue
        if not is_hex_or_value(d):
            continue

        try:
            line_no = int(a)
        except Exception:
            line_no = None

        rows.append({
            "line": line_no,
            "dec": b,
            "bin": c,
            "hex": d
        })
    return rows

def parse_user_rows_block4(body: str):
    """
    Parser alterno para bloques de 4 líneas (line, dec, bin, hex)
    cuando no hay tabla con tuberías.

    *** Cambio clave: NO exigimos que 'Decimal' sea numérico. ***
    Igual que arriba, se acepta cualquier token en 'Decimal' si BIN/HEX son válidos.
    """
    raw_lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
    data_lines = [ln for ln in raw_lines if not is_rule_or_total_or_header_line(ln)]
    rows = []
    i = 0
    while i + 3 < len(data_lines):
        a, b, c, d = data_lines[i], data_lines[i+1], data_lines[i+2], data_lines[i+3]
        # 'a' debe ser entero; 'b' (Decimal) puede ser cualquier token;
        # 'c' y 'd' deben ser binario/HEX o '#VALUE!'
        if a.lstrip("+-").isdigit() and is_bin_or_value(c) and is_hex_or_value(d):
            try:
                line_no = int(a)
            except Exception:
                line_no = None
            rows.append({"line": line_no, "dec": b.strip(), "bin": c.strip(), "hex": d.strip()})
            i += 4
        else:
            i += 1
    return rows

# ---------------- Parser: esperados ----------------
def parse_expected_sections(text: str):
    """
    A4.2.P2.Results.txt:
      ITEM  TC1  BIN  HEX
      <rows>
      ITEM  TC2  BIN  HEX
      <rows>
      ITEM  TC3  BIN  HEX
      <rows>
      ITEM  TC4  BIN  HEX
      <rows>

    Devuelve dict[tc] = [{line, dec, bin, hex}...]
    (El archivo que compartiste trae ese formato por TC, incluyendo TC4 con ABC/ERR/VAL) [2](https://tecmx-my.sharepoint.com/personal/a01796323_tec_mx/Documents/Archivos%20de%20Microsoft%C2%A0Copilot%20Chat/A4.2.P2.Results.txt)
    """
    lines = [ln.rstrip() for ln in text.splitlines() if ln.strip()]
    results = {}
    current_tc = None

    header_re = re.compile(r"^ITEM\s+TC(\d+)\s+BIN\s+HEX\b", re.IGNORECASE)
    row_re    = re.compile(r"^\s*(\d+)\s+([\-A-Za-z0-9]+)\s+([#A-Za-z0-9!]+)\s+([#A-Za-z0-9!\\]+)\s*$")

    for ln in lines:
        m_hdr = header_re.match(ln)
        if m_hdr:
            tc = "TC" + m_hdr.group(1)
            current_tc = tc
            results[current_tc] = []
            continue

        if current_tc:
            m_row = row_re.match(ln)
            if m_row:
                idx   = int(m_row.group(1))
                dec   = m_row.group(2)
                bin_s = m_row.group(3)
                hex_s = m_row.group(4)
                results[current_tc].append({
                    "line": idx,
                    "dec": dec,
                    "bin": bin_s,
                    "hex": hex_s
                })
    return results

# ---------------- Comparación ----------------
def compare_tc(tc, user_rows, exp_rows):
    """
    Compara por índice (1..N). Si difiere el total, se reporta.
    Retorna lista de mismatches:
      [{line: idx|COUNT_MISMATCH, problems:[(field, expected, got), ...]}, ...]
    """
    diffs = []
    n_user = len(user_rows)
    n_exp  = len(exp_rows)
    n = min(n_user, n_exp)

    for i in range(n):
        u = user_rows[i]
        e = exp_rows[i]
        u_dec, u_bin, u_hex = norm_val(u["dec"]), norm_val(u["bin"]), norm_val(u["hex"])
        e_dec, e_bin, e_hex = norm_val(e["dec"]), norm_val(e["bin"]), norm_val(e["hex"])

        mismatch = []
        if u_dec != e_dec:
            mismatch.append(("DEC", e_dec, u_dec))
        if u_bin != e_bin:
            mismatch.append(("BIN", e_bin, u_bin))
        if u_hex != e_hex:
            mismatch.append(("HEX", e_hex, u_hex))

        if mismatch:
            diffs.append({"line": i+1, "problems": mismatch})

    if n_user != n_exp:
        diffs.append({"line": "COUNT_MISMATCH",
                      "problems": [("ROWS", str(n_exp), str(n_user))]})

    return diffs

# ---------------- Main ----------------
def main():
    # Cargar archivos
    if not os.path.exists(YOUR_RESULTS_PATH):
        print(f"[FATAL] No se encontró tu archivo: {YOUR_RESULTS_PATH}", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(EXPECTED_PATH):
        print(f"[FATAL] No se encontró el archivo de esperados: {EXPECTED_PATH}", file=sys.stderr)
        sys.exit(1)

    with open(YOUR_RESULTS_PATH, "r", encoding="utf-8") as f:
        your_text = f.read()
    with open(EXPECTED_PATH, "r", encoding="utf-8") as f:
        exp_text = f.read()

    # Parsear resultados y esperados
    # ConvertionResults.txt: secciones + tabla con '|' o bloques x4  [1](https://tecmx-my.sharepoint.com/personal/a01796323_tec_mx/Documents/Archivos%20de%20Microsoft%C2%A0Copilot%20Chat/ConvertionResults.txt)
    # A4.2.P2.Results.txt: tablas por TC (ITEM TCx BIN HEX)           [2](https://tecmx-my.sharepoint.com/personal/a01796323_tec_mx/Documents/Archivos%20de%20Microsoft%C2%A0Copilot%20Chat/A4.2.P2.Results.txt)
    your = parse_user_sections(your_text)
    exp  = parse_expected_sections(exp_text)

    tcs = sorted(set(your.keys()).intersection(set(exp.keys())))
    dbg(f"TCs comunes: {tcs}")

    any_diff = False
    print("=== Validation of P2 Conversions (only mismatches) ===\n")

    if not tcs:
        print("[ERROR] No se encontraron TCs comunes entre tus resultados y los esperados.")
        print("Revisa el encabezado '=== tests/TCx.txt ... ===' y el formato de filas (tabla con | o bloques x4).")
        sys.exit(1)

    for tc in tcs:
        diffs = compare_tc(tc, your[tc], exp[tc])
        if diffs:
            any_diff = True
            print(f"[{tc}] Mismatches:")
            for d in diffs:
                line = d["line"]
                for (field, e_val, u_val) in d["problems"]:
                    print(f"  - Line {line:>3}: {field} expected={e_val}  got={u_val}")
            print()
        else:
            print(f"[{tc}] OK\n")

    # Reportar TCs que sobran/faltan
    only_user = sorted(set(your.keys()) - set(exp.keys()))
    only_exp  = sorted(set(exp.keys()) - set(your.keys()))
    if only_user:
        any_diff = True
        for tc in only_user:
            print(f"[{tc}] solo existe en tus resultados; no existe en esperados.")
    if only_exp:
        any_diff = True
        for tc in only_exp:
            print(f"[{tc}] solo existe en esperados; no existe en tus resultados.")

    print("\n=== Validation Completed ===")
    print("Overall:", "PASS ✅" if not any_diff else "FAIL ❌")
    sys.exit(0 if not any_diff else 1)

if __name__ == "__main__":
    main()