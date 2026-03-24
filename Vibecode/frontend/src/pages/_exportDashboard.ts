// ─── Export PDF — render chart data as pure HTML (no SVG serialization) ──────
function exportDashboard(items: DashItem[]) {
  const COLORS = ['#D4AF37','#00CED1','#FF6B6B','#9B59B6','#2ECC71','#F39C12','#3498DB','#E91E63','#00BCD4','#8BC34A']

  // Build a pure-HTML bar chart from data — works perfectly in any browser/print
  function buildHtmlChart(item: DashItem): string {
    const s   = item.analyticsSlice
    const cfg = item.chartConfig
    const sub = item.subtype

    // ── KPI card ──────────────────────────────────────────────────────────────
    if (item.type === 'kpi') {
      const pct = item.data?.pct_change
      const col = SUBTYPE_COLOR[sub] || '#D4AF37'
      return `
        <div class="kpi-body">
          <div class="kpi-val" style="color:${col}">${item.data?.formatted_value || item.data?.value || '–'}</div>
          ${item.data?.formatted_total ? `<div class="kpi-sub">Total: ${item.data.formatted_total}</div>` : ''}
          ${pct != null ? `<div class="kpi-delta" style="color:${pct > 0 ? '#2ECC71' : pct < 0 ? '#FF6B6B' : '#9ca3af'}">${pct > 0 ? '▲' : pct < 0 ? '▼' : '→'} ${Math.abs(pct).toFixed(1)}%</div>` : ''}
        </div>`
    }

    // ── Custom analytics: array of data rows ──────────────────────────────────
    if (Array.isArray(s) && s.length > 0 && cfg?.chartType) {
      return buildBarRows(s, cfg.xCol || Object.keys(s[0])[0],
        cfg.yCols?.length ? cfg.yCols : Object.keys(s[0]).filter((k: string) => k !== cfg.xCol && typeof s[0][k] === 'number').slice(0, 2),
        COLORS)
    }

    // ── VisualizationsTab slices ───────────────────────────────────────────────
    // KPIs slice
    if (sub === 'kpis' && s?.kpis?.length) {
      const kpiRows = s.kpis.slice(0, 6).map((k: any) =>
        `<tr><td>${k.display_name || k.metric}</td><td style="color:#D4AF37;font-weight:700;text-align:right">${k.formatted_value || nf(k.value)}</td><td style="text-align:right;color:${(k.pct_change||0)>0?'#2ECC71':'#FF6B6B'}">${k.pct_change != null ? ((k.pct_change>0?'▲':'▼')+Math.abs(k.pct_change).toFixed(1)+'%') : ''}</td></tr>`
      ).join('')
      return `<table class="dt"><thead><tr><th>Metric</th><th>Value</th><th>Change</th></tr></thead><tbody>${kpiRows}</tbody></table>`
    }

    // Segments
    if (sub === 'segments' && s?.segments?.[0]?.data?.length) {
      const seg = s.segments[0]
      const data = seg.data.slice(0, 12)
      const max  = Math.max(...data.map((d: any) => d.total || 0)) || 1
      return buildBarRows(data, 'category', ['total'], COLORS, max, (d: any) => d.direction === 'above' ? '#2ECC71' : '#FF6B6B')
    }

    // Trend
    if (sub === 'trend' && s?.time_series?.[0]?.data?.length) {
      const ts   = s.time_series[0]
      const data = ts.data.slice(0, 30)
      const keys = (ts.metrics || []).slice(0, 3).map((m: any) => m.key)
      return buildLineTable(data, 'period', keys, ts.metrics)
    }

    // Growth
    if (sub === 'growth' && s?.growth_rates?.[0]?.periods?.length) {
      const data = s.growth_rates[0].periods.slice(0, 20)
      return buildBarRows(data, 'period', ['value', 'growth_rate_pct'], COLORS)
    }

    // Distribution
    if (sub === 'distribution' && s?.distributions?.[0]?.histogram?.length) {
      const hist = s.distributions[0].histogram
      const max  = Math.max(...hist.map((h: any) => h.count || 0)) || 1
      return buildBarRows(hist, 'label', ['count'], ['#9B59B6'], max)
    }

    // Composition
    if (sub === 'composition' && s?.composition?.[0]?.data?.length) {
      const data = s.composition[0].data.slice(0, 8)
      const rows = data.map((d: any, i: number) => `
        <tr>
          <td><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${COLORS[i%COLORS.length]};margin-right:6px"></span>${d.name}</td>
          <td style="text-align:right;font-weight:700">${d.pct?.toFixed(1)}%</td>
          <td style="text-align:right;color:rgba(255,255,255,0.5)">${nf(d.value)}</td>
        </tr>`).join('')
      return `<table class="dt"><thead><tr><th>Category</th><th>Share</th><th>Value</th></tr></thead><tbody>${rows}</tbody></table>`
    }

    // Correlation
    if (sub === 'correlation' && s?.correlation_matrix?.cells?.length) {
      const cells = s.correlation_matrix.cells.filter((c: any) => c.x !== c.y)
      const seen  = new Set<string>()
      const pairs = cells.reduce((acc: any[], c: any) => {
        const k = [c.x, c.y].sort().join('|')
        if (!seen.has(k)) { seen.add(k); acc.push(c) }
        return acc
      }, []).sort((a: any, b: any) => b.abs_value - a.abs_value).slice(0, 8)
      const rows  = pairs.map((p: any) => `
        <tr>
          <td>${p.x.slice(0,14)} ↔ ${p.y.slice(0,14)}</td>
          <td style="text-align:right;font-weight:700;color:${p.value>=0?'#00CED1':'#FF6B6B'}">${p.value?.toFixed(3)}</td>
          <td style="text-align:right">${p.strength}</td>
        </tr>`).join('')
      return `<table class="dt"><thead><tr><th>Pair</th><th>r</th><th>Strength</th></tr></thead><tbody>${rows}</tbody></table>`
    }

    // vs Average
    if (sub === 'vsavg') {
      const vsAvg = (s?.percentage_changes || []).find((x: any) => x.type === 'vs_average')
      const data  = (vsAvg?.data || []).slice(0, 10)
      if (data.length) {
        const max = Math.max(...data.map((d: any) => Math.abs(d.pct_vs_average || 0))) || 1
        return buildBarRows(data, 'category', ['pct_vs_average'], COLORS, max, (d: any) => d.direction === 'above' ? '#2ECC71' : '#FF6B6B')
      }
    }

    // Top/Bottom
    if (sub === 'topbottom') {
      const tb   = (s?.percentage_changes || []).find((x: any) => x.type === 'top_bottom_5')
      const data = [...(tb?.top_5||[]).map((d: any) => ({...d, _g:'Top'})), ...(tb?.bottom_5||[]).slice().reverse().map((d: any) => ({...d, _g:'Bottom'}))]
      if (data.length) {
        const max = Math.max(...data.map((d: any) => d.value || 0)) || 1
        return buildBarRows(data, 'category', ['value'], COLORS, max, (d: any) => d._g === 'Top' ? '#2ECC71' : '#FF6B6B')
      }
    }

    // Ranking
    if (sub === 'ranking' && s?.ranking?.[0]?.data?.length) {
      const data = s.ranking[0].data.slice(0, 12)
      const max  = Math.max(...data.map((d: any) => d.value || 0)) || 1
      return buildBarRows(data, 'category', ['value'], COLORS, max)
    }

    // Pareto
    if (sub === 'pareto' && s?.running_total?.[0]?.data?.length) {
      const data = s.running_total[0].data.slice(0, 15)
      return buildBarRows(data, 'category', ['value', 'cumulative_pct'], COLORS)
    }

    // Percentile
    if (sub === 'percentile' && s?.percentile_bands?.[0]) {
      const p = s.percentile_bands[0]
      return `<table class="dt"><thead><tr><th>Percentile</th><th>Value</th></tr></thead><tbody>
        ${[['P10', p.p10],['P25', p.p25],['Median (P50)', p.p50],['Mean', p.mean],['P75', p.p75],['P90', p.p90]].map(([l,v]) => `<tr><td>${l}</td><td style="text-align:right;font-weight:700;color:#3498DB">${nf(v)}</td></tr>`).join('')}
      </tbody></table>`
    }

    // Cohort
    if (sub === 'cohort' && s?.cohort?.[0]?.data?.length) {
      const coh    = s.cohort[0]
      const labels = coh.col_labels || []
      const data   = coh.data.slice(0, 8)
      const headerCols = ['Category', ...labels].map((h: string) => `<th>${h.slice(0,14)}</th>`).join('')
      const bodyRows = data.map((row: any) =>
        `<tr><td>${row.category}</td>${labels.map((l: string) => `<td style="text-align:right">${nf(row[l])}</td>`).join('')}</tr>`
      ).join('')
      return `<table class="dt"><thead><tr>${headerCols}</tr></thead><tbody>${bodyRows}</tbody></table>`
    }

    // Multi-Metric
    if (sub === 'multi_metric' && s?.multi_metric?.[0]) {
      const mm      = s.multi_metric[0]
      const metrics = (mm.metrics || []).slice(0, 4)
      const cats    = (mm.categories || []).slice(0, 6)
      const radar   = mm.radar_data || []
      const headerCols = ['Category', ...metrics].map((h: string) => `<th>${String(h).slice(0,12)}</th>`).join('')
      const bodyRows = radar.slice(0, 6).map((row: any) =>
        `<tr><td>${row.category}</td>${metrics.map((m: string) => `<td style="text-align:right">${nf(row[m])}</td>`).join('')}</tr>`
      ).join('')
      return `<table class="dt"><thead><tr>${headerCols}</tr></thead><tbody>${bodyRows}</tbody></table>`
    }

    // Stats table
    if (sub === 'stats_table' && s?.summary_stats?.length) {
      const ss   = s.summary_stats.slice(0, 8)
      const rows = ss.map((r: any) =>
        `<tr><td style="font-weight:600">${r.display_name}</td><td style="text-align:right;color:#D4AF37">${nf(r.mean)}</td><td style="text-align:right">${nf(r.median)}</td><td style="text-align:right">${nf(r.std)}</td><td style="text-align:right">${nf(r.min)}</td><td style="text-align:right">${nf(r.max)}</td></tr>`
      ).join('')
      return `<table class="dt"><thead><tr><th>Column</th><th>Mean</th><th>Median</th><th>Std</th><th>Min</th><th>Max</th></tr></thead><tbody>${rows}</tbody></table>`
    }

    // Gauge
    if (sub === 'gauge' && s?.gauge?.[0]) {
      const gd   = s.gauge
      const rows = gd.map((g: any) => {
        const col  = g.status==='excellent'?'#2ECC71':g.status==='good'?'#00CED1':g.status==='warning'?'#F39C12':'#FF6B6B'
        const pct  = g.gauge_pct || g.pct_of_target || 0
        return `<tr>
          <td>${g.display_name}</td>
          <td style="text-align:right;font-weight:700;color:${col}">${g.formatted_actual}</td>
          <td style="text-align:right">${g.formatted_target}</td>
          <td style="text-align:right"><span style="color:${col};font-weight:700">${pct.toFixed(0)}%</span></td>
          <td style="text-align:right"><span style="background:${col}22;color:${col};padding:2px 8px;border-radius:20px;font-size:0.85em">${g.status}</span></td>
        </tr>`
      }).join('')
      return `<table class="dt"><thead><tr><th>Metric</th><th>Actual</th><th>Target</th><th>% Target</th><th>Status</th></tr></thead><tbody>${rows}</tbody></table>`
    }

    // Concentration
    if (sub === 'concentration' && s?.concentration?.[0]) {
      const c = s.concentration[0]
      const shares = (c.share_data || []).slice(0, 8)
      const max    = Math.max(...shares.map((d: any) => d.share_pct || 0)) || 1
      return `
        <div style="display:flex;gap:12px;padding:12px 14px;border-bottom:1px solid rgba(255,255,255,0.06);flex-wrap:wrap">
          ${[['Gini',`${c.gini_pct}%`,'#D4AF37'],['HHI',`${c.hhi_pct?.toFixed(1)}%`,'#F39C12'],['Top 1 Share',`${c.top1_share}%`,'#FF6B6B'],['Level',c.concentration_level,'#00CED1']]
            .map(([l,v,col]) => `<div style="text-align:center;padding:8px 12px;border-radius:8px;background:rgba(255,255,255,0.04)"><div style="font-size:0.75em;opacity:0.5">${l}</div><div style="font-weight:700;color:${col}">${v}</div></div>`).join('')}
        </div>
        ${buildBarRows(shares, 'category', ['share_pct'], COLORS, max)}`
    }

    // VaR
    if (sub === 'var' && s?.value_at_risk?.[0]) {
      const v   = s.value_at_risk[0]
      const col = v.risk_tier==='High'?'#FF6B6B':v.risk_tier==='Medium'?'#F39C12':'#2ECC71'
      return `<table class="dt"><thead><tr><th>Metric</th><th>Value</th></tr></thead><tbody>
        ${[['Risk Tier', v.risk_tier],['VaR 95%', nf(v.var_95)],['VaR 99%', nf(v.var_99)],['CVaR 95%', nf(v.cvar_95)],['Mean', nf(v.mean)],['CV %', `${v.cv_pct?.toFixed(1)}%`]]
          .map(([l, val]) => `<tr><td>${l}</td><td style="text-align:right;font-weight:700;color:${col}">${val}</td></tr>`).join('')}
      </tbody></table>`
    }

    // Moving average
    if (sub === 'moving' && s?.moving_statistics?.[0]) {
      const ms   = s.moving_statistics[0]
      const data = (ms.data || []).slice(-20)
      return buildLineTable(data, 'index', ['value', 'ma3', 'ma7'], [{key:'value',display_name:'Actual'},{key:'ma3',display_name:'MA3'},{key:'ma7',display_name:'MA7'}])
    }

    // Benchmark
    if (sub === 'benchmark' && s?.benchmark_comparison?.length) {
      const bm   = s.benchmark_comparison
      const rows = bm.map((b: any) => {
        const col = b.status==='above'?'#2ECC71':'#FF6B6B'
        return `<tr><td>${b.display_name}</td><td style="text-align:right;font-weight:700;color:${col}">${b.formatted_actual}</td><td style="text-align:right">${b.formatted_benchmark}</td><td style="text-align:right;color:${col}">${b.status==='above'?'▲':'▼'} ${Math.abs(b.diff_pct||0).toFixed(1)}%</td></tr>`
      }).join('')
      return `<table class="dt"><thead><tr><th>Metric</th><th>Actual</th><th>Benchmark</th><th>Diff</th></tr></thead><tbody>${rows}</tbody></table>`
    }

    // Frequency
    if (sub === 'frequency' && s?.frequency_analysis?.[0]?.data?.length) {
      const fa   = s.frequency_analysis[0]
      const data = (fa.data || []).slice(0, 12)
      const max  = Math.max(...data.map((d: any) => d.pct || 0)) || 1
      return buildBarRows(data, 'category', ['pct'], COLORS, max)
    }

    // Outliers
    if (sub === 'outliers' && s?.outlier_detail?.[0]) {
      const out  = s.outlier_detail[0]
      const svd  = out.severity_data || []
      if (svd.length) {
        return `<div style="padding:12px 14px">
          <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:10px">
            ${[['Extreme', out.extreme_count,'#FF6B6B'],['Mild', out.mild_count,'#F39C12'],['Total', out.total_outliers,'#D4AF37'],['Outlier %', `${out.outlier_pct}%`,'#9B59B6']]
              .map(([l,v,c]) => `<div style="padding:8px 12px;border-radius:8px;background:rgba(255,255,255,0.04);text-align:center"><div style="font-size:0.75em;opacity:0.5">${l}</div><div style="font-weight:700;color:${c}">${v}</div></div>`).join('')}
          </div>
        </div>` + buildBarRows(svd, 'label', ['count'], ['#FF6B6B'])
      }
    }

    // Heatmap / Scatter / Radar fallback to table
    if (sub === 'heatmap' && s?.correlation_matrix?.columns?.length) {
      const cm   = s.correlation_matrix
      const cols = cm.columns.slice(0, 6)
      const cells = cm.cells || []
      const rows = cols.map((row: string) => {
        const tds = cols.map((col: string) => {
          const cell = cells.find((c: any) => (c.x===row&&c.y===col)||(c.x===col&&c.y===row))
          const v    = row===col ? 1 : (cell?.value ?? 0)
          const bg   = v >= 0 ? `rgba(0,206,209,${0.1+v*0.8})` : `rgba(255,107,107,${0.1+Math.abs(v)*0.8})`
          return `<td style="text-align:center;background:${bg};font-weight:600;font-size:0.85em">${v.toFixed(2)}</td>`
        }).join('')
        return `<tr><td style="font-size:0.8em">${row.slice(0,12)}</td>${tds}</tr>`
      }).join('')
      const header = `<tr><th></th>${cols.map((c: string) => `<th>${c.slice(0,10)}</th>`).join('')}</tr>`
      return `<table class="dt"><thead>${header}</thead><tbody>${rows}</tbody></table>`
    }

    // Decomp
    if (sub === 'decomp' && s?.time_decomposition?.[0]?.data?.length) {
      const td   = s.time_decomposition[0]
      const data = (td.data || []).slice(-20)
      return buildLineTable(data, 'period', ['actual', 'trend'], [{key:'actual',display_name:'Actual'},{key:'trend',display_name:'Trend'}])
    }

    // Quality
    if (sub === 'quality' && s?.data_quality_detail?.length) {
      const dq   = s.data_quality_detail.slice(0, 10)
      const rows = dq.map((d: any) => {
        const col = d.quality_score >= 80 ? '#2ECC71' : d.quality_score >= 50 ? '#F39C12' : '#FF6B6B'
        return `<tr><td>${d.display_name}</td><td style="text-align:right;font-weight:700;color:${col}">${d.quality_score}%</td><td style="text-align:right">${d.null_pct}%</td><td style="text-align:right">${d.col_type}</td></tr>`
      }).join('')
      return `<table class="dt"><thead><tr><th>Column</th><th>Quality</th><th>Nulls</th><th>Type</th></tr></thead><tbody>${rows}</tbody></table>`
    }

    // Default fallback — show raw summary
    return buildFallbackSummary(item)
  }

  // ── Pure HTML horizontal bar chart (works everywhere including print) ─────
  function buildBarRows(
    data: any[], xKey: string, yKeys: string[], colors: string[],
    maxOverride?: number, colorFn?: (d: any) => string
  ): string {
    if (!data?.length) return '<div class="no-data">No data</div>'
    const max = maxOverride || Math.max(...data.flatMap((d: any) => yKeys.map((k: string) => Math.abs(d[k] || 0)))) || 1
    const rows = data.slice(0, 15).map((d: any) => {
      const label = String(d[xKey] || '').slice(0, 22)
      const bars = yKeys.map((k: string, i: number) => {
        const v   = d[k] || 0
        const pct = Math.min(100, (Math.abs(v) / max) * 100)
        const col = colorFn ? colorFn(d) : colors[i % colors.length]
        return `<div style="display:flex;align-items:center;gap:6px;margin-top:${i>0?3:0}px">
          ${yKeys.length > 1 ? `<span style="font-size:0.7em;color:rgba(255,255,255,0.4);width:70px;text-align:right;flex-shrink:0">${k.slice(0,10)}</span>` : ''}
          <div style="flex:1;height:14px;background:rgba(255,255,255,0.05);border-radius:3px;overflow:hidden">
            <div style="width:${pct}%;height:100%;background:${col};border-radius:3px;opacity:0.85;min-width:2px"></div>
          </div>
          <span style="font-size:0.78em;color:rgba(255,255,255,0.7);min-width:40px;text-align:right">${nf(v)}</span>
        </div>`
      }).join('')
      return `<div style="padding:5px 14px;border-bottom:1px solid rgba(255,255,255,0.04)">
        <div style="font-size:0.82em;color:rgba(255,255,255,0.55);margin-bottom:3px">${label}</div>
        ${bars}
      </div>`
    }).join('')
    return `<div class="chart-bars">${rows}</div>`
  }

  // ── Simple table for time-series / line data ──────────────────────────────
  function buildLineTable(data: any[], xKey: string, yKeys: string[], metrics?: any[]): string {
    if (!data?.length) return '<div class="no-data">No data</div>'
    const metaMap: Record<string, string> = {}
    ;(metrics || []).forEach((m: any) => { metaMap[m.key || m] = m.display_name || m.key || m })
    const header = `<tr><th>${xKey}</th>${yKeys.map((k: string) => `<th>${(metaMap[k] || k).slice(0,12)}</th>`).join('')}</tr>`
    const rows   = data.slice(0, 20).map((d: any, i: number) => `<tr style="background:${i%2===0?'rgba(255,255,255,0.01)':'transparent'}">
      <td>${String(d[xKey] || i).slice(0,16)}</td>
      ${yKeys.map((k: string) => `<td style="text-align:right">${d[k] != null ? nf(d[k]) : '–'}</td>`).join('')}
    </tr>`).join('')
    return `<table class="dt"><thead>${header}</thead><tbody>${rows}</tbody></table>`
  }

  // ── Fallback ──────────────────────────────────────────────────────────────
  function buildFallbackSummary(item: DashItem): string {
    const s = item.analyticsSlice
    if (item.image_base64) {
      return `<div style="padding:0"><img src="data:image/png;base64,${item.image_base64}" style="width:100%;max-height:220px;object-fit:contain;display:block;background:rgba(0,0,0,0.2)"/></div>`
    }
    const summary = Array.isArray(s) && s.length
      ? `${s.length} data points · ${item.subtype}`
      : s?.kpis?.length ? s.kpis.slice(0,3).map((k: any) => `${k.display_name}: ${k.formatted_value||k.value}`).join(' · ')
      : s?.segments?.[0] ? `${s.segments[0].display_dimension} × ${s.segments[0].display_metric} · ${s.segments[0].data?.length} categories`
      : `${item.subtype} visualization`
    return `<div class="no-data">${summary}</div>`
  }

  // ── Build HTML ────────────────────────────────────────────────────────────
  const cards = items.map(item => {
    const color = SUBTYPE_COLOR[item.subtype] || '#D4AF37'
    const body  = buildHtmlChart(item)
    return `
<div class="card">
  <div class="card-hdr">
    <div class="dot" style="background:${color}"></div>
    <span>${item.title}</span>
    <span class="card-sub">${item.jobName}</span>
  </div>
  <div class="card-body">${body}</div>
  <div class="card-ftr">${item.jobName} · ${new Date(item.pinnedAt).toLocaleDateString()}</div>
</div>`
  }).join('\n')

  const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>DataFlow Dashboard Export</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body {
    font-family: system-ui, -apple-system, sans-serif;
    background: #080810;
    color: #e0e0e0;
    padding: 28px 20px;
  }
  /* Header */
  .hdr { text-align:center; margin-bottom:24px; padding:24px 20px; background:rgba(212,175,55,0.06); border:1px solid rgba(212,175,55,0.2); border-radius:16px; }
  .logo { font-size:1.6em; font-weight:900; color:#D4AF37; margin-bottom:6px; }
  .subtitle { color:rgba(255,255,255,0.4); font-size:0.85em; }
  /* Stats row */
  .stats { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin-bottom:24px; }
  .stat { padding:14px; background:rgba(255,255,255,0.02); border:1px solid rgba(212,175,55,0.12); border-radius:10px; text-align:center; }
  .stat-val { font-size:1.8em; font-weight:900; color:#D4AF37; }
  .stat-lbl { font-size:0.75em; color:rgba(255,255,255,0.35); margin-top:3px; }
  /* Grid */
  .grid { display:grid; grid-template-columns:repeat(auto-fill, minmax(460px,1fr)); gap:14px; }
  /* Card */
  .card { background:rgba(255,255,255,0.02); border:1px solid rgba(212,175,55,0.12); border-radius:14px; overflow:hidden; break-inside:avoid; page-break-inside:avoid; }
  .card-hdr { display:flex; align-items:center; gap:8px; padding:11px 14px; border-bottom:1px solid rgba(255,255,255,0.06); }
  .card-hdr span:first-of-type { font-weight:600; font-size:0.9em; color:#fff; flex:1; }
  .card-sub { font-size:0.75em; color:rgba(255,255,255,0.3); }
  .dot { width:8px; height:8px; border-radius:50%; flex-shrink:0; }
  .card-body { min-height:60px; }
  .card-ftr { padding:6px 14px; border-top:1px solid rgba(255,255,255,0.04); font-size:0.72em; color:rgba(255,255,255,0.25); }
  /* KPI */
  .kpi-body { padding:20px 16px; }
  .kpi-val { font-size:2.6em; font-weight:900; line-height:1; }
  .kpi-sub { font-size:0.85em; color:rgba(255,255,255,0.4); margin-top:6px; }
  .kpi-delta { font-size:0.9em; font-weight:700; margin-top:8px; }
  /* Bar chart rows */
  .chart-bars { padding:6px 0; }
  /* Data table */
  .dt { width:100%; border-collapse:collapse; font-size:0.82em; }
  .dt th { padding:7px 10px; text-align:left; color:rgba(212,175,55,0.8); border-bottom:1px solid rgba(212,175,55,0.15); font-weight:600; background:rgba(0,0,0,0.2); }
  .dt td { padding:6px 10px; border-bottom:1px solid rgba(255,255,255,0.04); color:rgba(255,255,255,0.7); }
  .dt tr:nth-child(even) td { background:rgba(255,255,255,0.01); }
  /* No-data */
  .no-data { padding:20px 14px; font-size:0.82em; color:rgba(255,255,255,0.35); }
  /* Print */
  @media print {
    body { background:#fff !important; color:#111 !important; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
    .card { background:#fff !important; border-color:rgba(0,0,0,0.15) !important; }
    .card-hdr { background:#f8f8f8 !important; }
    .card-hdr span:first-of-type { color:#111 !important; }
    .dt th { background:#f0f0f0 !important; color:#333 !important; }
    .dt td { color:#444 !important; }
    .hdr, .stats .stat { background:#f8f8f8 !important; }
    .stat-val { color:#996515 !important; }
    .logo { color:#996515 !important; }
    .kpi-val { color:#996515 !important; }
  }
</style>
</head>
<body>

<div class="hdr">
  <div class="logo">✦ DataFlow</div>
  <div class="subtitle">Dashboard Export · ${new Date().toLocaleDateString('en-US',{year:'numeric',month:'long',day:'numeric'})} · ${items.length} pinned items</div>
</div>

<div class="stats">
  <div class="stat"><div class="stat-val">${items.filter(i=>i.type!=='kpi').length}</div><div class="stat-lbl">Charts</div></div>
  <div class="stat"><div class="stat-val">${items.filter(i=>i.type==='kpi').length}</div><div class="stat-lbl">KPIs</div></div>
  <div class="stat"><div class="stat-val">${new Set(items.map(i=>i.jobId)).size}</div><div class="stat-lbl">Analyses</div></div>
</div>

<div class="grid">
${cards}
</div>

<div style="margin-top:28px;text-align:center;font-size:0.75em;color:rgba(255,255,255,0.2)">
  Generated by DataFlow Enterprise Analytics · ${new Date().toISOString().split('T')[0]}
</div>

</body>
</html>`

  const win = window.open('', '_blank')
  if (!win) { alert('Allow pop-ups to export PDF'); return }
  win.document.write(html)
  win.document.close()
  setTimeout(() => win.print(), 400)
}