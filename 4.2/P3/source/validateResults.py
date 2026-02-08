#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
validate_wordcount.py

Valida WordCount comparando:
  - WordCountResults.txt  (reporte consolidado por secciones TCx)
  - TCx.Results.txt       (archivos de esperados por TC, estilo tabla dinámica)

Reglas:
  - Orden NO importa.
  - Verificar que TODAS las palabras esperadas estén en tus resultados con el CONTEO esperado.
  - Verificar que "Total valid words" == Grand Total del esperado.
  - SOLO reportar mismatches:
      * palabra faltante
      * palabra con conteo distinto
      * total de palabras diferente

Salida:
  - Por cada TC encontrado en ambos lados:
      * "OK" si todo coincide
      * Lista de diferencias si hay mismatches
  - Exit code: 0 si todo OK; 1 si hubo diferencias.

El parser del reporte está adaptado al formato de:
  - "=== tests/TCx.txt — Word Count (Distinct Words & Frequencies) ==="
  - tabla verticalizada de Word / Frequency
  - renglón "Total valid words: N"
(estructura observada en tu WordCountResults.txt)  # cite turn54search1

El parser de esperados está adaptado al formato de:
  - "Row Labels<TAB>Count of TCx"
  - "<palabra><TAB><conteo>"
  - "Grand Total<TAB>n"
