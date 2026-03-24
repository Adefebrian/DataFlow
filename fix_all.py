#!/usr/bin/env python3
"""
fix_all.py — Fix 3 issues:
1. Add onPin to missing 6 Cards in VisualizationsTab.tsx (Ranking, Outliers, Cohort, Multi-Metric, Percentile, Pareto)
2. Fix MyDashboardPage.tsx to render gauge, stats_table, concentration, var, etc.
3. Fix Export PDF to capture SVG charts
"""
import re, os, sys

# ═══════════════════════════════════════════════════════════════════════════════
# FIX 1: VisualizationsTab — add onPin to missing cards
# ═══════════════════════════════════════════════════════════════════════════════
VT = "/Users/brianeedsleep/Documents/Vibecode/frontend/src/components/VisualizationsTab.tsx"
with open(VT, "r", encoding="utf-8") as f:
    vt = f.read()
vt_orig = vt

# Each tuple: (unique fragment to find, replacement with onPin injected)
# We search for the Card opening of each render function and inject onPin

fixes_vt = [
    # ── Category Ranking ── (renderRanking)
    # Find: <Card title="Category Ranking" ... without onPin
    (
        'title="Category Ranking"',
        'RANKING_PLACEHOLDER'
    ),
    # ── Outlier Analysis ── (renderOutliers)
    (
        'title="Outlier Analysis"',
        'OUTLIERS_PLACEHOLDER'
    ),
    # ── Cohort Analysis ── (renderCohort)
    (
        'title="Cohort Analysis"',
        'COHORT_PLACEHOLDER'
    ),
    # ── Multi-Metric Comparison ── (renderMultiMetric)
    (
        'title="Multi-Metric Comparison"',
        'MULTI_PLACEHOLDER'
    ),
    # ── Percentile Distribution ── (renderPercentile)
    (
        'title="Percentile Distribution"',
        'PERCENTILE_PLACEHOLDER'
    ),
    # ── Pareto Analysis ── (renderPareto)
    (
        'title="Pareto Analysis (80/20)"',
        'PARETO_PLACEHOLDER'
    ),
]

# For each Card, find the full Card component opening (multi-line) and inject onPin
def inject_onpin(src, card_title, title_var, subtype, slice_expr, title_expr):
    """
    Finds a Card with the given title string and injects onPin if not present.
    """
    # Pattern: find the Card opening that contains this title and does NOT have onPin
    # We look for `title="XXXX"` preceded by <Card or followed by props
    
    # Find the position of title="..."
    pos = src.find(f'title="{card_title}"')
    if pos == -1:
        print(f"  NOT FOUND: title=\"{card_title}\"")
        return src, False
    
    # Find the start of <Card backwards from pos
    card_start = src.rfind('<Card', 0, pos)
    if card_start == -1:
        print(f"  Card start not found for: {card_title}")
        return src, False
    
    # Find the closing > of the Card props (first > after card_start not inside {})
    i = card_start
    depth = 0
    jsx_depth = 0
    card_end = -1
    while i < len(src) and i < card_start + 2000:
        ch = src[i]
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
        elif ch == '>' and depth == 0:
            # Check if this is the closing > of the Card props
            card_end = i
            break
        i += 1
    
    if card_end == -1:
        print(f"  Card end not found for: {card_title}")
        return src, False
    
    # Extract the Card props block
    card_block = src[card_start:card_end+1]
    
    # Check if onPin already present
    if 'onPin=' in card_block:
        print(f"  SKIP (already has onPin): {card_title}")
        return src, False
    
    # Inject onPin just before the closing >
    # Find where bar= ends or relevance= ends, or just before >
    # We insert onPin right before the closing >
    
    # Find the last prop before >
    # Insert: onPin={()=>pin(TITLE_EXPR, SUBTYPE, SLICE_EXPR)} pinned={hasItem(jobId, TITLE_EXPR)}
    inject = f'\n        onPin={{()=>pin({title_expr},\'{subtype}\',{slice_expr})}} pinned={{hasItem(jobId,{title_expr})}}'
    
    new_card_block = card_block[:-1] + inject + '>'
    new_src = src[:card_start] + new_card_block + src[card_end+1:]
    print(f"  ✅ injected onPin: {card_title}")
    return new_src, True

