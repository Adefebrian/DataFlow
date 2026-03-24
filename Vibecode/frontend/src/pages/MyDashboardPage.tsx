/**
 * MyDashboardPage v4
 * ─────────────────────────────────────────────────────────────────
 * FIXES:
 *  ✅ ALL VisualizationsTab subtypes rendered (gauge, stats_table,
 *     concentration, var, moving, benchmark, quality, frequency, decomp)
 *  ✅ Export PDF captures actual SVG charts via XMLSerializer
 *  ✅ Drag-and-drop reorder cards
 *  ✅ All custom analytics chart types (bar/line/area/pie/scatter/etc.)
 */
import { useState, useRef, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { useDashboard, DashItem } from '../hooks/useDashboard'
import {
  ResponsiveContainer, AreaChart, Area, BarChart, Bar,
  LineChart, Line, PieChart, Pie, Cell,
  ComposedChart, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ScatterChart, Scatter, XAxis, YAxis, ZAxis, CartesianGrid, Tooltip, Legend,
  ReferenceLine, Treemap, FunnelChart, Funnel,
} from 'recharts'
import {
  LayoutDashboard, Trash2, X, ZoomIn, BarChart3, TrendingUp, Activity,
  PieChart as PieIcon, Layers, Target, ArrowRight, Plus, Download,
  Award, Eye, Hash, Zap, GitBranch, Grid3x3, LayoutList, RefreshCw,
  ArrowUpRight, ArrowDownRight, Minus, GripVertical, ShieldAlert, Sigma,
} from 'lucide-react'

const C = {
  gold: '#D4AF37', teal: '#00CED1', coral: '#FF6B6B', purple: '#9B59B6',
  green: '#2ECC71', amber: '#F39C12', blue: '#3498DB', pink: '#E91E63',
  cyan: '#00BCD4', lime: '#8BC34A', orange: '#FF9800', indigo: '#5C6BC0',
}
const SEQ = [C.gold, C.teal, C.coral, C.purple, C.green, C.amber, C.blue, C.pink, C.cyan, C.lime]

const nf = (v: any, d = 1) => {
  if (v == null || isNaN(+v)) return '–'
  const n = +v, a = Math.abs(n)
  if (a >= 1e9) return `${(n/1e9).toFixed(d)}B`
  if (a >= 1e6) return `${(n/1e6).toFixed(d)}M`
  if (a >= 1e3) return `${(n/1e3).toFixed(d)}K`
  return n.toLocaleString(undefined, { maximumFractionDigits: 2 })
}

const SUBTYPE_COLOR: Record<string, string> = {
  kpis: C.gold, segments: C.green, trend: C.teal, growth: C.green,
  distribution: C.purple, composition: C.amber, scatter: C.gold,
  correlation: C.teal, heatmap: C.indigo, vsavg: C.green, topbottom: C.coral,
  radar: C.pink, ranking: C.gold, outliers: C.coral, cohort: C.cyan,
  multi_metric: C.orange, percentile: C.blue, pareto: C.lime,
  gauge: C.teal, stats_table: C.purple, concentration: C.indigo,
  var: C.coral, moving: C.cyan, benchmark: C.green, quality: C.green,
  frequency: C.amber, decomp: C.teal,
  kpi: C.gold, meta: C.blue,
  bar: C.gold, hbar: C.teal, line: C.blue, area: C.teal,
  pie: C.amber, donut: C.amber, treemap: C.purple,
  histogram: C.purple, waterfall: C.green,
  lollipop: C.gold, composed: C.blue, funnel: C.orange, step: C.teal,
}

const SUBTYPE_ICON: Record<string, any> = {
  kpis: Target, segments: BarChart3, trend: TrendingUp, growth: TrendingUp,
  distribution: Activity, composition: PieIcon, scatter: GitBranch,
  correlation: Layers, vsavg: Zap, topbottom: Award,
  radar: Eye, kpi: Target, meta: Hash,
  gauge: Target, stats_table: Sigma, concentration: Layers,
  var: ShieldAlert, moving: TrendingUp, benchmark: Award, quality: ShieldAlert,
  frequency: BarChart3, decomp: TrendingUp,
  bar: BarChart3, hbar: BarChart3, line: TrendingUp, area: Activity,
  pie: PieIcon, donut: PieIcon, treemap: Grid3x3,
}

const AX = { stroke: 'rgba(255,255,255,0.05)', tick: { fill: 'rgba(255,255,255,0.3)', fontSize: 9 } as any }

function MiniTip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null
  return (
    <div style={{ background: '#10101c', border: '1px solid rgba(212,175,55,0.2)', borderRadius: 8, padding: '8px 12px', fontSize: 11, maxWidth: 220 }}>
      {label && <p style={{ color: 'rgba(255,255,255,0.5)', marginBottom: 4, fontSize: 10 }}>{label}</p>}
      {payload.map((p: any, i: number) => (
        <div key={i} style={{ display: 'flex', gap: 8, alignItems: 'center', color: 'rgba(255,255,255,0.8)', marginTop: 2 }}>
          <span style={{ width: 6, height: 6, borderRadius: '50%', background: p.color ?? p.fill ?? C.gold, flexShrink: 0 }} />
          {p.name}: <b>{typeof p.value === 'number' ? nf(p.value) : String(p.value ?? '–')}</b>
        </div>
      ))}
    </div>
  )
}

function Placeholder({ msg }: { msg: string }) {
  return <div style={{ padding: '32px 0', textAlign: 'center', color: 'rgba(255,255,255,0.2)', fontSize: 11 }}>{msg}</div>
}

// ─── Universal renderer ──────────────────────────────────────────────────────
function renderChart(item: DashItem) {
  const s   = item.analyticsSlice
  const cfg = item.chartConfig
  const sub = item.subtype

  if (Array.isArray(s) && s.length > 0 && cfg?.chartType) {
    return <CustomChartMini data={s} cfg={cfg} />
  }

  switch (sub) {
    // ── Core VisualizationsTab subtypes ──
    case 'kpis':         return <KpisGrid slice={s} />
    case 'segments':     return <SegmentsBar slice={s} />
    case 'trend':        return <TrendArea slice={s} cfg={cfg} />
    case 'growth':       return <GrowthComposed slice={s} />
    case 'distribution': return <DistributionHist slice={s} />
    case 'composition':  return <CompositionPie slice={s} />
    case 'correlation':  return <CorrelationBar slice={s} />
    case 'vsavg':        return <VsAvgBar slice={s} />
    case 'topbottom':    return <TopBottomBar slice={s} />
    case 'radar':        return <RadarSpider slice={s} />
    case 'ranking':      return <RankingBar slice={s} />
    case 'outliers':     return <OutlierSeverity slice={s} />
    case 'cohort':       return <CohortGrouped slice={s} />
    case 'multi_metric': return <MultiMetricRadar slice={s} />
    case 'percentile':   return <PercentileBands slice={s} />
    case 'pareto':       return <ParetoComposed slice={s} />
    case 'heatmap':      return <HeatmapBar slice={s} />
    case 'scatter':      return <ScatterDots slice={s} />
    // ── Previously missing subtypes — NOW FIXED ──
    case 'gauge':        return <GaugeCard slice={s} />
    case 'stats_table':  return <StatsTableCard slice={s} />
    case 'concentration':return <ConcentrationCard slice={s} />
    case 'var':          return <VarCard slice={s} />
    case 'moving':       return <MovingAvgCard slice={s} />
    case 'benchmark':    return <BenchmarkCard slice={s} />
    case 'quality':      return <QualityCard slice={s} />
    case 'frequency':    return <FrequencyCard slice={s} />
    case 'decomp':       return <DecompCard slice={s} />
    // ── Custom analytics saved without cfg ──
    case 'bar': case 'hbar': case 'line': case 'area': case 'composed':
    case 'pie': case 'donut': case 'treemap': case 'histogram':
    case 'waterfall': case 'lollipop': case 'step': case 'funnel': case 'bubble':
      if (Array.isArray(s)) return <CustomChartMini data={s} cfg={{ chartType: sub, ...cfg }} />
      return <Placeholder msg={`${sub} chart — re-pin to restore`} />
    default:
      return <Placeholder msg={`${sub} visualization`} />
  }
}

