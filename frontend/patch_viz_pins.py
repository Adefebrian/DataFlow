#!/usr/bin/env python3
"""
patch_viz_pins.py — Inject onPin/pinned into ALL Card components missing them.
Runs inside Docker build at /app/src/components/VisualizationsTab.tsx
"""
import os, sys

FILE = "/app/src/components/VisualizationsTab.tsx"
if not os.path.exists(FILE):
    print(f"SKIP: {FILE} not found", flush=True)
    sys.exit(0)

with open(FILE, "r", encoding="utf-8") as f:
    src = f.read()

original = src
applied = 0

def inject(src, search_title, subtype, title_expr, slice_expr):
    """Find <Card title="TITLE" ...> and inject onPin before the closing >."""
    global applied

    title_attr = f'title="{search_title}"'
    pos = src.find(title_attr)
    if pos == -1:
        print(f"  NOT FOUND: {search_title!r}", flush=True)
        return src

    # Walk backwards to find <Card
    card_pos = src.rfind('<Card', 0, pos)
    if card_pos == -1:
        print(f"  No <Card found before: {search_title}", flush=True)
        return src

    # Scan forward from card_pos to closing > of the props block (depth-aware)
    i = card_pos + 5
    depth = 0
    close_angle = -1
    while i < len(src) and i < card_pos + 6000:
        ch = src[i]
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
        elif ch == '>' and depth == 0:
            close_angle = i
            break
        i += 1

    if close_angle == -1:
        print(f"  Can't find closing > for: {search_title}", flush=True)
        return src

    card_block = src[card_pos:close_angle + 1]

    if 'onPin=' in card_block:
        print(f"  SKIP (already has onPin): {search_title}", flush=True)
        return src

    inject_str = (
        f"\n        onPin={{()=>pin({title_expr},'{subtype}',"
        f"{{{slice_expr},meta}})}} pinned={{hasItem(jobId,{title_expr})}}"
    )

    new_src = src[:close_angle] + inject_str + src[close_angle:]
    print(f"  \u2705 {search_title}", flush=True)
    applied += 1
    return new_src


# ── Complete list of ALL cards that need onPin ─────────────────────────────────
# Format: (card title, subtype key, title JS expression, slice keys)
CARDS = [
    # ── Core cards (previous session — safe to re-run, skips if already done) ──
    ("Category Ranking",        "ranking",      "`Ranking: ${rnkItem?.display_dimension}\u00d7${rnkItem?.display_metric}`", "ranking:rnk"),
    ("Outlier Analysis",        "outliers",     "`Outliers: ${outItem?.display_name}`",                                      "outlier_detail:out"),
    ("Cohort Analysis",         "cohort",       "`Cohort: ${cohItem?.display_row}\u00d7${cohItem?.display_col}`",            "cohort:coh"),
    ("Multi-Metric Comparison", "multi_metric", "`Multi-Metric: ${mmItem?.display_dimension}`",                             "multi_metric:mm"),
    ("Percentile Distribution", "percentile",   "`Percentiles: ${pctItem?.display_name}`",                                  "percentile_bands:pbd"),
    ("Pareto Analysis (80/20)", "pareto",       "`Pareto: ${prtItem?.display_dimension}\u00d7${prtItem?.display_metric}`",   "running_total:prt"),
    # ── 9 newly reported missing cards ──────────────────────────────────────────
    ("Statistical Risk Analysis",       "var",         "`Risk: ${item.display_name}`",                                                "value_at_risk:var_"),
    ("Market Concentration",            "concentration","`Concentration: ${item.display_dimension}\u00d7${item.display_metric}`",      "concentration:conc"),
    ("Frequency Analysis",              "frequency",   "`Frequency: ${item.display_name}`",                                           "frequency_analysis:fa"),
    ("Gauge / KPI vs Target",           "gauge",       "`Gauge: ${item.display_name}`",                                               "gauge:gd"),
    ("Slope / Before\u2013After",       "slope",       "`Slope: ${item.display_dimension}\u00d7${item.display_metric}`",               "slope_chart:sl"),
    ("Confidence Intervals (95% CI)",   "errorbars",   "`CI: ${item.display_dimension}\u00d7${item.display_metric}`",                  "error_bars:eb"),
    ("Marimekko / Mosaic Chart",        "marimekko",   "`Marimekko: ${item.display_dim1}\u00d7${item.display_dim2}`",                  "marimekko:mm_"),
    ("Flow / Sankey Diagram",           "sankey",      "`Sankey: ${item.display_source}\u2192${item.display_target}`",                 "sankey:sk"),
    ("Moving Average Analysis",         "moving",      "`Moving Avg: ${item.display_name}`",                                          "moving_statistics:ms"),
    # ── Belt-and-suspenders: previously patched but verify ─────────────────────
    ("Correlation Heatmap",             "heatmap",     "'Correlation Heatmap'",                                                        "correlation_matrix:cm"),
    ("Segment Radar",                   "radar",       "'Segment Radar'",                                                              "segments:segs"),
    # ── Extra cards found in source ─────────────────────────────────────────────
    ("Gantt / Timeline",                "gantt",       "`Gantt: ${item.display_start}\u2192${item.display_end}`",                       "gantt:gn"),
    ("Drill-Through Explorer",          "drill",       "`Drill: ${item.display_dimension}`",                                           "drill_through:dt"),
    ("Trend Decomposition",             "decomp",      "`Decomp: ${item.display_name}`",                                               "time_decomposition:td"),
    ("Industry Benchmark Comparison",   "benchmark",   "'Industry Benchmark Comparison'",                                              "benchmark_comparison:bm"),
    ("Column Quality Report",           "quality",     "'Column Quality Report'",                                                      "data_quality_detail:dq"),
    ("Descriptive Statistics",          "stats_table", "'Descriptive Statistics'",                                                     "summary_stats:ss"),
]

for title, subtype, title_expr, slice_expr in CARDS:
    src = inject(src, title, subtype, title_expr, slice_expr)

if src != original:
    with open(FILE, "w", encoding="utf-8") as f:
        f.write(src)
    print(f"\npatch_viz_pins: {applied} new cards patched \u2705", flush=True)
else:
    print(f"\npatch_viz_pins: no changes needed (all already patched)", flush=True)