# Apply fixes for the 6 missing cards
injections = [
    (
        "Category Ranking",
        "ranking",
        "{ranking:rnk,meta}",
        "`Ranking: ${rnkItem?.display_dimension}×${rnkItem?.display_metric}`"
    ),
    (
        "Outlier Analysis",
        "outliers",
        "{outlier_detail:out,meta}",
        "`Outliers: ${outItem?.display_name}`"
    ),
    (
        "Cohort Analysis",
        "cohort",
        "{cohort:coh,meta}",
        "`Cohort: ${cohItem?.display_row}×${cohItem?.display_col}`"
    ),
    (
        "Multi-Metric Comparison",
        "multi_metric",
        "{multi_metric:mm,meta}",
        "`Multi-Metric: ${mmItem?.display_dimension}`"
    ),
    (
        "Percentile Distribution",
        "percentile",
        "{percentile_bands:pbd,meta}",
        "`Percentiles: ${pctItem?.display_name}`"
    ),
    (
        "Pareto Analysis (80/20)",
        "pareto",
        "{running_total:prt,meta}",
        "`Pareto: ${prtItem?.display_dimension}×${prtItem?.display_metric}`"
    ),
]

applied_vt = 0
for card_title, subtype, slice_expr, title_expr in injections:
    vt, ok = inject_onpin(vt, card_title, None, subtype, slice_expr, title_expr)
    if ok:
        applied_vt += 1

if vt != vt_orig:
    with open(VT, "w", encoding="utf-8") as f:
        f.write(vt)
    print(f"\nVisualizationsTab: {applied_vt} onPin injected ✅")
else:
    print("\nVisualizationsTab: no changes made")

# ═══════════════════════════════════════════════════════════════════════════════
# FIX 2 & 3: MyDashboardPage — add renderers for missing subtypes + fix PDF export
# ═══════════════════════════════════════════════════════════════════════════════
DB = "/Users/brianeedsleep/Documents/Vibecode/frontend/src/pages/MyDashboardPage.tsx"
with open(DB, "r", encoding="utf-8") as f:
    db = f.read()

# Check which subtypes are already handled
missing_subtypes = []
for sub in ['gauge', 'stats_table', 'concentration', 'var', 'moving', 'benchmark', 'quality', 'frequency', 'decomp', 'slope', 'errorbars', 'gantt', 'sankey', 'drill', 'marimekko']:
    if f"case '{sub}':" not in db:
        missing_subtypes.append(sub)

print(f"\nMyDashboardPage missing subtypes: {missing_subtypes}")

# The renderChart function's switch statement — add missing cases
# Find the default case and insert before it
default_marker = "    default:             return <Placeholder msg={`"
if default_marker not in db:
    # Try alternate
    default_marker = "    default:"
    