// ─── Custom Analytics Mini ───────────────────────────────────────────────────
function CustomChartMini({ data, cfg }: { data: any[]; cfg: any }) {
  if (!data?.length) return <Placeholder msg="No data" />
  const { chartType = 'bar', xCol, yCols = [], palette = 'Gold' } = cfg
  const PALETTES: Record<string, string[]> = {
    Gold: [C.gold, C.amber, C.coral, C.teal, C.purple, C.blue],
    Ocean: ['#0EA5E9','#06B6D4','#10B981','#3B82F6','#6366F1','#8B5CF6'],
    Sunset: ['#F59E0B','#EF4444','#EC4899','#8B5CF6','#6366F1','#3B82F6'],
    Forest: ['#22C55E','#16A34A','#84CC16','#CA8A04','#D97706','#B45309'],
    Mono: ['#F8FAFC','#CBD5E1','#94A3B8','#64748B','#475569','#334155'],
    Vibrant: ['#FF6B6B','#4ECDC4','#45B7D1','#96CEB4','#FFEAA7','#DDA0DD'],
  }
  const colors = PALETTES[palette] || PALETTES.Gold
  const xKey = xCol || Object.keys(data[0])[0]
  const yKeys = yCols.length > 0 ? yCols : Object.keys(data[0]).filter((k: string) => k !== xKey && typeof data[0][k] === 'number').slice(0, 3)
  const H = 200

  if (chartType === 'pie' || chartType === 'donut') {
    const pieData = data.slice(0,12).map((r:any) => ({ name: String(r[xKey]), value: parseFloat(String(r[yKeys[0]]||0))||0 }))
    return (
      <div style={{ height: H }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart><Pie data={pieData} dataKey="value" nameKey="name" outerRadius={80} innerRadius={chartType==='donut'?40:0} paddingAngle={2} startAngle={90} endAngle={-270}>
            {pieData.map((_:any,i:number) => <Cell key={i} fill={colors[i%colors.length]}/>)}
          </Pie><Tooltip content={<MiniTip/>}/></PieChart>
        </ResponsiveContainer>
      </div>
    )
  }
  if (chartType === 'scatter' || chartType === 'bubble') {
    const scData = data.slice(0,100).map((r:any) => ({ x:parseFloat(String(r[xKey]))||0, y:parseFloat(String(r[yKeys[0]]||0))||0 }))
    return (
      <div style={{ height: H }}>
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{top:5,right:10,bottom:5,left:0}}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)"/>
            <XAxis type="number" dataKey="x" {...AX}/><YAxis type="number" dataKey="y" {...AX} tickFormatter={(v:number)=>nf(v,0)}/>
            <Tooltip content={<MiniTip/>}/><Scatter data={scData} fill={colors[0]} opacity={0.75}/>
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    )
  }
  if (chartType === 'radar') {
    return (
      <div style={{ height: H }}>
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={data.slice(0,10)}>
            <PolarGrid stroke="rgba(255,255,255,0.07)"/><PolarAngleAxis dataKey={xKey} tick={{fill:'rgba(255,255,255,0.35)',fontSize:9}}/><PolarRadiusAxis tick={{fill:'rgba(255,255,255,0.2)',fontSize:7}}/>
            {yKeys.map((yc:string,i:number) => <Radar key={yc} name={yc} dataKey={yc} stroke={colors[i%colors.length]} fill={colors[i%colors.length]} fillOpacity={0.12} strokeWidth={2}/>)}
            <Tooltip content={<MiniTip/>}/>
          </RadarChart>
        </ResponsiveContainer>
      </div>
    )
  }
  if (chartType === 'hbar') {
    return (
      <div style={{ height: Math.max(H, data.length*28+40) }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{left:80,right:30,top:4,bottom:4}}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" horizontal={false}/>
            <XAxis type="number" {...AX} tickFormatter={(v:number)=>nf(v,0)}/><YAxis type="category" dataKey={xKey} {...AX} width={75}/>
            <Tooltip content={<MiniTip/>}/>
            {yKeys.map((yc:string,i:number) => <Bar key={yc} dataKey={yc} name={yc} fill={colors[i%colors.length]} radius={[0,3,3,0]} maxBarSize={20}/>)}
          </BarChart>
        </ResponsiveContainer>
      </div>
    )
  }
  if (chartType === 'area') {
    return (
      <div style={{ height: H }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{top:4,right:8,bottom:4,left:0}}>
            <defs>{yKeys.map((_:any,i:number) => <linearGradient key={i} id={`dca${i}`} x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={colors[i%colors.length]} stopOpacity={0.4}/><stop offset="100%" stopColor={colors[i%colors.length]} stopOpacity={0.02}/></linearGradient>)}</defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false}/>
            <XAxis dataKey={xKey} {...AX}/><YAxis {...AX} tickFormatter={(v:number)=>nf(v,0)}/>
            <Tooltip content={<MiniTip/>}/>
            {yKeys.map((yc:string,i:number) => <Area key={yc} type="monotone" dataKey={yc} name={yc} stroke={colors[i%colors.length]} strokeWidth={2} fill={`url(#dca${i})`} dot={false}/>)}
          </AreaChart>
        </ResponsiveContainer>
      </div>
    )
  }
  if (chartType === 'line' || chartType === 'step') {
    return (
      <div style={{ height: H }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{top:4,right:8,bottom:4,left:0}}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false}/>
            <XAxis dataKey={xKey} {...AX}/><YAxis {...AX} tickFormatter={(v:number)=>nf(v,0)}/><Tooltip content={<MiniTip/>}/>
            {yKeys.map((yc:string,i:number) => <Line key={yc} type={chartType==='step'?'stepAfter':'monotone'} dataKey={yc} name={yc} stroke={colors[i%colors.length]} strokeWidth={2} dot={false}/>)}
          </LineChart>
        </ResponsiveContainer>
      </div>
    )
  }
  if (chartType === 'waterfall') {
    let running = 0
    const wfData = data.slice(0,20).map((r:any) => { const v=parseFloat(String(r[yKeys[0]]||0))||0; const e={[xKey]:r[xKey],value:v,_pos:v>=0}; running+=v; return e })
    return (
      <div style={{ height: H }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={wfData} margin={{top:4,right:8,bottom:24,left:0}}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false}/>
            <XAxis dataKey={xKey} {...AX} tick={{fill:'rgba(255,255,255,0.3)',fontSize:8}}/><YAxis {...AX} tickFormatter={(v:number)=>nf(v,0)}/>
            <Tooltip content={<MiniTip/>}/><ReferenceLine y={0} stroke="rgba(255,255,255,0.2)"/>
            <Bar dataKey="value" radius={[2,2,0,0]} maxBarSize={28}>{wfData.map((d:any,i:number) => <Cell key={i} fill={d._pos?C.green:C.coral} opacity={0.85}/>)}</Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    )
  }
  if (chartType === 'histogram') {
    const numVals = data.map((r:any)=>parseFloat(String(r[yKeys[0]||xKey]))).filter((v:number)=>!isNaN(v))
    if (!numVals.length) return <Placeholder msg="No numeric data"/>
    const min=Math.min(...numVals),max=Math.max(...numVals),bins=15,step=(max-min)/bins||1
    const buckets = Array.from({length:bins},(_,i)=>({x:`${(min+i*step).toFixed(1)}`,count:numVals.filter((v:number)=>v>=min+i*step&&v<min+(i+1)*step).length}))
    return (
      <div style={{ height: H }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={buckets} margin={{top:4,right:8,bottom:4,left:0}}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false}/>
            <XAxis dataKey="x" {...AX} interval="preserveStartEnd" tick={{fill:'rgba(255,255,255,0.25)',fontSize:8}}/><YAxis {...AX}/><Tooltip content={<MiniTip/>}/>
            <Bar dataKey="count" name="Count" radius={[2,2,0,0]}>{buckets.map((_:any,i:number) => <Cell key={i} fill={`${colors[0]}${Math.round(60+i*(180/bins)).toString(16).padStart(2,'0')}`}/>)}</Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    )
  }
  if (chartType === 'composed') {
    return (
      <div style={{ height: H }}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{top:4,right:8,bottom:4,left:0}}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false}/>
            <XAxis dataKey={xKey} {...AX}/><YAxis {...AX} tickFormatter={(v:number)=>nf(v,0)}/><Tooltip content={<MiniTip/>}/>
            {yKeys.slice(0,1).map((yc:string,i:number) => <Bar key={yc} dataKey={yc} name={yc} fill={`${colors[i]}50`} radius={[2,2,0,0]} maxBarSize={24}/>)}
            {yKeys.slice(1).map((yc:string,i:number) => <Line key={yc} type="monotone" dataKey={yc} name={yc} stroke={colors[(i+1)%colors.length]} strokeWidth={2} dot={false}/>)}
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    )
  }
  // Default: vertical bar
  return (
    <div style={{ height: H }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{top:4,right:8,bottom:24,left:0}}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false}/>
          <XAxis dataKey={xKey} {...AX} tick={{fill:'rgba(255,255,255,0.3)',fontSize:9}}/><YAxis {...AX} tickFormatter={(v:number)=>nf(v,0)}/><Tooltip content={<MiniTip/>}/>
          {yKeys.map((yc:string,i:number) => <Bar key={yc} dataKey={yc} name={yc} fill={colors[i%colors.length]} radius={[3,3,0,0]} maxBarSize={32} opacity={0.85}/>)}
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

