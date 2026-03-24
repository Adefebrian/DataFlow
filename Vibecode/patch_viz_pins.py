#!/usr/bin/env python3
"""
patch_viz_pins.py — Adds missing onPin/pinned props to ALL Card components in VisualizationsTab.tsx
Run from the Vibecode root: python3 patch_viz_pins.py
"""

import sys, os

FILE = "frontend/src/components/VisualizationsTab.tsx"

if not os.path.exists(FILE):
    print(f"ERROR: {FILE} not found. Run from the Vibecode root directory.")
    sys.exit(1)

with open(FILE, "r", encoding="utf-8") as f:
    src = f.read()

original_len = len(src)

# Each patch is (old_snippet, new_snippet)
# The old snippet must be a UNIQUE substring that appears exactly once.
patches = [
    # ─── Heatmap ──────────────────────────────────────────────────────────────
    (
        'icon={Grid} col={C.indigo} relevance={rv}\n        bar={<Sel opts={hmCols}',
        'icon={Grid} col={C.indigo} relevance={rv}\n        onPin={()=>pin(\'Correlation Heatmap\',\'heatmap\',{correlation_matrix:cm,meta})} pinned={hasItem(jobId,\'Correlation Heatmap\')}\n        bar={<Sel opts={hmCols}',
    ),
    # ─── Radar ────────────────────────────────────────────────────────────────
    (
        'icon={Eye} col={C.pink} relevance={rel(\'radar\',a)}>',
        'icon={Eye} col={C.pink} relevance={rel(\'radar\',a)}\n        onPin={()=>pin(\'Segment Radar\',\'radar\',{segments:segs,meta})} pinned={hasItem(jobId,\'Segment Radar\')}>',
    ),
    # ─── VaR ──────────────────────────────────────────────────────────────────
    (
        'col={item.risk_tier===\'High\'?C.coral:item.risk_tier===\'Medium\'?C.amber:C.green} relevance={rv}\n        bar={var_.length>1',
        'col={item.risk_tier===\'High\'?C.coral:item.risk_tier===\'Medium\'?C.amber:C.green} relevance={rv}\n        onPin={()=>pin(`Risk Analysis: ${item.display_name}`,\'var\',{value_at_risk:var_,meta})} pinned={hasItem(jobId,`Risk Analysis: ${item.display_name}`)}\n        bar={var_.length>1',
    ),
    # ─── Moving Stats ─────────────────────────────────────────────────────────
    (
        'icon={TrendingUp} col={C.cyan} relevance={rel(\'trend\',a)}\n        bar={ms.length>1',
        'icon={TrendingUp} col={C.cyan} relevance={rel(\'trend\',a)}\n        onPin={()=>pin(`Moving Avg: ${item.display_name}`,\'moving\',{moving_statistics:ms,meta})} pinned={hasItem(jobId,`Moving Avg: ${item.display_name}`)}\n        bar={ms.length>1',
    ),
    # ─── Concentration ────────────────────────────────────────────────────────
    (
        'icon={GitMerge} col={C.indigo} relevance={rv}\n        bar={conc.length>1',
        'icon={GitMerge} col={C.indigo} relevance={rv}\n        onPin={()=>pin(`Concentration: ${item.display_dimension}`,\'concentration\',{concentration:conc,meta})} pinned={hasItem(jobId,`Concentration: ${item.display_dimension}`)}\n        bar={conc.length>1',
    ),
    # ─── Benchmark ────────────────────────────────────────────────────────────
    (
        'icon={Award} col={C.green} relevance={\'Strong\'}>',
        'icon={Award} col={C.green} relevance={\'Strong\'}\n        onPin={()=>pin(\'Industry Benchmark Comparison\',\'benchmark\',{benchmark_comparison:bm,meta})} pinned={hasItem(jobId,\'Industry Benchmark Comparison\')}>',
    ),
    # ─── Quality Detail ───────────────────────────────────────────────────────
    (
        'icon={ShieldAlert} col={C.green} relevance={\'Strong\'}>',
        'icon={ShieldAlert} col={C.green} relevance={\'Strong\'}\n        onPin={()=>pin(\'Column Quality Report\',\'quality\',{data_quality_detail:dq,meta})} pinned={hasItem(jobId,\'Column Quality Report\')}>',
    ),
    # ─── Summary Stats ────────────────────────────────────────────────────────
    (
        'icon={Sigma} col={C.purple} relevance={\'Strong\'}>',
        'icon={Sigma} col={C.purple} relevance={\'Strong\'}\n        onPin={()=>pin(\'Descriptive Statistics\',\'stats_table\',{summary_stats:ss,meta})} pinned={hasItem(jobId,\'Descriptive Statistics\')}>',
    ),
    # ─── Frequency ────────────────────────────────────────────────────────────
    (
        'icon={BarChart3} col={C.slate} relevance={rel(\'distribution\',a)}\n        bar={fa.length>1',
        'icon={BarChart3} col={C.slate} relevance={rel(\'distribution\',a)}\n        onPin={()=>pin(`Frequency: ${item.display_name}`,\'frequency\',{frequency_analysis:fa,meta})} pinned={hasItem(jobId,`Frequency: ${item.display_name}`)}\n        bar={fa.length>1',
    ),
    # ─── Time Decomposition ───────────────────────────────────────────────────
    (
        'col={item.trend_direction===\'upward\'?C.green:C.coral} relevance={rv}\n        bar={td.length>1',
        'col={item.trend_direction===\'upward\'?C.green:C.coral} relevance={rv}\n        onPin={()=>pin(`Decomposition: ${item.display_name}`,\'decomp\',{time_decomposition:td,meta})} pinned={hasItem(jobId,`Decomposition: ${item.display_name}`)}\n        bar={td.length>1',
    ),
    # ─── Gauge ────────────────────────────────────────────────────────────────
    (
        'col={statusColor} relevance={\'Strong\'}\n        bar={gd.length>1',
        'col={statusColor} relevance={\'Strong\'}\n        onPin={()=>pin(`Gauge: ${item.display_name}`,\'gauge\',{gauge:gd,meta})} pinned={hasItem(jobId,`Gauge: ${item.display_name}`)}\n        bar={gd.length>1',
    ),
    # ─── Slope ────────────────────────────────────────────────────────────────
    (
        'icon={TrendingUp} col={C.teal} relevance={\'Strong\'}\n        bar={sl.length>1',
        'icon={TrendingUp} col={C.teal} relevance={\'Strong\'}\n        onPin={()=>pin(`Slope: ${item.display_dimension}×${item.display_metric}`,\'slope\',{slope_chart:sl,meta})} pinned={hasItem(jobId,`Slope: ${item.display_dimension}×${item.display_metric}`)}\n        bar={sl.length>1',
    ),
    # ─── Error Bars ───────────────────────────────────────────────────────────
    (
        'icon={Activity} col={C.purple} relevance={\'Strong\'}\n        bar={eb.length>1',
        'icon={Activity} col={C.purple} relevance={\'Strong\'}\n        onPin={()=>pin(`CI: ${item.display_dimension}×${item.display_metric}`,\'errorbars\',{error_bars:eb,meta})} pinned={hasItem(jobId,`CI: ${item.display_dimension}×${item.display_metric}`)}\n        bar={eb.length>1',
    ),
    # ─── Gantt ────────────────────────────────────────────────────────────────
    (
        'icon={TrendingUp} col={C.cyan} relevance={\'Strong\'}\n        bar={gn.length>1',
        'icon={TrendingUp} col={C.cyan} relevance={\'Strong\'}\n        onPin={()=>pin(`Gantt: ${item.display_start}→${item.display_end}`,\'gantt\',{gantt:gn,meta})} pinned={hasItem(jobId,`Gantt: ${item.display_start}→${item.display_end}`)}\n        bar={gn.length>1',
    ),
    # ─── Sankey ───────────────────────────────────────────────────────────────
    (
        'icon={GitMerge} col={C.purple} relevance={\'Strong\'}\n        bar={sk.length>1',
        'icon={GitMerge} col={C.purple} relevance={\'Strong\'}\n        onPin={()=>pin(`Sankey: ${item.display_source}→${item.display_target}`,\'sankey\',{sankey:sk,meta})} pinned={hasItem(jobId,`Sankey: ${item.display_source}→${item.display_target}`)}\n        bar={sk.length>1',
    ),
    # ─── Drill-Through ────────────────────────────────────────────────────────
    (
        'icon={Eye} col={C.gold} relevance={\'Strong\'}\n        bar={dt.length>1',
        'icon={Eye} col={C.gold} relevance={\'Strong\'}\n        onPin={()=>pin(`Drill: ${item.display_dimension}`,\'drill\',{drill_through:dt,meta})} pinned={hasItem(jobId,`Drill: ${item.display_dimension}`)}\n        bar={dt.length>1',
    ),
    # ─── Marimekko ────────────────────────────────────────────────────────────
    (
        'icon={Grid} col={C.slate} relevance={\'Strong\'}\n        bar={mm_.length>1',
        'icon={Grid} col={C.slate} relevance={\'Strong\'}\n        onPin={()=>pin(`Marimekko: ${item.display_dim1}×${item.display_dim2}`,\'marimekko\',{marimekko:mm_,meta})} pinned={hasItem(jobId,`Marimekko: ${item.display_dim1}×${item.display_dim2}`)}\n        bar={mm_.length>1',
    ),
]

applied = 0
skipped = 0
failed  = 0

for old, new in patches:
    count = src.count(old)
    if count == 0:
        # might already be patched
        if new in src:
            print(f"  ↳ Already patched: {old[:60].strip()!r}")
            skipped += 1
        else:
            print(f"  ❌ NOT FOUND: {old[:60].strip()!r}")
            failed += 1
    elif count == 1:
        src = src.replace(old, new, 1)
        print(f"  ✅ Patched: {old[:60].strip()!r}")
        applied += 1
    else:
        print(f"  ⚠️  AMBIGUOUS ({count} matches): {old[:60].strip()!r} — SKIPPING")
        skipped += 1

with open(FILE, "w", encoding="utf-8") as f:
    f.write(src)

delta = len(src) - original_len
print(f"\n{'='*60}")
print(f"✅  Applied : {applied} patches")
print(f"↳   Skipped : {skipped} (already done or ambiguous)")
print(f"❌  Failed  : {failed} (text not found)")
print(f"📏  File grew by {delta:+,} chars ({original_len:,} → {len(src):,})")
print(f"\nRestart dev server:  npm run dev  (in frontend/ dir)")