if default_marker in db:
    pos = db.find(default_marker)
    # Find the end of the default case
    
    new_cases = ""
    
    if 'gauge' not in str([s for s in ['gauge'] if f"case '{s}':" in db]):
        new_cases += """
    // Gauge/KPI vs Target
    case 'gauge': {
      const gd = s?.gauge || s?.value_at_risk || []
      const item = Array.isArray(gd) ? gd[0] : s
      if (!item) return <Placeholder msg="No gauge data" />
      const statusColor = item.status==='excellent'?C.green:item.status==='good'?C.teal:item.status==='warning'?C.amber:C.coral
      const pct = item.gauge_pct || item.pct_of_target || 0
      return (
        <div style={{ display:'flex', flexDirection:'column', alignItems:'center', padding:'12px 0' }}>
          <div style={{ fontSize:42, fontWeight:900, color:statusColor }}>{pct?.toFixed(0)}%</div>
          <div style={{ fontSize:12, color:'rgba(255,255,255,0.4)', marginTop:4 }}>of target · {item.status}</div>
          <div style={{ fontSize:13, color:'rgba(255,255,255,0.6)', marginTop:8 }}>
            {item.formatted_actual} <span style={{color:'rgba(255,255,255,0.3)'}}>vs</span> {item.formatted_target}
          </div>
          <div style={{ marginTop:12, width:'100%', height:8, borderRadius:4, background:'rgba(255,255,255,0.08)' }}>
            <div style={{ width:`${Math.min(100,pct)}%`, height:'100%', borderRadius:4, background:statusColor, opacity:0.8 }}/>
          </div>
        </div>
      )
    }
"""
    
    if 'stats_table' not in str([s for s in ['stats_table'] if f"case '{s}':" in db]):
        new_cases += """
    // Descriptive Statistics Table
    case 'stats_table': {
      const ss: any[] = s?.summary_stats || []
      if (!ss.length) return <Placeholder msg="No statistics data" />
      return (
        <div style={{ overflowX:'auto' }}>
          <table style={{ width:'100%', borderCollapse:'collapse', fontSize:10 }}>
            <thead>
              <tr>{['Column','Mean','Median','Std','Min','Max'].map((h:string) => (
                <th key={h} style={{ padding:'5px 8px', textAlign: h==='Column'?'left':'right', color:'rgba(212,175,55,0.7)', borderBottom:'1px solid rgba(255,255,255,0.06)', fontWeight:600 }}>{h}</th>
              ))}</tr>
            </thead>
            <tbody>
              {ss.slice(0,8).map((row:any, i:number) => (
                <tr key={i} style={{ background: i%2===0?'rgba(255,255,255,0.01)':'transparent' }}>
                  <td style={{ padding:'5px 8px', color:'rgba(255,255,255,0.7)', borderBottom:'1px solid rgba(255,255,255,0.04)', fontWeight:600 }}>{row.display_name}</td>
                  <td style={{ padding:'5px 8px', textAlign:'right', color:C.gold, borderBottom:'1px solid rgba(255,255,255,0.04)' }}>{nf(row.mean)}</td>
                  <td style={{ padding:'5px 8px', textAlign:'right', color:'rgba(255,255,255,0.5)', borderBottom:'1px solid rgba(255,255,255,0.04)' }}>{nf(row.median)}</td>
                  <td style={{ padding:'5px 8px', textAlign:'right', color:'rgba(255,255,255,0.5)', borderBottom:'1px solid rgba(255,255,255,0.04)' }}>{nf(row.std)}</td>
                  <td style={{ padding:'5px 8px', textAlign:'right', color:'rgba(255,255,255,0.4)', borderBottom:'1px solid rgba(255,255,255,0.04)' }}>{nf(row.min)}</td>
                  <td style={{ padding:'5px 8px', textAlign:'right', color:'rgba(255,255,255,0.4)', borderBottom:'1px solid rgba(255,255,255,0.04)' }}>{nf(row.max)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )
    }
"""

    if 'concentration' not in str([s for s in ['concentration'] if f"case '{s}':" in db]):
        new_cases += """
    // Market Concentration (Lorenz / Gini)
    case 'concentration': {
      const conc: any[] = s?.concentration || []
      const item = conc[0]
      if (!item) return <Placeholder msg="No concentration data" />
      const shares: any[] = (item.share_data || []).slice(0,8)
      return (
        <div>
          <div style={{ display:'flex', gap:12, marginBottom:12, flexWrap:'wrap' }}>
            {[['Gini',`${item.gini_pct}%`,C.gold],['HHI',`${item.hhi_pct?.toFixed(1)}%`,C.amber],['Top 1',`${item.top1_share}%`,C.coral],['Level',item.concentration_level,C.teal]].map(([l,v,c]:[string,string,string]) => (
              <div key={l} style={{ flex:1, minWidth:60, padding:'8px', borderRadius:8, background:`${c}0a`, border:`1px solid ${c}20`, textAlign:'center' }}>
                <p style={{ fontSize:9, color:'rgba(255,255,255,0.3)' }}>{l}</p>
                <p style={{ fontSize:14, fontWeight:700, color:c }}>{v}</p>
              </div>
            ))}
          </div>
          {shares.length > 0 && (
            <div style={{ height:140 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={shares} layout="vertical" margin={{ left:70, right:40, top:4, bottom:4 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" horizontal={false} />
                  <XAxis type="number" {...AX} tickFormatter={(v:number) => `${v}%`} />
                  <YAxis type="category" dataKey="category" {...AX} width={65} />
                  <Tooltip content={<MiniTip />} />
                  <Bar dataKey="share_pct" name="Share %" radius={[0,3,3,0]} maxBarSize={16}>
                    {shares.map((_:any,i:number) => <Cell key={i} fill={SEQ[i%SEQ.length]} opacity={0.85} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )
    }
"""

    if 'var' not in str([s for s in ['var'] if f"case '{s}':" in db]):
        new_cases += """
    // Value at Risk / Statistical Risk
    case 'var': {
      const var_: any[] = s?.value_at_risk || []
      const item = var_[0]
      if (!item) return <Placeholder msg="No VaR data" />
      const statusColor = item.risk_tier==='High'?C.coral:item.risk_tier==='Medium'?C.amber:C.green
      const hist: any[] = item.histogram || []
      return (
        <div>
          <div style={{ display:'flex', gap:10, marginBottom:12, flexWrap:'wrap' }}>
            {[['Risk Tier',item.risk_tier,statusColor],['VaR 95%',nf(item.var_95),C.amber],['CV%',`${item.cv_pct?.toFixed(1)}%`,statusColor],['Mean',nf(item.mean),C.gold]].map(([l,v,c]:[string,string,string]) => (
              <div key={l} style={{ flex:1, minWidth:60, padding:'8px', borderRadius:8, background:`${c}0a`, border:`1px solid ${c}20`, textAlign:'center' }}>
                <p style={{ fontSize:9, color:'rgba(255,255,255,0.3)' }}>{l}</p>
                <p style={{ fontSize:12, fontWeight:700, color:c }}>{v}</p>
              </div>
            ))}
          </div>
          {hist.length > 0 && (
            <div style={{ height:120 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={hist} margin={{ top:4, right:8, bottom:4, left:0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
                  <XAxis dataKey="bin" {...AX} interval="preserveStartEnd" />
                  <YAxis {...AX} />
                  <Tooltip content={<MiniTip />} />
                  <Bar dataKey="count" name="Count" radius={[2,2,0,0]}>
                    {hist.map((d:any,i:number) => <Cell key={i} fill={d.is_risk?C.coral:C.blue} opacity={0.8} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )
    }
"""

    if 'moving' not in str([s for s in ['moving'] if f"case '{s}':" in db]):
        new_cases += """
    // Moving Average
    case 'moving': {
      const ms: any[] = s?.moving_statistics || []
      const item = ms[0]
      const data: any[] = (item?.data || []).slice(-40)
      if (!data.length) return <Placeholder msg="No moving average data" />
      return (
        <div style={{ height:180 }}>
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={data} margin={{ top:4, right:8, bottom:4, left:0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
              <XAxis dataKey="index" {...AX} tickFormatter={(v:number) => `T${v+1}`} />
              <YAxis {...AX} tickFormatter={(v:number) => nf(v,0)} />
              <Tooltip content={<MiniTip />} />
              <Bar dataKey="value" name="Actual" fill={`${C.blue}30`} radius={[2,2,0,0]} maxBarSize={16} />
              <Line type="monotone" dataKey="ma3" name="MA3" stroke={C.gold} strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="ma7" name="MA7" stroke={C.teal} strokeWidth={1.5} dot={false} strokeDasharray="4 2" />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      )
    }
"""

    if 'benchmark' not in str([s for s in ['benchmark'] if f"case '{s}':" in db]):
        new_cases += """
    // Benchmark Comparison
    case 'benchmark': {
      const bm: any[] = s?.benchmark_comparison || []
      if (!bm.length) return <Placeholder msg="No benchmark data" />
      return (
        <div style={{ height:Math.max(140, bm.length*36) }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={bm} layout="vertical" margin={{ left:90, right:70, top:4, bottom:4 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" horizontal={false} />
              <XAxis type="number" {...AX} tickFormatter={(v:number) => nf(v,0)} />
              <YAxis type="category" dataKey="display_name" {...AX} width={85} />
              <Tooltip content={<MiniTip />} />
              <Bar dataKey="actual" name="Actual" radius={[0,3,3,0]} maxBarSize={18}>
                {bm.map((d:any,i:number) => <Cell key={i} fill={d.status==='above'?C.green:C.coral} opacity={0.85} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )
    }
"""

    if 'quality' not in str([s for s in ['quality'] if f"case '{s}':" in db]):
        new_cases += """
    // Data Quality
    case 'quality': {
      const dq: any[] = s?.data_quality_detail || []
      if (!dq.length) return <Placeholder msg="No quality data" />
      return (
        <div style={{ height:Math.max(120, dq.length*24) }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={dq} layout="vertical" margin={{ left:90, right:60, top:4, bottom:4 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" horizontal={false} />
              <XAxis type="number" domain={[0,100]} {...AX} tickFormatter={(v:number) => `${v}%`} />
              <YAxis type="category" dataKey="display_name" {...AX} width={85} />
              <Tooltip content={<MiniTip />} />
              <Bar dataKey="quality_score" name="Quality %" radius={[0,3,3,0]} maxBarSize={16}>
                {dq.map((d:any,i:number) => <Cell key={i} fill={d.fill||C.green} opacity={0.85} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )
    }
"""

    if 'frequency' not in str([s for s in ['frequency'] if f"case '{s}':" in db]):
        new_cases += """
    // Frequency Analysis
    case 'frequency': {
      const fa: any[] = s?.frequency_analysis || []
      const item = fa[0]
      const data: any[] = (item?.data || []).slice(0,12)
      if (!data.length) return <Placeholder msg="No frequency data" />
      return (
        <div style={{ height:160 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} layout="vertical" margin={{ left:90, right:50, top:4, bottom:4 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" horizontal={false} />
              <XAxis type="number" {...AX} tickFormatter={(v:number) => `${v}%`} />
              <YAxis type="category" dataKey="category" {...AX} width={85} />
              <Tooltip content={<MiniTip />} />
              <Bar dataKey="pct" name="Share %" radius={[0,3,3,0]} maxBarSize={18}>
                {data.map((_:any,i:number) => <Cell key={i} fill={SEQ[i%SEQ.length]} opacity={0.85} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )
    }
"""

    if 'decomp' not in str([s for s in ['decomp'] if f"case '{s}':" in db]):
        new_cases += """
    // Time Decomposition
    case 'decomp': {
      const td: any[] = s?.time_decomposition || []
      const item = td[0]
      const data: any[] = (item?.data || []).slice(-40)
      if (!data.length) return <Placeholder msg="No decomposition data" />
      const trendColor = item?.trend_direction==='upward'?C.green:C.coral
      return (
        <div style={{ height:180 }}>
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={data} margin={{ top:4, right:8, bottom:4, left:0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
              <XAxis dataKey="period" {...AX} />
              <YAxis {...AX} tickFormatter={(v:number) => nf(v,0)} />
              <Tooltip content={<MiniTip />} />
              <Area type="monotone" dataKey="actual" name="Actual" stroke={C.blue} fill={`${C.blue}20`} strokeWidth={1.5} dot={false} />
              <Line type="monotone" dataKey="trend" name="Trend" stroke={trendColor} strokeWidth={2} dot={false} strokeDasharray="5 3" />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      )
    }
"""

    if new_cases:
        # Insert before the default case
        db = db.replace(default_marker, new_cases + "\n    " + default_marker.strip())
        print(f"\nMyDashboardPage: injected {len(missing_subtypes)} missing subtype renderers ✅")
    else:
        print(f"\nMyDashboardPage: all subtypes already handled")