// ─── Core slice renderers ────────────────────────────────────────────────────
function KpisGrid({ slice }: { slice: any }) {
  const kpis: any[] = slice?.kpis || []
  if (!kpis.length) return <Placeholder msg="No KPI data" />
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(130px, 1fr))', gap: 8 }}>
      {kpis.slice(0, 6).map((kpi: any, i: number) => {
        const col = SEQ[i % SEQ.length], pct = kpi.pct_change, isPos = (pct??0)>0, isFlat = Math.abs(pct??0)<0.5
        const sparks = (kpi.sparkline || []).map((v: number, si: number) => ({ si, v }))
        return (
          <div key={i} style={{ padding: 10, borderRadius: 10, background: 'rgba(255,255,255,0.03)', border: `1px solid ${col}20` }}>
            <p style={{ fontSize: 10, color: 'rgba(255,255,255,0.4)', marginBottom: 4, lineHeight: 1.3 }}>{kpi.display_name || kpi.metric}</p>
            <p style={{ fontSize: 18, fontWeight: 900, color: col }}>{kpi.formatted_value || nf(kpi.value)}</p>
            {sparks.length > 2 && (
              <div style={{ height: 22, margin: '4px -2px' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={sparks}><defs><linearGradient id={`dspk${i}`} x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={col} stopOpacity={0.4}/><stop offset="100%" stopColor={col} stopOpacity={0}/></linearGradient></defs>
                  <Area type="monotone" dataKey="v" stroke={col} strokeWidth={1.5} fill={`url(#dspk${i})`} dot={false}/></AreaChart>
                </ResponsiveContainer>
              </div>
            )}
            {pct != null && (
              <span style={{ fontSize: 9, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 2, marginTop: 2, color: isFlat?'#9ca3af':isPos?'#34d399':'#f87171' }}>
                {isFlat?<Minus style={{width:8,height:8}}/>:isPos?<ArrowUpRight style={{width:8,height:8}}/>:<ArrowDownRight style={{width:8,height:8}}/>}{Math.abs(pct).toFixed(1)}%
              </span>
            )}
          </div>
        )
      })}
    </div>
  )
}