(estructura observada en TC1.Results.txt)  # cite turn54search2
"""

import argparse
import glob
import os
import re
import sys
from collections import defaultdict

# ------------------------------ DEBUG ------------------------------
DEBUG_LEVEL = 0
def dbg(level, msg):
    if DEBUG_LEVEL >= level:
        print(f"[DEBUG{level}] {msg}")

# ------------------------------ Parser de TU reporte ------------------------------
# Formato real (secciones por TC) como el de WordCountResults.txt adjunto:
# "=== tests/TC1.txt — Word Count (Distinct Words & Frequencies) ==="
# Columnas: Word / Frequency verticalizado por filas; al final:
# "Total valid words: N"
#
# Referencia: ver archivo adjunto WordCountResults.txt.  # [1](https://tecmx-my.sharepoint.com/personal/a01796323_tec_mx/Documents/Archivos%20de%20Microsoft%C2%A0Copilot%20Chat/WordCountResults.txt)

SEC_HDR_RE = re.compile(r"^===\s*tests/(TC\d+)\.txt\s+—\s+Word Count.*===$", re.MULTILINE)


def parse_user_results(results_path):
    """
    Lee WordCountResults.txt y extrae, por cada TC:
      - dict word -> frequency
      - total valid words
    Soporta DOS layouts dentro de la sección:
      (A) Tabla con tuberías: "No. | Word | Frequency"  (una línea por registro)
      (B) Layout verticalizado: pares (Word, Frequency) en líneas separadas
    """
    if not os.path.exists(results_path):
        print(f"[FATAL] No se encontró tu archivo de resultados: {results_path}", file=sys.stderr)
        sys.exit(1)

    with open(results_path, "r", encoding="utf-8") as f:
        text = f.read()

    # 1) Secciones TCx
    sections = []
    for m in SEC_HDR_RE.finditer(text):
        sections.append((m.group(1), m.end()))
    dbg(1, f"Secciones TC detectadas en {os.path.basename(results_path)}: {[tc for tc,_ in sections]}")
    if not sections:
        print("[FATAL] No se detectaron secciones TCx en tu WordCountResults.txt", file=sys.stderr)
        sys.exit(1)

    # 2) Cuerpos
    tc_to_body = {}
    for i, (tc, start) in enumerate(sections):
        end = sections[i+1][1] if i+1 < len(sections) else len(text)
        tc_to_body[tc] = text[start:end]

    out = {}
    for tc, body in tc_to_body.items():
        words = {}
        total_valid = None

        # 2.1 Total
        m_tot = re.search(r"Total valid words:\s*(\d+)", body)
        if m_tot:
            total_valid = int(m_tot.group(1))
            dbg(2, f"[{tc}] Total valid words leído: {total_valid}")
        else:
            dbg(1, f"[{tc}] WARNING: No se encontró 'Total valid words:' en la sección")

        # 2.2 Extraer bloque de datos (desde encabezado Word|Frequency hasta 'Total valid words')
        lines = [ln.rstrip() for ln in body.splitlines()]
        hdr_idx = -1
        for idx, ln in enumerate(lines):
            if "Word" in ln and "Frequency" in ln:
                hdr_idx = idx
                break

        if hdr_idx == -1:
            dbg(1, f"[{tc}] WARNING: No se halló encabezado 'Word'/'Frequency'; intento de parseo laxo.")
            data_lines_all = [ln.strip() for ln in lines]
        else:
            dbg(3, f"[{tc}] Índice encabezado Word/Frequency: {hdr_idx}")
            data_lines_all = [ln.strip() for ln in lines[hdr_idx+1:]]

        # Cortar por 'Total valid words'
        cut_idx = len(data_lines_all)
        for i, ln in enumerate(data_lines_all):
            if ln.startswith("Total valid words:"):
                cut_idx = i
                break
        data_lines_all = data_lines_all[:cut_idx]

        # Filtrar ruido (reglas, encabezados, líneas vacías)
        def is_rule_or_noise(s: str) -> bool:
            if not s:
                return True
            if set(s) <= set("-+|\\ "):  # regla "-----+-----"
                return True
            if s.lower().startswith("no.") or s.lower().startswith("word") or s.lower().startswith("frequency"):
                return True
            return False

        payload = [ln for ln in data_lines_all if not is_rule_or_noise(ln)]
        dbg(3, f"[{tc}] Líneas útiles después de filtrar: {len(payload)}")
        if DEBUG_LEVEL >= 3:
            preview = "\n      ".join(payload[:12])
            dbg(3, f"[{tc}] Preview payload (hasta 12):\n      {preview}")

        # 2.3 PRIMER intento: parsear "tabla con tuberías" (No. | Word | Frequency)
        pipe_rows = []
        for ln in payload:
            if "|" in ln:
                # tomar las 3 últimas columnas por robustez
                parts = [p.strip() for p in ln.split("|")]
                if len(parts) >= 3:
                    no_s, word_s, freq_s = parts[-3], parts[-2], parts[-1]
                    # 'no' puede o no ser entero; 'freq' debe ser entero
                    if freq_s.isdigit() and word_s:
                        pipe_rows.append((word_s, int(freq_s)))
        if pipe_rows:
            for w, c in pipe_rows:
                words[w] = c
            dbg(2, f"[{tc}] Palabras capturadas (por tuberías): {len(pipe_rows)}")
            if DEBUG_LEVEL >= 3:
                dbg(3, f"[{tc}] Muestra 10 (pipe): {pipe_rows[:10]}")
            out[tc] = {"words": words, "total": total_valid}
            continue  # ya parseamos por tuberías, pasamos a la siguiente sección

        # 2.4 SEGUNDO intento (fallback): pares verticalizados (Word en una línea, Frequency en la siguiente)
        i = 0
        used_pairs = 0
        while i < len(payload):
            ln = payload[i].strip()
            # Saltar numeración sola (por si apareciera)
            if ln.isdigit():
                i += 1
                continue
            # LN = palabra
            w = ln
            # Siguiente debe ser frecuencia
            if i + 1 < len(payload) and payload[i+1].strip().isdigit():
                c = int(payload[i+1].strip())
                words[w] = c
                used_pairs += 1
                i += 2
            else:
                i += 1

        dbg(2, f"[{tc}] Palabras capturadas (verticalizado): {len(words)} (pares válidos={used_pairs})")
        if DEBUG_LEVEL >= 3:
            sample = list(words.items())[:10]
            dbg(3, f"[{tc}] Muestra 10 (vertical): {sample}")

        out[tc] = {"words": words, "total": total_valid}

    return out

# === El resto del script (carga de esperados, compare_tc, main, etc.) queda igual al que ya tienes con --debug. ===

# ------------------------------ Parser de ESPERADOS por TC ------------------------------
# Formato real: "Row Labels<TAB>Count of TC1"  y filas  "palabra<TAB>conteo"
# con "Grand Total<TAB>n" al final. (Ejemplo: TC1.Results.txt)  # [2](https://tecmx-my.sharepoint.com/personal/a01796323_tec_mx/Documents/Archivos%20de%20Microsoft%C2%A0Copilot%20Chat/TC1.Results.txt)

def parse_expected_file(exp_path):
    if not os.path.exists(exp_path):
        raise FileNotFoundError(exp_path)
    with open(exp_path, "r", encoding="utf-8") as f:
        raw = f.read()

    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    words = {}
    grand_total = None

    for ln in lines:
        parts = re.split(r"\t+", ln)
        if len(parts) < 2:
            continue
        key = parts[0].strip()
        val = parts[1].strip()
        if key.lower().startswith("row labels"):
            continue
        if key.lower() == "grand total":
            try:
                grand_total = int(val)
            except Exception:
                grand_total = None
            continue
        try:
            cnt = int(val)
        except Exception:
            # (blank) u otras filas no numéricas se ignoran
            continue
        if key:
            words[key] = cnt

    return words, grand_total


def load_expected_from_dir(expected_dir, pattern):
    paths = sorted(glob.glob(os.path.join(expected_dir, pattern)))
    tc_map = {}
    for p in paths:
        base = os.path.basename(p)
        m = re.match(r"^(TC\d+)\.Results\.txt$", base, flags=re.IGNORECASE)
        if not m:
            m = re.match(r"^(TC\d+)\.results\.txt$", base, flags=re.IGNORECASE)
        if not m:
            continue
        tc = m.group(1).upper()
        words, grand_total = parse_expected_file(p)
        tc_map[tc] = {"words": words, "total": grand_total, "path": p}
        dbg(2, f"[{tc}] Esperados: {len(words)} palabras, Grand Total={grand_total}, file={base}")
    return tc_map


# ------------------------------ Comparación ------------------------------
def compare_tc(tc, your_tc_data, exp_tc_data, max_list=20):
    """
    Compara:
      - cada palabra esperada está en tus resultados con el MISMO conteo
      - total de palabras
    Devuelve (ok:bool, mismatches:list[str])
    """
    mismatches = []

    your_words = your_tc_data.get("words", {}) or {}
    your_total = your_tc_data.get("total", None)

    exp_words  = exp_tc_data.get("words", {}) or {}
    exp_total  = exp_tc_data.get("total", None)

    dbg(2, f"[{tc}] Comparando: yours={len(your_words)} palabras, total={your_total} vs exp={len(exp_words)}, total={exp_total}")

    # 1) Palabras esperadas: faltantes o conteos distintos
    missing = []
    wrong   = []
    for w, cnt_exp in exp_words.items():
        cnt_yours = your_words.get(w)
        if cnt_yours is None:
            missing.append((w, cnt_exp))
        elif cnt_yours != cnt_exp:
            wrong.append((w, cnt_exp, cnt_yours))

    # Log resumido
    if missing:
        m_show = ", ".join([f"{w}({c})" for w,c in missing[:max_list]])
        more = "" if len(missing) <= max_list else f" ... (+{len(missing)-max_list} más)"
        dbg(2, f"[{tc}] FALTAN {len(missing)} palabras esperadas: {m_show}{more}")
    if wrong:
        w_show = ", ".join([f"{w}(exp={e},got={g})" for w,e,g in wrong[:max_list]])
        more = "" if len(wrong) <= max_list else f" ... (+{len(wrong)-max_list} más)"
        dbg(2, f"[{tc}] CONTEO distinto en {len(wrong)} palabras: {w_show}{more}")

    for w, cexp in missing:
        mismatches.append(f"Missing word: '{w}' (expected {cexp}, got MISSING)")
    for w, cexp, cy in wrong:
        mismatches.append(f"Count mismatch: '{w}' (expected {cexp}, got {cy})")

    # 2) Total valid words
    if exp_total is not None and your_total is not None and your_total != exp_total:
        mismatches.append(f"Total valid words mismatch (expected {exp_total}, got {your_total})")
        dbg(2, f"[{tc}] Total mismatch: expected {exp_total} vs got {your_total}")

    return (len(mismatches) == 0), mismatches


# ------------------------------ Main ------------------------------
def main():
    global DEBUG_LEVEL

    parser = argparse.ArgumentParser(description="Validate WordCount results vs. expected files")
    parser.add_argument("--results", required=True, help="Ruta al WordCountResults.txt consolidado")
    parser.add_argument("--expected-dir", default=".", help="Carpeta con TC*.Results.txt")
    parser.add_argument("--pattern", default="TC*.Results.txt", help='Patrón glob para esperados (p. ej., "TC*.Results.txt")')
    parser.add_argument("--expected", nargs="*", help="Lista explícita de archivos esperados (opcional)")
    parser.add_argument("--only", nargs="*", help="Validar solo estos TCs (p. ej., --only TC1 TC3)")
    parser.add_argument("--debug", nargs="?", const="1", default="0",
                        help="Nivel de debug: 0=off, 1=básico, 2=detallado, 3=muy verboso")

    args = parser.parse_args()
    try:
        DEBUG_LEVEL = int(args.debug or "1")
    except Exception:
        DEBUG_LEVEL = 1

    dbg(1, f"Args: results={args.results}, expected-dir={args.expected_dir}, pattern={args.pattern}, expected={args.expected}, only={args.only}, debug={DEBUG_LEVEL}")

    # 1) Cargar TU reporte consolidado
    your_map = parse_user_results(args.results)  # [1](https://tecmx-my.sharepoint.com/personal/a01796323_tec_mx/Documents/Archivos%20de%20Microsoft%C2%A0Copilot%20Chat/WordCountResults.txt)
    dbg(1, f"TUs TCs disponibles: {sorted(your_map.keys())}")

    # 2) Cargar ESPERADOS (por dir/patrón o por lista explícita)
    if args.expected:
        exp_map = {}
        for p in args.expected:
            words, total = parse_expected_file(p)  # [2](https://tecmx-my.sharepoint.com/personal/a01796323_tec_mx/Documents/Archivos%20de%20Microsoft%C2%A0Copilot%20Chat/TC1.Results.txt)
            base = os.path.basename(p)
            m = re.match(r"^(TC\d+)\.", base, flags=re.IGNORECASE)
            if not m:
                print(f"[WARN] No pude inferir TC de: {p}. Se omite.", file=sys.stderr)
                continue
            tc = m.group(1).upper()
            exp_map[tc] = {"words": words, "total": total, "path": p}
            dbg(2, f"[{tc}] Esperados desde lista: {len(words)} palabras, Grand Total={total}, file={base}")
    else:
        exp_map = load_expected_from_dir(args.expected_dir, args.pattern)  # [2](https://tecmx-my.sharepoint.com/personal/a01796323_tec_mx/Documents/Archivos%20de%20Microsoft%C2%A0Copilot%20Chat/TC1.Results.txt)

    if not exp_map:
        print("[FATAL] No se encontraron archivos de esperados.", file=sys.stderr)
        sys.exit(1)

    dbg(1, f"TCs con esperados: {sorted(exp_map.keys())}")

    # 3) Determinar TCs a validar
    tcs_common = sorted(set(your_map.keys()).intersection(set(exp_map.keys())))
    if args.only:
        only_up = {tc.upper() for tc in args.only}
        tcs_common = [tc for tc in tcs_common if tc in only_up]
        dbg(1, f"Filtrado por --only: {tcs_common}")

    if not tcs_common:
        print("[ERROR] No hay TCs comunes entre tu reporte y los esperados (o filtrados por --only).", file=sys.stderr)
        sys.exit(1)

    any_diff = False
    print("=== Validation of WordCount (only mismatches) ===\n")

    for tc in tcs_common:
        ok, mismatches = compare_tc(tc, your_map[tc], exp_map[tc])
        if mismatches:
            any_diff = True
            exp_name = os.path.basename(exp_map[tc]['path']) if 'path' in exp_map[tc] else 'N/A'
            print(f"[{tc}] Mismatches (expected file: {exp_name}):")
            for m in mismatches:
                print(f"  - {m}")
            print()
        else:
            print(f"[{tc}] OK")

    # Reportar TCs que sobran/faltan
    only_your = sorted(set(your_map.keys()) - set(exp_map.keys()))
    only_exp  = sorted(set(exp_map.keys()) - set(your_map.keys()))
    if only_your:
        any_diff = True
        for tc in only_your:
            print(f"[{tc}] solo está en tus resultados; no existe archivo esperado.")
    if only_exp:
        any_diff = True
        for tc in only_exp:
            print(f"[{tc}] solo existe archivo esperado; no aparece en tu WordCountResults.txt.")

    print("\n=== Validation Completed ===")
    print("Overall:", "PASS ✅" if not any_diff else "FAIL ❌")
    sys.exit(0 if not any_diff else 1)

if __name__ == "__main__":
    main()