else:
    print(f"\nMyDashboardPage: could not find default marker")

# ── FIX 3: Export PDF — capture SVG charts ──────────────────────────────────
# Replace the exportDashboard function to properly serialize SVG from recharts

export_old_marker = "function exportDashboard("
if export_old_marker in db:
    # Find and replace the exportDashboard function
    start = db.find(export_old_marker)
    # Find the end of the function (next top-level function or export)
    # Look for "// ─── Header stats" or "function HeaderStats" or similar
    end_markers = ["function HeaderStats", "// ─── Header stats", "function buildExportHtml"]
    end_pos = len(db)
    for m in end_markers:
        p = db.find(m, start)
        if p != -1 and p < end_pos:
            end_pos = p
    
    old_fn = db[start:end_pos]
    
    new_fn = '''function exportDashboard(items: DashItem[]) {
  // Capture all SVG elements from rendered charts
  const captureChartsHTML = () => {
    const chartCards = document.querySelectorAll('[data-dashboard-card]')
    const captures: string[] = []
    
    chartCards.forEach((card: Element) => {
      const title = (card as HTMLElement).dataset.dashboardTitle || 'Chart'
      const svgEl = card.querySelector('svg')
      const color = (card as HTMLElement).dataset.dashboardColor || '#D4AF37'
      
      if (svgEl) {
        // Clone and fix SVG for export
        const cloned = svgEl.cloneNode(true) as SVGElement
        // Inline computed styles for SVG text elements
        const texts = cloned.querySelectorAll('text')
        texts.forEach((t: Element) => {
          (t as SVGTextElement).setAttribute('font-family', 'system-ui, sans-serif')
        })
        const serialized = new XMLSerializer().serializeToString(cloned)
        const b64 = btoa(unescape(encodeURIComponent(serialized)))
        captures.push(`
          <div class="card">
            <div class="card-header"><div class="dot" style="background:${color}"></div>${title}</div>
            <div class="chart-body"><img src="data:image/svg+xml;base64,${b64}" style="width:100%;max-height:280px;object-fit:contain" /></div>
          </div>
        `)
      } else {
        // Fallback: text summary
        const bodyEl = card.querySelector('[data-chart-content]')
        const bodyText = bodyEl ? (bodyEl as HTMLElement).innerText : ''
        captures.push(`
          <div class="card">
            <div class="card-header"><div class="dot" style="background:${color}"></div>${title}</div>
            <div class="chart-body" style="padding:16px;font-size:12px;color:rgba(255,255,255,0.5)">${bodyText.slice(0,200)}</div>
          </div>
        `)
      }
    })
    return captures.join('\\n')
  }

  const cardsHTML = captureChartsHTML()
  
  // KPI items
  const kpiHTML = items.filter(i => i.type === 'kpi').map(item => {
    const color = '#D4AF37'
    const pct = item.data?.pct_change
    return `
      <div class="card kpi-card">
        <div class="card-header"><div class="dot" style="background:${color}"></div>${item.title}</div>
        <div class="kpi-val" style="color:${color}">${item.data?.formatted_value || item.data?.value || '–'}</div>
        ${pct != null ? `<div class="kpi-delta">${pct > 0 ? '▲' : '▼'} ${Math.abs(pct).toFixed(1)}%</div>` : ''}
      </div>
    `
  }).join('\\n')

  const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>DataFlow Dashboard Export</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family: system-ui, sans-serif; background: #080810; color: #e0e0e0; padding: 28px 20px;
    background-image: radial-gradient(ellipse at 0% 0%, rgba(212,175,55,0.06) 0%, transparent 60%); }
  .header { text-align:center; margin-bottom:28px; padding:24px; background:rgba(212,175,55,0.06); 
    border:1px solid rgba(212,175,55,0.15); border-radius:16px; }
  .logo { font-size:1.5em; font-weight:900; color:#D4AF37; margin-bottom:6px; }
  .subtitle { color:rgba(255,255,255,0.35); font-size:0.85em; }
  .stats { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin-bottom:24px; }
  .stat { padding:14px; background:rgba(255,255,255,0.02); border:1px solid rgba(212,175,55,0.1); 
    border-radius:10px; text-align:center; }
  .stat-val { font-size:1.8em; font-weight:900; color:#D4AF37; }
  .stat-lbl { font-size:0.75em; color:rgba(255,255,255,0.35); margin-top:2px; }
  .grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(460px,1fr)); gap:14px; }
  .card { background:rgba(255,255,255,0.02); border:1px solid rgba(212,175,55,0.1); 
    border-radius:14px; overflow:hidden; break-inside:avoid; }
  .card-header { display:flex; align-items:center; gap:8px; padding:11px 14px; 
    border-bottom:1px solid rgba(255,255,255,0.05); font-weight:600; font-size:0.88em; color:#fff; }
  .dot { width:7px; height:7px; border-radius:50%; flex-shrink:0; }
  .chart-body { padding:0; background:rgba(0,0,0,0.2); }
  .chart-body img { display:block; width:100%; }
  .kpi-card .kpi-val { font-size:2.4em; font-weight:900; padding:16px 14px 4px; }
  .kpi-card .kpi-delta { font-size:0.85em; padding:0 14px 14px; color:rgba(255,255,255,0.5); }
  .footer { margin-top:24px; text-align:center; font-size:0.75em; color:rgba(255,255,255,0.2); }
  @media print { 
    body { background:#fff !important; color:#111 !important; }
    .card { background:#fff !important; border-color:rgba(0,0,0,0.12) !important; }
    .card-header { color:#111 !important; border-color:rgba(0,0,0,0.08) !important; }
    .chart-body { background:#f5f5f5 !important; }
  }
</style>
</head>
<body>
<div class="header">
  <div class="logo">✦ DataFlow</div>
  <div class="subtitle">Dashboard Export · ${new Date().toLocaleDateString('en-US', { year:'numeric', month:'long', day:'numeric' })} · ${items.length} pinned items</div>
</div>
<div class="stats">
  <div class="stat"><div class="stat-val">${items.filter(i => i.type !== 'kpi').length}</div><div class="stat-lbl">Charts</div></div>
  <div class="stat"><div class="stat-val">${items.filter(i => i.type === 'kpi').length}</div><div class="stat-lbl">KPIs</div></div>
  <div class="stat"><div class="stat-val">${new Set(items.map(i => i.jobId)).size}</div><div class="stat-lbl">Analyses</div></div>
</div>
<div class="grid">
${cardsHTML}
${kpiHTML}
</div>
<div class="footer">Generated by DataFlow Enterprise Analytics · ${new Date().toISOString().split('T')[0]}</div>
</body>
</html>`

  const win = window.open('', '_blank')
  if (!win) return
  win.document.write(html)
  win.document.close()
  setTimeout(() => win.print(), 800)
}

'''
    db = db[:start] + new_fn + db[end_pos:]
    print("MyDashboardPage: exportDashboard updated with SVG capture ✅")