function SegmentsBar({ slice }: { slice: any }) {
  const seg = slice?.segments?.[0]; const data = (seg?.data||[]).slice(0,12)
  if (!data.length) return <Placeholder msg="No segment data"/>
  return (
    <div style={{ height: Math.max(160, data.length*26) }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" margin={{left:80,right:30,top:4,bottom:4}}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" horizontal={false}/><XAxis type="number" {...AX} tickFormatter={(v:number)=>nf(v,0)}/><YAxis type="category" dataKey="category" {...AX} width={75}/>
          <Tooltip content={<MiniTip/>}/>{seg?.overall_mean&&<ReferenceLine x={seg.overall_mean} stroke={`${C.amber}60`} strokeDasharray="3 2"/>}
          <Bar dataKey="total" name={seg?.display_metric||'Value'} radius={[0,3,3,0]} maxBarSize={18}>{data.map((d:any,i:number)=><Cell key={i} fill={d.direction==='above'?C.green:C.coral} opacity={0.8}/>)}</Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

function TrendArea({ slice, cfg }: { slice: any; cfg: any }) {
  const tsItem = slice?.time_series?.[0]; const data = tsItem?.data||[]; const metrics = tsItem?.metrics||[]
  if (!data.length||!metrics.length) return <Placeholder msg="No trend data"/>
  return (
    <div style={{ height: 180 }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{top:4,right:8,bottom:4,left:0}}>
          <defs>{metrics.map((_:any,j:number)=><linearGradient key={j} id={`dtga${j}`} x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={SEQ[j%SEQ.length]} stopOpacity={0.4}/><stop offset="100%" stopColor={SEQ[j%SEQ.length]} stopOpacity={0.02}/></linearGradient>)}</defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false}/><XAxis dataKey="period" {...AX}/><YAxis {...AX} tickFormatter={(v:number)=>nf(v,0)}/><Tooltip content={<MiniTip/>}/>
          {metrics.map((m:any,j:number)=><Area key={m.key} type="monotone" dataKey={m.key} name={m.display_name} stroke={SEQ[j%SEQ.length]} strokeWidth={2} fill={`url(#dtga${j})`} dot={false}/>)}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}

function GrowthComposed({ slice }: { slice: any }) {
  const gr = slice?.growth_rates?.[0]; const data = (gr?.periods||[]).slice(0,30)
  if (!data.length) return <Placeholder msg="No growth data"/>
  return (
    <div style={{ height: 180 }}>
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={data} margin={{top:4,right:16,bottom:4,left:0}}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false}/>
          <XAxis dataKey="period" {...AX}/><YAxis yAxisId="l" {...AX} tickFormatter={(v:number)=>nf(v,0)}/><YAxis yAxisId="r" orientation="right" {...AX} tickFormatter={(v:number)=>`${(+v).toFixed(0)}%`}/><Tooltip content={<MiniTip/>}/>
          <Bar yAxisId="l" dataKey="value" name="Value" fill={`${C.blue}40`} radius={[2,2,0,0]} maxBarSize={20}/>
          <Line yAxisId="r" type="monotone" dataKey="growth_rate_pct" name="Growth %" stroke={C.gold} strokeWidth={2} dot={false}/>
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}

function DistributionHist({ slice }: { slice: any }) {
  const dist = slice?.distributions?.[0]; const hist = dist?.histogram||[]
  if (!hist.length) return <Placeholder msg="No distribution data"/>
  return (
    <div style={{ height: 160 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={hist} margin={{top:4,right:8,bottom:4,left:0}}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false}/><XAxis dataKey="label" {...AX} interval="preserveStartEnd"/><YAxis {...AX}/><Tooltip content={<MiniTip/>}/>
          <Bar dataKey="count" name="Count" radius={[2,2,0,0]}>{hist.map((_:any,i:number)=><Cell key={i} fill={`${C.purple}${Math.round(50+(i/hist.length)*180).toString(16).padStart(2,'0')}`}/>)}</Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

function CompositionPie({ slice }: { slice: any }) {
  const item = slice?.composition?.[0]; const data = item?.data||[]
  if (!data.length) return <Placeholder msg="No composition data"/>
  return (
    <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
      <div style={{ height: 140, flex: '0 0 140px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart><Pie data={data} dataKey="value" nameKey="name" outerRadius={60} innerRadius={28} paddingAngle={2} startAngle={90} endAngle={-270}>{data.map((_:any,i:number)=><Cell key={i} fill={SEQ[i%SEQ.length]}/>)}</Pie><Tooltip content={<MiniTip/>}/></PieChart>
        </ResponsiveContainer>
      </div>
      <div style={{ flex:1,display:'flex',flexDirection:'column',gap:4 }}>
        {data.slice(0,5).map((d:any,i:number)=>(
          <div key={i} style={{display:'flex',justifyContent:'space-between',fontSize:10,gap:4}}>
            <span style={{display:'flex',alignItems:'center',gap:4,color:'rgba(255,255,255,0.5)',minWidth:0}}><span style={{width:5,height:5,borderRadius:'50%',background:SEQ[i%SEQ.length],flexShrink:0}}/><span style={{overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{d.name}</span></span>
            <span style={{fontWeight:700,color:'rgba(255,255,255,0.8)',flexShrink:0}}>{d.pct?.toFixed(0)}%</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function CorrelationBar({ slice }: { slice: any }) {
  const cells = (slice?.correlation_matrix?.cells||[]).filter((c:any)=>c.x!==c.y)
  const seen = new Set<string>()
  const pairs = cells.reduce((acc:any[],c:any)=>{const k=[c.x,c.y].sort().join('|');if(!seen.has(k)){seen.add(k);acc.push({...c,label:`${c.x.slice(0,8)} ↔ ${c.y.slice(0,8)}`})}return acc},[]).sort((a:any,b:any)=>b.abs_value-a.abs_value).slice(0,6)
  if (!pairs.length) return <Placeholder msg="No correlation data"/>
  return (
    <div style={{ height: Math.max(120,pairs.length*22+30) }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={pairs} layout="vertical" margin={{left:110,right:30,top:4,bottom:4}}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" horizontal={false}/><XAxis type="number" domain={[-1,1]} {...AX}/><YAxis type="category" dataKey="label" {...AX} width={105}/><Tooltip content={<MiniTip/>}/><ReferenceLine x={0} stroke="rgba(255,255,255,0.12)"/>
          <Bar dataKey="value" name="r" radius={[0,2,2,0]} maxBarSize={14}>{pairs.map((d:any,i:number)=><Cell key={i} fill={d.value>=0?C.teal:C.coral} opacity={0.4+d.abs_value*0.6}/>)}</Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

function VsAvgBar({ slice }: { slice: any }) {
  const vsAvg = (slice?.percentage_changes||[]).find((x:any)=>x.type==='vs_average'); const data = (vsAvg?.data||[]).slice(0,10)
  if (!data.length) return <Placeholder msg="No vs-average data"/>
  return (
    <div style={{ height: 160 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{top:4,right:4,bottom:28,left:0}}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false}/>
          <XAxis dataKey="category" {...AX} tick={({x,y,payload}:any)=><text x={x} y={y+5} textAnchor="end" fontSize={7} fill="rgba(255,255,255,0.3)" transform={`rotate(-30,${x},${y})`}>{String(payload.value).slice(0,10)}</text>} height={30}/>
          <YAxis {...AX} tickFormatter={(v:number)=>`${(+v).toFixed(0)}%`}/><Tooltip content={<MiniTip/>}/><ReferenceLine y={0} stroke="rgba(255,255,255,0.18)"/>
          <Bar dataKey="pct_vs_average" name="vs Avg %" radius={[2,2,0,0]} maxBarSize={22}>{data.map((d:any,i:number)=><Cell key={i} fill={d.direction==='above'?C.green:C.coral} opacity={0.8}/>)}</Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

function TopBottomBar({ slice }: { slice: any }) {
  const tb = (slice?.percentage_changes||[]).find((x:any)=>x.type==='top_bottom_5')
  const data = [...(tb?.top_5||[]).map((d:any)=>({...d,_g:'Top'})),...(tb?.bottom_5||[]).slice().reverse().map((d:any)=>({...d,_g:'Bottom'}))]
  if (!data.length) return <Placeholder msg="No top/bottom data"/>
  return (
    <div style={{ height: Math.max(140,data.length*20) }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" margin={{left:75,right:40,top:4,bottom:4}}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" horizontal={false}/><XAxis type="number" {...AX} tickFormatter={(v:number)=>nf(v,0)}/><YAxis type="category" dataKey="category" {...AX} width={70}/><Tooltip content={<MiniTip/>}/>
          <Bar dataKey="value" name="Value" radius={[0,3,3,0]} maxBarSize={16}>{data.map((d:any,i:number)=><Cell key={i} fill={d._g==='Top'?C.green:C.coral} opacity={0.8}/>)}</Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

function RadarSpider({ slice }: { slice: any }) {
  const rd = (slice?.segments?.[0]?.data||[]).slice(0,8).map((d:any)=>({subject:String(d.category||'').slice(0,10),total:d.total??0,mean:d.mean??0}))
  if (rd.length<3) return <Placeholder msg="Not enough data"/>
  return (
    <div style={{ height: 180 }}>
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart data={rd}><PolarGrid stroke="rgba(255,255,255,0.07)"/><PolarAngleAxis dataKey="subject" tick={{fill:'rgba(255,255,255,0.35)',fontSize:9}}/><PolarRadiusAxis tick={{fill:'rgba(255,255,255,0.2)',fontSize:7}}/>
          <Radar name="Total" dataKey="total" stroke={C.gold} fill={C.gold} fillOpacity={0.12} strokeWidth={2}/>
          <Radar name="Mean" dataKey="mean" stroke={C.teal} fill={C.teal} fillOpacity={0.08} strokeWidth={1.5}/>
          <Tooltip content={<MiniTip/>}/>
        </RadarChart>
      </ResponsiveContainer>
    </div>
  )
}

function RankingBar({ slice }: { slice: any }) {
  const rnk = slice?.ranking?.[0]; const data = (rnk?.data||[]).slice(0,10)
  if (!data.length) return <Placeholder msg="No ranking data"/>
  return (
    <div style={{ height: Math.max(160,data.length*24) }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" margin={{left:80,right:50,top:4,bottom:4}}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" horizontal={false}/><XAxis type="number" {...AX} tickFormatter={(v:number)=>nf(v,0)}/><YAxis type="category" dataKey="category" {...AX} width={75}/><Tooltip content={<MiniTip/>}/>
          <Bar dataKey="value" name={rnk?.display_metric||'Value'} radius={[0,3,3,0]} maxBarSize={18}>{data.map((_:any,i:number)=><Cell key={i} fill={SEQ[i%SEQ.length]} opacity={0.85}/>)}</Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

function OutlierSeverity({ slice }: { slice: any }) {
  const out = slice?.outlier_detail?.[0]; const svd = out?.severity_data||[]
  if (!svd.length) return <Placeholder msg="No outlier data"/>
  return (
    <div style={{ height: 140 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={svd} margin={{top:4,right:8,bottom:4,left:0}}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false}/><XAxis dataKey="label" {...AX}/><YAxis {...AX}/><Tooltip content={<MiniTip/>}/>
          <Bar dataKey="count" name="Count" radius={[3,3,0,0]}>{svd.map((d:any,i:number)=><Cell key={i} fill={d.fill||C.coral} opacity={0.85}/>)}</Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

function CohortGrouped({ slice }: { slice: any }) {
  const coh = slice?.cohort?.[0]; const data = coh?.data||[]; const labels: string[] = coh?.col_labels||[]
  if (!data.length) return <Placeholder msg="No cohort data"/>
  return (
    <div style={{ height: 180 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{top:4,right:8,bottom:28,left:0}}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false}/>
          <XAxis dataKey="category" {...AX} tick={({x,y,payload}:any)=><text x={x} y={y+5} textAnchor="end" fontSize={8} fill="rgba(255,255,255,0.3)" transform={`rotate(-25,${x},${y})`}>{String(payload.value).slice(0,12)}</text>} height={30}/>
          <YAxis {...AX} tickFormatter={(v:number)=>nf(v,0)}/><Tooltip content={<MiniTip/>}/>
          {labels.map((l:string,i:number)=><Bar key={l} dataKey={l} name={l} fill={SEQ[i%SEQ.length]} radius={[2,2,0,0]} maxBarSize={20} opacity={0.85}/>)}
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

function MultiMetricRadar({ slice }: { slice: any }) {
  const mm = slice?.multi_metric?.[0]; const rd = mm?.radar_data||[]; const metrics: string[] = mm?.metrics||[]
  if (!rd.length) return <Placeholder msg="No multi-metric data"/>
  return (
    <div style={{ height: 200 }}>
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart data={rd}><PolarGrid stroke="rgba(255,255,255,0.07)"/><PolarAngleAxis dataKey="category" tick={{fill:'rgba(255,255,255,0.35)',fontSize:9}}/><PolarRadiusAxis tick={{fill:'rgba(255,255,255,0.2)',fontSize:7}}/>
          {metrics.slice(0,4).map((m,i)=><Radar key={m} name={m} dataKey={`${m}_norm`} stroke={SEQ[i%SEQ.length]} fill={SEQ[i%SEQ.length]} fillOpacity={0.1} strokeWidth={2}/>)}
          <Tooltip content={<MiniTip/>}/>
        </RadarChart>
      </ResponsiveContainer>
    </div>
  )
}

function PercentileBands({ slice }: { slice: any }) {
  const pbd = slice?.percentile_bands?.[0]; const bands = pbd?.bands||[]
  if (!bands.length) return <Placeholder msg="No percentile data"/>
  return (
    <div style={{ height: 140 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={bands} margin={{top:4,right:8,bottom:4,left:0}}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false}/><XAxis dataKey="label" {...AX}/><YAxis {...AX} tickFormatter={(v:number)=>nf(v,0)}/><Tooltip content={<MiniTip/>}/>
          {pbd?.mean&&<ReferenceLine y={pbd.mean} stroke={C.gold} strokeDasharray="4 2"/>}
          <Bar dataKey="value" name="Value" radius={[3,3,0,0]}>{bands.map((b:any,i:number)=><Cell key={i} fill={b.fill||SEQ[i%SEQ.length]}/>)}</Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

function ParetoComposed({ slice }: { slice: any }) {
  const prt = slice?.running_total?.[0]; const data = (prt?.data||[]).slice(0,20)
  if (!data.length) return <Placeholder msg="No Pareto data"/>
  return (
    <div style={{ height: 180 }}>
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={data} margin={{top:4,right:24,bottom:28,left:0}}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false}/>
          <XAxis dataKey="category" {...AX} tick={({x,y,payload}:any)=><text x={x} y={y+5} textAnchor="end" fontSize={7} fill="rgba(255,255,255,0.3)" transform={`rotate(-30,${x},${y})`}>{String(payload.value).slice(0,10)}</text>} height={30}/>
          <YAxis yAxisId="l" {...AX} tickFormatter={(v:number)=>nf(v,0)}/><YAxis yAxisId="r" orientation="right" {...AX} tickFormatter={(v:number)=>`${(+v).toFixed(0)}%`}/><Tooltip content={<MiniTip/>}/>
          <Bar yAxisId="l" dataKey="value" name="Value" radius={[2,2,0,0]} maxBarSize={24}>{data.map((d:any,i:number)=><Cell key={i} fill={d.is_vital_few?C.gold:`${C.gold}40`} opacity={0.85}/>)}</Bar>
          <Line yAxisId="r" type="monotone" dataKey="cumulative_pct" name="Cumulative %" stroke={C.coral} strokeWidth={2} dot={false}/>
          <ReferenceLine yAxisId="r" y={80} stroke={`${C.teal}60`} strokeDasharray="4 2"/>
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}

function HeatmapBar({ slice }: { slice: any }) {
  const cm = slice?.correlation_matrix; if(!cm?.columns?.length) return <Placeholder msg="No heatmap data"/>
  const col = cm.columns[0]; const cells = (cm.cells||[]).filter((c:any)=>c.x!==c.y)
  const data = cm.columns.slice(0,8).map((row:string)=>{const cell=cells.find((c:any)=>(c.x===row&&c.y===col)||(c.x===col&&c.y===row));return{name:row.slice(0,10),value:row===col?1:(cell?.value??0)}})
  return (
    <div style={{ height: 160 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{top:4,right:8,bottom:28,left:0}}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false}/>
          <XAxis dataKey="name" {...AX} tick={({x,y,payload}:any)=><text x={x} y={y+5} textAnchor="end" fontSize={8} fill="rgba(255,255,255,0.3)" transform={`rotate(-25,${x},${y})`}>{payload.value}</text>} height={30}/>
          <YAxis domain={[-1,1]} {...AX} tickFormatter={(v:number)=>v.toFixed(1)}/><Tooltip content={<MiniTip/>}/><ReferenceLine y={0} stroke="rgba(255,255,255,0.15)"/>
          <Bar dataKey="value" name={`r vs ${col?.slice(0,10)}`} radius={[2,2,0,0]} maxBarSize={32}>{data.map((d:any,i:number)=><Cell key={i} fill={d.value>=0?`rgba(0,206,209,${0.2+Math.abs(d.value)*0.8})`:`rgba(255,107,107,${0.2+Math.abs(d.value)*0.8})`}/>)}</Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

function ScatterDots({ slice }: { slice: any }) {
  const sct = slice?.scatter?.[0]; const data = (sct?.data||[]).slice(0,100)
  if (!data.length) return <Placeholder msg="No scatter data"/>
  return (
    <div style={{ height: 180 }}>
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart margin={{top:5,right:10,bottom:5,left:0}}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)"/>
          <XAxis type="number" dataKey="x" name={sct?.display_x} {...AX} tickFormatter={(v:number)=>nf(v,0)}/>
          <YAxis type="number" dataKey="y" name={sct?.display_y} {...AX} tickFormatter={(v:number)=>nf(v,0)}/><Tooltip content={<MiniTip/>}/>
          <Scatter data={data} fill={C.gold} opacity={0.75}/>
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  )
}

// ─── Previously missing subtypes — NEW RENDERERS ─────────────────────────────

function GaugeCard({ slice }: { slice: any }) {
  const gd: any[] = slice?.gauge || []
  const item = gd[0]
  if (!item) return <Placeholder msg="No gauge data" />
  const statusColor = item.status==='excellent'?C.green:item.status==='good'?C.teal:item.status==='warning'?C.amber:C.coral
  const pct = Math.min(100, item.gauge_pct || item.pct_of_target || 0)
  const allData = gd.map((g: any) => ({ name: g.display_name, value: g.gauge_pct||0, fill: g.status==='excellent'?C.green:g.status==='good'?C.teal:g.status==='warning'?C.amber:C.coral }))
  return (
    <div style={{ display: 'flex', gap: 14, alignItems: 'center' }}>
      <div style={{ flex: '0 0 110px', textAlign: 'center' }}>
        <p style={{ fontSize: 40, fontWeight: 900, color: statusColor, lineHeight: 1 }}>{pct.toFixed(0)}%</p>
        <p style={{ fontSize: 10, color: 'rgba(255,255,255,0.35)', marginTop: 4 }}>of target</p>
        <span style={{ display: 'inline-block', marginTop: 6, fontSize: 10, padding: '2px 8px', borderRadius: 20, background: `${statusColor}18`, color: statusColor, border: `1px solid ${statusColor}30`, fontWeight: 700 }}>{item.status}</span>
        <div style={{ marginTop: 8, display: 'flex', justifyContent: 'center', gap: 8 }}>
          <div><p style={{ fontSize: 9, color: 'rgba(255,255,255,0.3)' }}>Actual</p><p style={{ fontSize: 12, fontWeight: 700, color: statusColor }}>{item.formatted_actual}</p></div>
          <div><p style={{ fontSize: 9, color: 'rgba(255,255,255,0.3)' }}>Target</p><p style={{ fontSize: 12, fontWeight: 700, color: 'rgba(255,255,255,0.5)' }}>{item.formatted_target}</p></div>
        </div>
      </div>
      {allData.length > 1 && (
        <div style={{ flex: 1, height: 140 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={allData} layout="vertical" margin={{ left: 60, right: 40, top: 4, bottom: 4 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" horizontal={false} />
              <XAxis type="number" domain={[0, 100]} {...AX} tickFormatter={(v: number) => `${v}%`} />
              <YAxis type="category" dataKey="name" {...AX} width={55} />
              <Tooltip content={<MiniTip />} />
              <ReferenceLine x={100} stroke="rgba(255,255,255,0.2)" strokeDasharray="3 2" />
              <Bar dataKey="value" name="% of Target" radius={[0, 3, 3, 0]} maxBarSize={16}>
                {allData.map((d: any, i: number) => <Cell key={i} fill={d.fill} opacity={0.85} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}

function StatsTableCard({ slice }: { slice: any }) {
  const ss: any[] = slice?.summary_stats || []
  if (!ss.length) return <Placeholder msg="No statistics data" />
  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 10 }}>
        <thead>
          <tr>{['Column','Mean','Median','Std','Min','Max'].map((h: string) => (
            <th key={h} style={{ padding: '5px 8px', textAlign: h==='Column'?'left':'right', color: 'rgba(212,175,55,0.7)', borderBottom: '1px solid rgba(255,255,255,0.06)', fontWeight: 600 }}>{h}</th>
          ))}</tr>
        </thead>
        <tbody>
          {ss.slice(0,8).map((row: any, i: number) => (
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

function ConcentrationCard({ slice }: { slice: any }) {
  const conc: any[] = slice?.concentration || []
  const item = conc[0]
  if (!item) return <Placeholder msg="No concentration data" />
  const shares: any[] = (item.share_data || []).slice(0, 8)
  return (
    <div>
      <div style={{ display: 'flex', gap: 10, marginBottom: 10, flexWrap: 'wrap' }}>
        {([['Gini',`${item.gini_pct}%`,C.gold],['HHI',`${item.hhi_pct?.toFixed(1)}%`,C.amber],['Top 1',`${item.top1_share}%`,C.coral],['Level',item.concentration_level,C.teal]] as [string,string,string][]).map(([l,v,c]) => (
          <div key={l} style={{ flex:1, minWidth:60, padding:'8px', borderRadius:8, background:`${c}0a`, border:`1px solid ${c}20`, textAlign:'center' }}>
            <p style={{ fontSize:9, color:'rgba(255,255,255,0.3)' }}>{l}</p>
            <p style={{ fontSize:13, fontWeight:700, color:c }}>{v}</p>
          </div>
        ))}
      </div>
      {shares.length > 0 && (
        <div style={{ height: 130 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={shares} layout="vertical" margin={{ left: 70, right: 40, top: 4, bottom: 4 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" horizontal={false} />
              <XAxis type="number" {...AX} tickFormatter={(v: number) => `${v}%`} />
              <YAxis type="category" dataKey="category" {...AX} width={65} />
              <Tooltip content={<MiniTip />} />
              <Bar dataKey="share_pct" name="Share %" radius={[0, 3, 3, 0]} maxBarSize={16}>
                {shares.map((_: any, i: number) => <Cell key={i} fill={SEQ[i % SEQ.length]} opacity={0.85} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}

function VarCard({ slice }: { slice: any }) {
  const var_: any[] = slice?.value_at_risk || []
  const item = var_[0]
  if (!item) return <Placeholder msg="No VaR data" />
  const statusColor = item.risk_tier==='High'?C.coral:item.risk_tier==='Medium'?C.amber:C.green
  const hist: any[] = item.histogram || []
  return (
    <div>
      <div style={{ display: 'flex', gap: 10, marginBottom: 10, flexWrap: 'wrap' }}>
        {([['Risk Tier',item.risk_tier,statusColor],['VaR 95%',nf(item.var_95),C.amber],['CV%',`${item.cv_pct?.toFixed(1)}%`,statusColor],['Mean',nf(item.mean),C.gold]] as [string,string,string][]).map(([l,v,c]) => (
          <div key={l} style={{ flex:1, minWidth:60, padding:'8px', borderRadius:8, background:`${c}0a`, border:`1px solid ${c}20`, textAlign:'center' }}>
            <p style={{ fontSize:9, color:'rgba(255,255,255,0.3)' }}>{l}</p>
            <p style={{ fontSize:12, fontWeight:700, color:c }}>{v}</p>
          </div>
        ))}
      </div>
      {hist.length > 0 && (
        <div style={{ height: 120 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={hist} margin={{ top: 4, right: 8, bottom: 4, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
              <XAxis dataKey="bin" {...AX} interval="preserveStartEnd" />
              <YAxis {...AX} /><Tooltip content={<MiniTip />} />
              <Bar dataKey="count" name="Count" radius={[2, 2, 0, 0]}>
                {hist.map((d: any, i: number) => <Cell key={i} fill={d.is_risk ? C.coral : C.blue} opacity={0.8} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}

function MovingAvgCard({ slice }: { slice: any }) {
  const ms: any[] = slice?.moving_statistics || []
  const item = ms[0]; const data: any[] = (item?.data || []).slice(-40)
  if (!data.length) return <Placeholder msg="No moving average data" />
  return (
    <div style={{ height: 180 }}>
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={data} margin={{ top: 4, right: 8, bottom: 4, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
          <XAxis dataKey="index" {...AX} tickFormatter={(v: number) => `T${v+1}`} />
          <YAxis {...AX} tickFormatter={(v: number) => nf(v, 0)} /><Tooltip content={<MiniTip />} />
          <Bar dataKey="value" name="Actual" fill={`${C.blue}30`} radius={[2, 2, 0, 0]} maxBarSize={16} />
          <Line type="monotone" dataKey="ma3" name="MA3" stroke={C.gold} strokeWidth={2} dot={false} />
          <Line type="monotone" dataKey="ma7" name="MA7" stroke={C.teal} strokeWidth={1.5} dot={false} strokeDasharray="4 2" />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}

function BenchmarkCard({ slice }: { slice: any }) {
  const bm: any[] = slice?.benchmark_comparison || []
  if (!bm.length) return <Placeholder msg="No benchmark data" />
  return (
    <div style={{ height: Math.max(140, bm.length * 34) }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={bm} layout="vertical" margin={{ left: 90, right: 70, top: 4, bottom: 4 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" horizontal={false} />
          <XAxis type="number" {...AX} tickFormatter={(v: number) => nf(v, 0)} />
          <YAxis type="category" dataKey="display_name" {...AX} width={85} />
          <Tooltip content={<MiniTip />} />
          <Legend wrapperStyle={{ fontSize: 10 }} />
          <Bar dataKey="actual" name="Actual" radius={[0, 3, 3, 0]} maxBarSize={16}>
            {bm.map((d: any, i: number) => <Cell key={i} fill={d.status==='above' ? C.green : C.coral} opacity={0.85} />)}
          </Bar>
          <Bar dataKey="benchmark" name="Benchmark" fill={`${C.blue}50`} radius={[0, 3, 3, 0]} maxBarSize={8} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

function QualityCard({ slice }: { slice: any }) {
  const dq: any[] = slice?.data_quality_detail || []
  if (!dq.length) return <Placeholder msg="No quality data" />
  return (
    <div style={{ height: Math.max(120, dq.length * 24) }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={dq} layout="vertical" margin={{ left: 90, right: 60, top: 4, bottom: 4 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" horizontal={false} />
          <XAxis type="number" domain={[0, 100]} {...AX} tickFormatter={(v: number) => `${v}%`} />
          <YAxis type="category" dataKey="display_name" {...AX} width={85} />
          <Tooltip content={<MiniTip />} />
          <ReferenceLine x={80} stroke={`${C.green}60`} strokeDasharray="3 2" />
          <Bar dataKey="quality_score" name="Quality %" radius={[0, 3, 3, 0]} maxBarSize={16}>
            {dq.map((d: any, i: number) => <Cell key={i} fill={d.fill || C.green} opacity={0.85} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

function FrequencyCard({ slice }: { slice: any }) {
  const fa: any[] = slice?.frequency_analysis || []
  const item = fa[0]; const data: any[] = (item?.data || []).slice(0, 12)
  if (!data.length) return <Placeholder msg="No frequency data" />
  return (
    <div style={{ height: 160 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" margin={{ left: 90, right: 50, top: 4, bottom: 4 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" horizontal={false} />
          <XAxis type="number" {...AX} tickFormatter={(v: number) => `${v}%`} />
          <YAxis type="category" dataKey="category" {...AX} width={85} />
          <Tooltip content={<MiniTip />} />
          <Bar dataKey="pct" name="Share %" radius={[0, 3, 3, 0]} maxBarSize={18}>
            {data.map((_: any, i: number) => <Cell key={i} fill={SEQ[i % SEQ.length]} opacity={0.85} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

function DecompCard({ slice }: { slice: any }) {
  const td: any[] = slice?.time_decomposition || []
  const item = td[0]; const data: any[] = (item?.data || []).slice(-40)
  if (!data.length) return <Placeholder msg="No decomposition data" />
  const trendColor = item?.trend_direction === 'upward' ? C.green : C.coral
  return (
    <div style={{ height: 180 }}>
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={data} margin={{ top: 4, right: 8, bottom: 4, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
          <XAxis dataKey="period" {...AX} />
          <YAxis {...AX} tickFormatter={(v: number) => nf(v, 0)} /><Tooltip content={<MiniTip />} />
          <Area type="monotone" dataKey="actual" name="Actual" stroke={C.blue} fill={`${C.blue}20`} strokeWidth={1.5} dot={false} />
          <Line type="monotone" dataKey="trend" name="Trend" stroke={trendColor} strokeWidth={2} dot={false} strokeDasharray="5 3" />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}

// ─── KPI item ─────────────────────────────────────────────────────────────────
function renderKpiItem(item: DashItem) {
  const col = SUBTYPE_COLOR[item.subtype] || C.gold
  const pct = item.data?.pct_change
  const isPos = (pct ?? 0) > 0, isFlat = Math.abs(pct ?? 0) < 0.5
  return (
    <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', padding: '8px 0' }}>
      <p style={{ fontSize: 38, fontWeight: 900, color: col, lineHeight: 1 }}>{item.data?.formatted_value || nf(item.data?.value) || '–'}</p>
      {item.data?.formatted_total && <p style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)', marginTop: 6 }}>Σ {item.data.formatted_total}</p>}
      {pct != null && (
        <span style={{ fontSize: 12, fontWeight: 700, marginTop: 10, display: 'inline-flex', alignItems: 'center', gap: 4, padding: '4px 10px', borderRadius: 8, width: 'fit-content',
          color: isFlat ? '#9ca3af' : isPos ? '#34d399' : '#f87171',
          background: isFlat ? 'rgba(255,255,255,0.05)' : isPos ? 'rgba(52,211,153,0.1)' : 'rgba(248,113,113,0.1)' }}>
          {isFlat ? <Minus style={{width:10,height:10}}/> : isPos ? <ArrowUpRight style={{width:10,height:10}}/> : <ArrowDownRight style={{width:10,height:10}}/>}
          {Math.abs(pct).toFixed(1)}% change
        </span>
      )}
    </div>
  )
}

// ─── Widget Card ──────────────────────────────────────────────────────────────
function WidgetCard({ item, onRemove, dragHandleProps, isDragging }: {
  item: DashItem; onRemove: () => void; dragHandleProps?: any; isDragging?: boolean
}) {
  const [zoomed, setZoomed] = useState(false)
  const Icon = SUBTYPE_ICON[item.subtype] || BarChart3
  const color = SUBTYPE_COLOR[item.subtype] || C.gold
  const isKpi = item.type === 'kpi'
  const content = isKpi ? renderKpiItem(item) : renderChart(item)

  return (
    <>
      {zoomed && (
        <div style={{ position:'fixed',inset:0,zIndex:200,display:'flex',alignItems:'center',justifyContent:'center',padding:16,background:'rgba(0,0,0,0.9)',backdropFilter:'blur(12px)' }} onClick={() => setZoomed(false)}>
          <div style={{ maxWidth:860,width:'100%',background:'#0d0d18',border:'1px solid rgba(212,175,55,0.2)',borderRadius:20,overflow:'hidden' }} onClick={e=>e.stopPropagation()}>
            <div style={{ padding:'14px 20px',borderBottom:'1px solid rgba(255,255,255,0.06)',display:'flex',justifyContent:'space-between',alignItems:'center' }}>
              <div><p style={{ fontWeight:700,color:'#fff',fontSize:15 }}>{item.title}</p><p style={{ fontSize:11,color:'rgba(255,255,255,0.35)',marginTop:2 }}>{item.jobName} · {new Date(item.pinnedAt).toLocaleDateString()}</p></div>
              <button onClick={()=>setZoomed(false)} style={{ padding:6,borderRadius:8,background:'rgba(255,255,255,0.05)',border:'1px solid rgba(255,255,255,0.08)',color:'rgba(255,255,255,0.5)',cursor:'pointer' }}><X style={{width:15,height:15}}/></button>
            </div>
            <div style={{ padding:24 }}>{content}</div>
            {item.jobId !== 'custom' && (
              <div style={{ padding:'12px 20px',borderTop:'1px solid rgba(255,255,255,0.05)',display:'flex',justifyContent:'flex-end' }}>
                <Link to={`/jobs/${item.jobId}`} style={{ fontSize:12,color:C.gold,display:'flex',alignItems:'center',gap:4 }}>Open full analysis <ArrowRight style={{width:12,height:12}}/></Link>
              </div>
            )}
          </div>
        </div>
      )}

      <div style={{
        background: isDragging ? 'rgba(212,175,55,0.06)' : 'rgba(255,255,255,0.02)',
        border: `1px solid ${isDragging ? 'rgba(212,175,55,0.3)' : 'rgba(255,255,255,0.07)'}`,
        borderRadius:16, overflow:'hidden', display:'flex', flexDirection:'column',
        minHeight: isKpi ? 140 : 240,
        transition:'border-color 0.15s, box-shadow 0.15s, transform 0.15s',
        transform: isDragging ? 'scale(1.01)' : 'scale(1)',
        boxShadow: isDragging ? `0 8px 32px rgba(212,175,55,0.15)` : 'none',
        cursor: isDragging ? 'grabbing' : 'default',
      }}>
        <div style={{ padding:'11px 14px',borderBottom:'1px solid rgba(255,255,255,0.05)',display:'flex',alignItems:'center',justifyContent:'space-between',gap:8 }}>
          <div style={{ display:'flex',alignItems:'center',gap:8,minWidth:0 }}>
            <div {...dragHandleProps} style={{ cursor:'grab',color:'rgba(255,255,255,0.2)',flexShrink:0,display:'flex',alignItems:'center',touchAction:'none' }}>
              <GripVertical style={{width:13,height:13}}/>
            </div>
            <div style={{ width:24,height:24,borderRadius:6,display:'flex',alignItems:'center',justifyContent:'center',background:`${color}18`,flexShrink:0 }}>
              <Icon style={{width:12,height:12,color}}/>
            </div>
            <p style={{ fontSize:12,fontWeight:600,color:'#fff',overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap' }}>{item.title}</p>
          </div>
          <div style={{ display:'flex',gap:4,flexShrink:0 }}>
            <button onClick={()=>setZoomed(true)} title="Zoom" style={{ padding:4,borderRadius:6,background:'rgba(255,255,255,0.04)',border:'1px solid rgba(255,255,255,0.07)',color:'rgba(255,255,255,0.4)',cursor:'pointer' }}><ZoomIn style={{width:11,height:11}}/></button>
            {item.jobId !== 'custom' && (
              <Link to={`/jobs/${item.jobId}`} title="Open analysis" style={{ padding:4,borderRadius:6,background:'rgba(255,255,255,0.04)',border:'1px solid rgba(255,255,255,0.07)',color:'rgba(255,255,255,0.4)',display:'flex',alignItems:'center' }}><ArrowRight style={{width:11,height:11}}/></Link>
            )}
            <button onClick={onRemove} title="Remove" style={{ padding:4,borderRadius:6,background:'rgba(255,107,107,0.07)',border:'1px solid rgba(255,107,107,0.15)',color:'#FF6B6B',cursor:'pointer' }}><X style={{width:11,height:11}}/></button>
          </div>
        </div>
        <div style={{ padding:'12px 14px',flex:1 }}>{content}</div>
        <div style={{ padding:'7px 14px',borderTop:'1px solid rgba(255,255,255,0.04)',display:'flex',justifyContent:'space-between',fontSize:10,color:'rgba(255,255,255,0.22)' }}>
          <span style={{ overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap',maxWidth:160,color }}>{item.jobName}</span>
          <span>{new Date(item.pinnedAt).toLocaleDateString()}</span>
        </div>
      </div>
    </>
  )
}

// ─── Header stats ─────────────────────────────────────────────────────────────
function HeaderStats({ items }: { items: DashItem[] }) {
  const charts = items.filter(i => i.type !== 'kpi').length
  const kpis   = items.filter(i => i.type === 'kpi').length
  const jobs   = new Set(items.map(i => i.jobId)).size
  return (
    <div style={{ display:'grid',gridTemplateColumns:'repeat(3,1fr)',gap:10,marginBottom:20 }}>
      {[{label:'Charts',value:charts,col:C.gold,icon:BarChart3},{label:'KPIs',value:kpis,col:C.teal,icon:Target},{label:'Sources',value:jobs,col:C.green,icon:TrendingUp}].map(s => (
        <div key={s.label} style={{ padding:'14px 16px',borderRadius:12,background:'rgba(255,255,255,0.02)',border:'1px solid rgba(255,255,255,0.06)',display:'flex',alignItems:'center',gap:10 }}>
          <div style={{ width:32,height:32,borderRadius:9,display:'flex',alignItems:'center',justifyContent:'center',background:`${s.col}14`,flexShrink:0 }}><s.icon style={{width:16,height:16,color:s.col}}/></div>
          <div><p style={{fontSize:22,fontWeight:900,color:s.col,lineHeight:1}}>{s.value}</p><p style={{fontSize:11,color:'rgba(255,255,255,0.35)',marginTop:2}}>{s.label}</p></div>
        </div>
      ))}
    </div>
  )
}

// ─── Export PDF — captures SVG from rendered charts ───────────────────────────
function exportDashboard(items: DashItem[]) {
  // 1. Collect all rendered SVG charts from the DOM
  const captureCards = () => {
    const cards = Array.from(document.querySelectorAll('[data-dash-card]'))
    return cards.map((card) => {
      const el = card as HTMLElement
      const title = el.dataset.dashTitle || 'Chart'
      const color = el.dataset.dashColor || '#D4AF37'
      const svgEl = el.querySelector('svg')
      let bodyHtml = ''
      if (svgEl) {
        try {
          const clone = svgEl.cloneNode(true) as SVGElement
          // Fix SVG dimensions for export
          clone.setAttribute('width', '520')
          clone.setAttribute('height', '240')
          const serialized = new XMLSerializer().serializeToString(clone)
          const b64 = btoa(unescape(encodeURIComponent(serialized)))
          bodyHtml = `<div class="chart-img"><img src="data:image/svg+xml;base64,${b64}" width="100%" style="max-height:240px;object-fit:contain;background:rgba(0,0,0,0.15);display:block"/></div>`
        } catch {
          bodyHtml = `<div class="body-text">Chart: ${title}</div>`
        }
      } else {
        // KPI or text fallback
        const inner = el.querySelector('[data-dash-content]') as HTMLElement
        bodyHtml = inner ? `<div class="body-text">${inner.innerText.slice(0, 300)}</div>` : `<div class="body-text">${title}</div>`
      }
      return { title, color, bodyHtml }
    })
  }

  const captured = captureCards()

  // 2. For items not captured from DOM (already unmounted), use summary
  const capturedTitles = new Set(captured.map(c => c.title))
  const fallbackItems = items.filter(i => !capturedTitles.has(i.title)).map(item => {
    const color = SUBTYPE_COLOR[item.subtype] || '#D4AF37'
    let bodyHtml = ''
    if (item.type === 'kpi') {
      const pct = item.data?.pct_change
      bodyHtml = `<div class="kpi-val" style="color:${color}">${item.data?.formatted_value || item.data?.value || '–'}</div>${pct != null ? `<div class="kpi-delta">${pct > 0 ? '▲' : '▼'} ${Math.abs(pct).toFixed(1)}%</div>` : ''}`
    } else if (item.image_base64) {
      bodyHtml = `<div class="chart-img"><img src="data:image/png;base64,${item.image_base64}" style="width:100%;max-height:200px;object-fit:contain"/></div>`
    } else {
      const s = item.analyticsSlice
      const summary = Array.isArray(s) && s.length ? `${s.length} data points · ${item.subtype} chart`
        : s?.kpis ? s.kpis.slice(0,3).map((k:any)=>`${k.display_name}: ${k.formatted_value||k.value}`).join(' · ')
        : `${item.subtype} visualization`
      bodyHtml = `<div class="body-text">${summary}</div>`
    }
    return { title: item.title, color, bodyHtml }
  })

  const allCards = [...captured, ...fallbackItems]

  const html = `<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>DataFlow Dashboard Export</title>
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  body{font-family:system-ui,sans-serif;background:#080810;color:#e0e0e0;padding:28px 20px;background-image:radial-gradient(ellipse at 0% 0%,rgba(212,175,55,.06) 0%,transparent 60%)}
  .hdr{text-align:center;margin-bottom:24px;padding:24px;background:rgba(212,175,55,.06);border:1px solid rgba(212,175,55,.15);border-radius:16px}
  .logo{font-size:1.5em;font-weight:900;color:#D4AF37;margin-bottom:6px}
  .stats{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:24px}
  .stat{padding:14px;background:rgba(255,255,255,.02);border:1px solid rgba(212,175,55,.1);border-radius:10px;text-align:center}
  .stat-val{font-size:1.8em;font-weight:900;color:#D4AF37}
  .stat-lbl{font-size:.75em;color:rgba(255,255,255,.35);margin-top:2px}
  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(460px,1fr));gap:14px}
  .card{background:rgba(255,255,255,.02);border:1px solid rgba(212,175,55,.1);border-radius:14px;overflow:hidden;break-inside:avoid}
  .card-hdr{display:flex;align-items:center;gap:8px;padding:11px 14px;border-bottom:1px solid rgba(255,255,255,.05);font-weight:600;font-size:.88em;color:#fff}
  .dot{width:7px;height:7px;border-radius:50%;flex-shrink:0}
  .chart-img{background:rgba(0,0,0,.2)}
  .chart-img img{display:block;width:100%}
  .body-text{padding:14px;font-size:.8em;color:rgba(255,255,255,.5);line-height:1.6;min-height:50px}
  .kpi-val{font-size:2.4em;font-weight:900;padding:16px 14px 4px}
  .kpi-delta{font-size:.85em;padding:0 14px 14px;color:rgba(255,255,255,.5)}
  .ftr{padding:7px 14px;border-top:1px solid rgba(255,255,255,.04);font-size:.72em;color:rgba(255,255,255,.25)}
  @media print{body{background:#fff!important;color:#111!important}.card{background:#fff!important;border-color:rgba(0,0,0,.12)!important}.card-hdr{color:#111!important}}
</style></head>
<body>
<div class="hdr"><div class="logo">✦ DataFlow</div><div style="color:rgba(255,255,255,.35);font-size:.85em">Dashboard Export · ${new Date().toLocaleDateString('en-US',{year:'numeric',month:'long',day:'numeric'})} · ${items.length} pinned items</div></div>
<div class="stats">
  <div class="stat"><div class="stat-val">${items.filter(i=>i.type!=='kpi').length}</div><div class="stat-lbl">Charts</div></div>
  <div class="stat"><div class="stat-val">${items.filter(i=>i.type==='kpi').length}</div><div class="stat-lbl">KPIs</div></div>
  <div class="stat"><div class="stat-val">${new Set(items.map(i=>i.jobId)).size}</div><div class="stat-lbl">Analyses</div></div>
</div>
<div class="grid">
${allCards.map((c, idx) => {
  const item = items.find(i => i.title === c.title)
  const jobName = item?.jobName || 'DataFlow'
  const pinnedAt = item ? new Date(item.pinnedAt).toLocaleDateString() : ''
  return `<div class="card">
  <div class="card-hdr"><div class="dot" style="background:${c.color}"></div>${c.title}</div>
  ${c.bodyHtml}
  <div class="ftr">${jobName}${pinnedAt ? ' · ' + pinnedAt : ''}</div>
</div>`
}).join('\n')}
</div>
<div style="margin-top:24px;text-align:center;font-size:.75em;color:rgba(255,255,255,.2)">Generated by DataFlow Enterprise Analytics · ${new Date().toISOString().split('T')[0]}</div>
</body></html>`

  const win = window.open('', '_blank')
  if (!win) { alert('Please allow pop-ups to export PDF'); return }
  win.document.write(html)
  win.document.close()
  setTimeout(() => win.print(), 800)
}

// ─── Drag & Drop ─────────────────────────────────────────────────────────────
function useDragReorder(items: DashItem[], reorderItems: (items: DashItem[]) => void) {
  const dragIdx = useRef<number | null>(null)
  const onDragStart = useCallback((idx: number) => (e: React.DragEvent) => { dragIdx.current = idx; e.dataTransfer.effectAllowed = 'move' }, [])
  const onDragOver  = useCallback((_idx: number) => (e: React.DragEvent) => { e.preventDefault(); e.dataTransfer.dropEffect = 'move' }, [])
  const onDrop = useCallback((idx: number) => (e: React.DragEvent) => {
    e.preventDefault(); const from = dragIdx.current
    if (from === null || from === idx) return
    const newList = [...items]; const [moved] = newList.splice(from, 1); newList.splice(idx, 0, moved)
    reorderItems(newList); dragIdx.current = null
  }, [items, reorderItems])
  const onDragEnd = useCallback(() => { dragIdx.current = null }, [])
  return { onDragStart, onDragOver, onDrop, onDragEnd }
}

// ─── Main Page ────────────────────────────────────────────────────────────────
export function MyDashboardPage() {
  const { items, removeItem, reorderItems, clearAll } = useDashboard()
  const [layout, setLayout] = useState<2 | 3>(2)
  const [filter, setFilter] = useState('All')
  const [draggingId, setDraggingId] = useState<string | null>(null)
  const { onDragStart, onDragOver, onDrop, onDragEnd } = useDragReorder(items, reorderItems)

  const filterOpts = (() => {
    const types = new Set(items.map(i => i.type === 'kpi' ? 'KPI' : i.subtype))
    return ['All', ...Array.from(types)]
  })()

  const filtered = filter === 'All' ? items
    : filter === 'KPI' ? items.filter(i => i.type === 'kpi')
    : items.filter(i => i.subtype === filter)

  if (items.length === 0) return (
    <div>
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 24, fontWeight: 900, color: '#fff', marginBottom: 5 }}>My Dashboard</h1>
        <p style={{ color: 'rgba(255,255,255,0.35)', fontSize: 13 }}>Pin charts from any analysis to build your custom view</p>
      </div>
      <div style={{ padding: '64px 24px', textAlign: 'center', background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(212,175,55,0.1)', borderRadius: 20 }}>
        <div style={{ width:60,height:60,borderRadius:14,background:'rgba(212,175,55,0.06)',border:'1px solid rgba(212,175,55,0.12)',display:'flex',alignItems:'center',justifyContent:'center',margin:'0 auto 18px' }}>
          <LayoutDashboard style={{width:30,height:30,color:'rgba(212,175,55,0.4)'}}/>
        </div>
        <h3 style={{ fontWeight:700,color:'#fff',marginBottom:8 }}>Your dashboard is empty</h3>
        <p style={{ fontSize:13,color:'rgba(255,255,255,0.35)',maxWidth:340,margin:'0 auto 22px',lineHeight:1.6 }}>
          Open any analysis or Custom Analytics and click the <b style={{color:'#D4AF37'}}>+ Dashboard</b> button on any chart.
        </p>
        <div style={{ display:'flex',gap:10,justifyContent:'center',flexWrap:'wrap' }}>
          <Link to="/jobs" style={{ display:'inline-flex',alignItems:'center',gap:6,padding:'9px 18px',borderRadius:10,background:'rgba(212,175,55,0.12)',border:'1px solid rgba(212,175,55,0.25)',color:'#D4AF37',fontWeight:600,fontSize:12,textDecoration:'none' }}>
            <Plus style={{width:13,height:13}}/> Browse Jobs
          </Link>
          <Link to="/custom" style={{ display:'inline-flex',alignItems:'center',gap:6,padding:'9px 18px',borderRadius:10,background:'rgba(0,206,209,0.1)',border:'1px solid rgba(0,206,209,0.2)',color:'#00CED1',fontWeight:600,fontSize:12,textDecoration:'none' }}>
            Custom Analytics
          </Link>
        </div>
      </div>
    </div>
  )

  return (
    <div>
      <div style={{ display:'flex',alignItems:'flex-start',justifyContent:'space-between',marginBottom:20,flexWrap:'wrap',gap:12 }}>
        <div>
          <h1 style={{ fontSize:24,fontWeight:900,color:'#fff',marginBottom:3 }}>My Dashboard</h1>
          <p style={{ color:'rgba(255,255,255,0.35)',fontSize:12 }}>
            {items.length} pinned · {new Set(items.map(i=>i.jobId)).size} sources
            <span style={{color:'rgba(255,255,255,0.2)',marginLeft:8}}>· drag ⠿ to reorder</span>
          </p>
        </div>
        <div style={{ display:'flex',alignItems:'center',gap:7,flexWrap:'wrap' }}>
          <div style={{ display:'flex',gap:2,padding:3,background:'rgba(255,255,255,0.04)',border:'1px solid rgba(255,255,255,0.06)',borderRadius:8 }}>
            {([2, 3] as const).map(n => {
              const Icon = n === 2 ? LayoutList : Grid3x3
              return (
                <button key={n} onClick={() => setLayout(n)} style={{ padding:'5px 6px',borderRadius:5,cursor:'pointer',transition:'all 0.15s',background:layout===n?'rgba(212,175,55,0.18)':'transparent',border:layout===n?'1px solid rgba(212,175,55,0.3)':'1px solid transparent',color:layout===n?C.gold:'rgba(255,255,255,0.35)' }}>
                  <Icon style={{width:13,height:13}}/>
                </button>
              )
            })}
          </div>
          <button onClick={() => exportDashboard(items)} style={{ display:'flex',alignItems:'center',gap:5,padding:'7px 13px',borderRadius:9,fontSize:12,fontWeight:600,cursor:'pointer',background:'rgba(46,204,113,0.08)',border:'1px solid rgba(46,204,113,0.2)',color:'#2ECC71' }}>
            <Download style={{width:12,height:12}}/> Export PDF
          </button>
          <button onClick={clearAll} style={{ display:'flex',alignItems:'center',gap:5,padding:'7px 13px',borderRadius:9,fontSize:12,cursor:'pointer',background:'rgba(255,107,107,0.06)',border:'1px solid rgba(255,107,107,0.14)',color:'#FF6B6B' }}>
            <Trash2 style={{width:12,height:12}}/> Clear All
          </button>
        </div>
      </div>

      <HeaderStats items={items} />

      {filterOpts.length > 2 && (
        <div style={{ display:'flex',flexWrap:'wrap',gap:5,marginBottom:16 }}>
          {filterOpts.slice(0, 10).map(opt => (
            <button key={opt} onClick={() => setFilter(opt)} style={{ padding:'4px 11px',borderRadius:20,fontSize:11,cursor:'pointer',fontWeight:filter===opt?700:400,background:filter===opt?'rgba(212,175,55,0.12)':'rgba(255,255,255,0.03)',border:`1px solid ${filter===opt?'rgba(212,175,55,0.3)':'rgba(255,255,255,0.06)'}`,color:filter===opt?C.gold:'rgba(255,255,255,0.4)' }}>
              {opt}
            </button>
          ))}
        </div>
      )}

      {filtered.length === 0 ? (
        <div style={{ padding:40,textAlign:'center',background:'rgba(255,255,255,0.02)',borderRadius:14,border:'1px solid rgba(255,255,255,0.06)' }}>
          <RefreshCw style={{width:26,height:26,opacity:0.2,margin:'0 auto 10px',color:'#fff'}}/>
          <p style={{color:'rgba(255,255,255,0.35)'}}>No items in this category</p>
        </div>
      ) : (
        <div style={{ display:'grid',gridTemplateColumns:layout===3?'repeat(auto-fill, minmax(320px,1fr))':'repeat(auto-fill, minmax(440px,1fr))',gap:14 }}>
          {filtered.map((item) => {
            const globalIdx = items.indexOf(item)
            return (
              <div
                key={item.id}
                data-dash-card="true"
                data-dash-title={item.title}
                data-dash-color={SUBTYPE_COLOR[item.subtype] || C.gold}
                draggable
                onDragStart={e => { setDraggingId(item.id); onDragStart(globalIdx)(e) }}
                onDragOver={onDragOver(globalIdx)}
                onDrop={e => { onDrop(globalIdx)(e); setDraggingId(null) }}
                onDragEnd={() => { onDragEnd(); setDraggingId(null) }}
              >
                <WidgetCard
                  item={item}
                  onRemove={() => removeItem(item.id)}
                  isDragging={draggingId === item.id}
                  dragHandleProps={{ onMouseDown: (e: React.MouseEvent) => e.stopPropagation() }}
                />
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