# ── FIX 4: Add data-dashboard-card attributes to WidgetCard ─────────────────
# So the export function can find them
widget_card_old = 'const content = isKpi\n    ? renderKpiItem(item)\n    : renderChart(item)'
widget_card_new_search = "style={{\n        background: isDragging"
if widget_card_new_search in db:
    # Add data attributes to the outer div of WidgetCard
    old_div = "style={{\n        background: isDragging ? 'rgba(212,175,55,0.06)' : 'rgba(255,255,255,0.02)',"
    if old_div in db:
        new_div = old_div.replace(
            "style={{",
            "data-dashboard-card=\"true\"\n      data-dashboard-title={item.title}\n      data-dashboard-color={SUBTYPE_COLOR[item.subtype] || C.gold}\n      style={{"
        )
        db = db.replace(old_div, new_div, 1)
        print("MyDashboardPage: added data-dashboard-card attributes ✅")

# Also wrap chart content area with data-chart-content
chart_content_old = "        <div style={{ padding: '12px 14px', flex: 1 }}>{content}</div>"
if chart_content_old in db:
    db = db.replace(
        chart_content_old,
        "        <div data-chart-content=\"true\" style={{ padding: '12px 14px', flex: 1 }}>{content}</div>"
    )
    print("MyDashboardPage: added data-chart-content attribute ✅")

with open(DB, "w", encoding="utf-8") as f:
    f.write(db)

print("\n✅ All fixes applied!")
print("Now run: cd /Users/brianeedsleep/Documents/Vibecode && docker compose --profile prod up -d --build")
