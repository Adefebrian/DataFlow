import { useState, useMemo } from 'react'
import {
  ResponsiveContainer, LineChart, Line, AreaChart, Area, BarChart, Bar,
  PieChart, Pie, Cell, ScatterChart, Scatter, CartesianGrid, XAxis,
  YAxis, Tooltip, Legend, RadarChart, Radar, PolarGrid, PolarAngleAxis,
  PolarRadiusAxis, ComposedChart, LabelList, ReferenceLine, Brush,
} from 'recharts'
import {
  TrendingUp, Minus, Activity, PieChart as PieIcon,
  BarChart3, Filter, ChevronDown, Sparkles, Target, Zap, Info,
  ArrowUpRight, ArrowDownRight, Eye, BarChart2, Layers, GitBranch,
  Clock, Award, Hash,
} from 'lucide-react'

// ─────────────────────────────────────────────
// TYPES
// ─────────────────────────────────────────────
type AnalyticsPayload = {
  success?: boolean
  kpis?: any[]
  time_series?: any[]
  distributions?: any[]
  segments?: any[]
  correlation_matrix?: { cells?: any[]; top_correlations?: any[] }
  percentage_changes?: any[]
  boxplots?: any[]
  composition?: any[]
  scatter?: any[]
  growth_rates?: any[]
  meta?: Record<string, any>
}
type Props = { analytics: AnalyticsPayload | null }

// ─────────────────────────────────────────────
// PALETTE
// ─────────────────────────────────────────────
const PALETTE = {
  gold:    '#D4AF37',
  teal:    '#00CED1',
  coral:   '#FF6B6B',
  purple:  '#9B59B6',
  emerald: '#2ECC71',
  amber:   '#F39C12',
  blue:    '#3498DB',
  pink:    '#E91E63',
}
const COLOR_SEQ = Object.values(PALETTE)

// ─────────────────────────────────────────────
// UTILS
// ─────────────────────────────────────────────
function num(v: any, decimals = 1): string {
  if (v === null || v === undefined || Number.isNaN(Number(v))) return '–'
  const n = Number(v)
  if (Math.abs(n) >= 1_000_000_000) return `${(n / 1e9).toFixed(decimals)}B`
  if (Math.abs(n) >= 1_000_000)     return `${(n / 1e6).toFixed(decimals)}M`
  if (Math.abs(n) >= 1_000)         return `${(n / 1e3).toFixed(decimals)}K`
  return n.toLocaleString(undefined, { maximumFractionDigits: 2 })
}
function pct(v: any): string {
  if (v === null || v === undefined) return '–'
  return `${Number(v).toFixed(1)}%`
}

// ─────────────────────────────────────────────
// CUSTOM TOOLTIP
// ─────────────────────────────────────────────
function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null
  return (
    <div className="rounded-xl px-4 py-3 shadow-2xl text-sm min-w-[140px]" style={{ background:'#10101c', border:'1px solid rgba(212,175,55,0.12)' }}>
      {label && <p className="text-gray-400 mb-2 text-xs font-medium pb-1.5" style={{ borderBottom:'1px solid rgba(212,175,55,0.08)' }}>{label}</p>}
      {payload.map((p: any, i: number) => (
        <div key={i} className="flex items-center justify-between gap-4 py-0.5">
          <span className="flex items-center gap-1.5 text-gray-300">
            <span className="w-2 h-2 rounded-full inline-block shrink-0" style={{ background: p.color }} />
            <span className="truncate max-w-[120px]">{p.name}</span>
          </span>
          <span className="font-bold text-white ml-2">{num(p.value)}</span>
        </div>
      ))}
    </div>
  )
}



// ─────────────────────────────────────────────
// SECTION WRAPPER
// ─────────────────────────────────────────────
function Section({
  title, subtitle, icon: Icon, iconColor = '#D4AF37',
  children, badge, className = '', headerRight,
}: {
  title: string; subtitle?: string; icon?: any; iconColor?: string
  children: React.ReactNode; badge?: string; className?: string; headerRight?: React.ReactNode
}) {
  return (
    <div className={`glass rounded-2xl overflow-hidden ${className}`}>
      <div className="px-5 py-4 section-divider flex items-center justify-between gap-3">
        <div className="flex items-center gap-3 min-w-0">
          {Icon && (
            <div className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0" style={{ background: `${iconColor}18` }}>
              <Icon className="w-4 h-4" style={{ color: iconColor }} />
            </div>
          )}
          <div className="min-w-0">
            <h3 className="text-white font-semibold text-sm">{title}</h3>
            {subtitle && <p className="text-gray-500 text-xs mt-0.5 line-clamp-1">{subtitle}</p>}
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          {badge && <span className="text-xs px-2.5 py-1 rounded-full text-gray-500" style={{ background:'rgba(212,175,55,0.06)', border:'1px solid rgba(212,175,55,0.1)' }}>{badge}</span>}
          {headerRight}
        </div>
      </div>
      <div className="p-5">{children}</div>
    </div>
  )
}

// ─────────────────────────────────────────────
// KPI CARD
// ─────────────────────────────────────────────
function KpiCard({ kpi, idx, selected, onClick }: { kpi: any; idx: number; selected: boolean; onClick: () => void }) {
  const color = COLOR_SEQ[idx % COLOR_SEQ.length]
  const pctChange = kpi.pct_change
  const isPos = (pctChange ?? 0) > 0
  const isNeutral = Math.abs(pctChange ?? 0) < 0.5
  const sparkData = (kpi.sparkline || []).map((v: number, i: number) => ({ i, v }))

  return (
    <button
      onClick={onClick}
      className="glass-light p-4 rounded-xl transition-all duration-300 text-left w-full group"
      style={selected
        ? { borderColor: `${color}60`, background: `${color}0a`, boxShadow: `0 0 20px ${color}18` }
        : { '--hover-color': color } as any
      }
    >
      <div className="flex items-start justify-between mb-2">
        <p className="text-xs text-gray-500 leading-tight pr-2 line-clamp-2">{kpi.display_name || kpi.metric}</p>
        {pctChange !== null && pctChange !== undefined && (
          <span className={`text-xs font-semibold flex items-center gap-0.5 shrink-0 ${
            isNeutral ? 'text-gray-400' : isPos ? 'text-emerald-400' : 'text-red-400'
          }`}>
            {isNeutral ? <Minus className="w-3 h-3" /> : isPos ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
            {pct(pctChange)}
          </span>
        )}
      </div>
      <p className="text-2xl font-bold mb-0.5" style={{ color }}>
        {kpi.formatted_value || num(kpi.value)}
      </p>
      <p className="text-xs text-gray-600 mb-3">
        Σ {kpi.formatted_total || num(kpi.total)}
      </p>
      {sparkData.length > 1 && (
        <div className="h-10 -mx-1">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={sparkData}>
              <defs>
                <linearGradient id={`spk-${idx}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={color} stopOpacity={0.35} />
                  <stop offset="100%" stopColor={color} stopOpacity={0} />
                </linearGradient>
              </defs>
              <Area type="monotone" dataKey="v" stroke={color} strokeWidth={1.5}
                fill={`url(#spk-${idx})`} dot={false} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}
    </button>
  )
}

// ─────────────────────────────────────────────
// AUTO SUMMARY GENERATOR
// ─────────────────────────────────────────────
function generateAutoSummary(type: string, data: any): string {
  if (!data) return ''
  try {
    if (type === 'time_series') {
      const d = data.data || []
      const key = data.metrics?.[0]?.key
      if (!d.length || !key) return ''
      const vals = d.map((r: any) => Number(r[key] ?? 0)).filter(Boolean)
      if (!vals.length) return ''
      const max = Math.max(...vals), min = Math.min(...vals)
      const avg = vals.reduce((a: number, b: number) => a + b, 0) / vals.length
      const last = vals[vals.length - 1], prev = vals[vals.length - 2]
      const trend = last > avg ? '↑ trending above average' : '↓ below average'
      const mom = prev ? ((last - prev) / Math.abs(prev) * 100).toFixed(1) : null
      return `Latest: ${num(last)}. Peak: ${num(max)}, Low: ${num(min)}, Avg: ${num(avg)}. ${trend}${mom ? `. Period change: ${mom}%` : ''}.`
    }
    if (type === 'distribution') {
      const s = data.stats || {}
      const skew = s.skewness ?? 0
      const shape = Math.abs(skew) < 0.5
        ? 'Symmetric — values spread evenly around the mean.'
        : skew > 0
        ? 'Right-skewed — a few high outliers pull the average up.'
        : 'Left-skewed — most values concentrate near the top.'
      return `Mean ${num(s.mean)}, Median ${num(s.median)}, Std Dev ${num(s.std)}. ${shape} Outliers: ${s.outlier_pct ?? 0}%.`
    }
    if (type === 'segment') {
      const d = data.data || []
      if (!d.length) return ''
      const sorted = [...d].sort((a, b) => (b.total ?? 0) - (a.total ?? 0))
      const top = sorted[0], bot = sorted[sorted.length - 1]
      const gap = top.total && bot.total ? Math.abs(((top.total - bot.total) / (bot.total || 1)) * 100).toFixed(0) : null
      return `Best: "${top.category}" (${num(top.total)}). Lowest: "${bot.category}" (${num(bot.total)}).${gap ? ` ${gap}% gap between top and bottom.` : ''}`
    }
    if (type === 'scatter') {
      const r = data.correlation ?? 0
      const strength = Math.abs(r) > 0.7 ? 'Strong' : Math.abs(r) > 0.4 ? 'Moderate' : 'Weak'
      const dir = r > 0 ? 'positive' : 'negative'
      return `${strength} ${dir} relationship (r = ${Number(r).toFixed(2)}). ${Math.abs(r) > 0.7 ? 'These metrics move together predictably — strong leverage point.' : 'Limited predictive value between these variables.'}`
    }
    if (type === 'composition') {
      const d = data.data || []
      const sorted = [...d].sort((a: any, b: any) => (b.value ?? 0) - (a.value ?? 0))
      const top = sorted.slice(0, 2)
      const cumTop = top.reduce((s: number, x: any) => s + (x.pct ?? 0), 0)
      return `Top ${top.length} (${top.map((t: any) => `"${t.name}"`).join(', ')}) account for ${cumTop.toFixed(0)}% of total. ${sorted.length} groups.`
    }
    if (type === 'growth') {
      const p = data.periods || []
      if (!p.length) return ''
      const rates = p.map((x: any) => Number(x.growth_rate_pct ?? 0)).filter((v: number) => !isNaN(v))
      if (!rates.length) return ''
      const avg = rates.reduce((a: number, b: number) => a + b, 0) / rates.length
      const last = rates[rates.length - 1]
      const cumGrowth = p[p.length - 1]?.cumulative_growth_pct
      return `Avg growth: ${avg.toFixed(1)}%/period. Latest: ${last.toFixed(1)}%.${cumGrowth !== undefined ? ` Cumulative: ${Number(cumGrowth).toFixed(1)}%.` : ''}`
    }
  } catch { }
  return ''
}

// ─────────────────────────────────────────────
// FILTER BAR
// ─────────────────────────────────────────────
function FilterBar({ categories, selected, onChange }: { categories: string[]; selected: string; onChange: (v: string) => void }) {
  if (categories.length <= 1) return null
  return (
    <div className="flex items-center gap-2 flex-wrap mb-5">
      <Filter className="w-3.5 h-3.5 text-gray-600 shrink-0" />
      {categories.map(c => (
        <button key={c} onClick={() => onChange(c)}
          className={`filter-pill ${selected === c ? 'active' : ''}`}>
          {c}
        </button>
      ))}
    </div>
  )
}

// ─────────────────────────────────────────────
// CHART TYPE TABS
// ─────────────────────────────────────────────
type ChartTab = 'area' | 'bar' | 'line'
function ChartTypeTabs({ value, onChange }: { value: ChartTab; onChange: (v: ChartTab) => void }) {
  const TABS: { key: ChartTab; icon: any }[] = [
    { key: 'area', icon: Activity },
    { key: 'bar',  icon: BarChart3 },
    { key: 'line', icon: TrendingUp },
  ]
  return (
    <div className="flex items-center gap-0.5 rounded-lg p-1" style={{ background:'rgba(212,175,55,0.06)' }}>
      {TABS.map(t => (
        <button key={t.key} onClick={() => onChange(t.key)}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs transition-all ${
            value === t.key ? 'bg-[#D4AF37]/20 text-[#D4AF37] border border-[#D4AF37]/30' : 'text-gray-400 hover:text-white'
          }`}>
          <t.icon className="w-3 h-3" /> {t.key}
        </button>
      ))}
    </div>
  )
}

// ─────────────────────────────────────────────
// EMPTY STATE
// ─────────────────────────────────────────────
function EmptyChart({ label }: { label: string }) {
  return (
    <div className="h-full flex flex-col items-center justify-center text-gray-600 gap-2 py-8">
      <BarChart2 className="w-8 h-8 opacity-20" />
      <span className="text-xs">{label}</span>
    </div>
  )
}

// ─────────────────────────────────────────────
// AI SUMMARY PILL
// ─────────────────────────────────────────────
function AISummary({ text }: { text: string }) {
  if (!text) return null
  return (
    <div className="mt-4 p-3.5 rounded-xl flex gap-2.5" style={{ background:'rgba(212,175,55,0.05)', border:'1px solid rgba(212,175,55,0.1)' }}>
      <Sparkles className="w-3.5 h-3.5 text-[#D4AF37] mt-0.5 shrink-0" />
      <p className="text-xs text-gray-400 leading-relaxed">{text}</p>
    </div>
  )
}

// ─────────────────────────────────────────────
// BOX PLOT (custom SVG)
// ─────────────────────────────────────────────
function BoxPlotChart({ distributions }: { distributions: any[] }) {
  if (!distributions?.length) return <EmptyChart label="No distribution data" />
  const items = distributions.slice(0, 8).filter(d => d.stats)

  return (
    <div className="space-y-3">
      {items.map((d, i) => {
        const s = d.stats
        const range = (s.max ?? 0) - (s.min ?? 0)
        if (!range) return null
        const toX = (v: number) => ((v - s.min) / range) * 100

        return (
          <div key={i} className="group">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-gray-400 truncate max-w-[200px]">{d.display_name}</span>
              <span className="text-xs text-gray-600 font-mono">{num(s.mean)} avg</span>
            </div>
            <div className="relative h-7 flex items-center">
              {/* Track */}
              <div className="absolute inset-0 flex items-center">
                <div className="w-full h-px rounded" style={{ background:'rgba(212,175,55,0.08)' }} />
              </div>
              {/* Min-Max whisker */}
              <div className="absolute h-3 border-l border-r border-gray-600"
                style={{ left: `${toX(s.min)}%`, right: `${100 - toX(s.max)}%` }} />
              {/* IQR box */}
              <div className="absolute h-4 rounded-sm opacity-70"
                style={{
                  left: `${toX(s.q1 ?? s.mean - s.std)}%`,
                  right: `${100 - toX(s.q3 ?? s.mean + s.std)}%`,
                  background: `${COLOR_SEQ[i % COLOR_SEQ.length]}40`,
                  border: `1px solid ${COLOR_SEQ[i % COLOR_SEQ.length]}60`,
                }} />
              {/* Median line */}
              <div className="absolute w-0.5 h-5 rounded"
                style={{ left: `${toX(s.median ?? s.mean)}%`, background: COLOR_SEQ[i % COLOR_SEQ.length] }} />
              {/* Mean dot */}
              <div className="absolute w-2 h-2 rounded-full"
                style={{ left: `calc(${toX(s.mean)}% - 4px)`, background: PALETTE.coral }} />
            </div>
            {/* Outlier indicator */}
            {(s.outlier_pct ?? 0) > 0 && (
              <div className="flex items-center gap-1 mt-0.5">
                <span className="text-[10px] text-orange-400/60">{s.outlier_pct}% outliers</span>
              </div>
            )}
          </div>
        )
      })}
      <div className="flex items-center gap-4 mt-3 text-[10px] text-gray-600 pt-3" style={{ borderTop:'1px solid rgba(212,175,55,0.06)' }}>
        <span className="flex items-center gap-1"><span className="w-3 h-0.5 inline-block bg-gray-500" /> Min/Max</span>
        <span className="flex items-center gap-1"><span className="w-3 h-3 inline-block rounded-sm bg-[#D4AF37]/30 border border-[#D4AF37]/50" /> IQR (25–75%)</span>
        <span className="flex items-center gap-1"><span className="w-0.5 h-3 inline-block bg-[#D4AF37]" /> Median</span>
        <span className="flex items-center gap-1"><span className="w-2 h-2 inline-block rounded-full bg-[#FF6B6B]" /> Mean</span>
      </div>
    </div>
  )
}

// ─────────────────────────────────────────────
// PERCENTILE CHART
// ─────────────────────────────────────────────
function PercentileChart({ dist }: { dist: any }) {
  if (!dist?.percentile_data) return <EmptyChart label="No percentile data" />
  const data = dist.percentile_data.map((p: any) => ({ label: p.label, value: p.value ?? 0 }))

  return (
    <div className="h-[180px]">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 10, right: 5, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#ffffff0a" vertical={false} />
          <XAxis dataKey="label" stroke="#555" tick={{ fontSize: 10, fill: '#888' }} />
          <YAxis stroke="#555" tick={{ fontSize: 9, fill: '#666' }} tickFormatter={(v) => num(v, 0)} />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="value" radius={[4, 4, 0, 0]} maxBarSize={40}>
            {data.map((_: any, i: number) => (
              <Cell key={i} fill={`${PALETTE.purple}${(40 + i * 30).toString(16).padStart(2, '0')}`} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

// ─────────────────────────────────────────────
// TOP vs BOTTOM comparison
// ─────────────────────────────────────────────
function TopBottomChart({ seg }: { seg: any }) {
  if (!seg?.data?.length) return <EmptyChart label="No segment data" />
  const sorted = [...seg.data].sort((a, b) => (b.total ?? 0) - (a.total ?? 0))
  const top5 = sorted.slice(0, 5)
  const bot5 = sorted.slice(-5).reverse()
  const combined = [
    ...top5.map((d: any) => ({ ...d, group: 'Top', fill: PALETTE.emerald })),
    ...bot5.map((d: any) => ({ ...d, group: 'Bottom', fill: PALETTE.coral })),
  ]

  return (
    <div className="h-[240px]">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={combined} layout="vertical" margin={{ left: 80 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#ffffff0a" horizontal={false} />
          <XAxis type="number" stroke="#555" tick={{ fontSize: 9, fill: '#888' }} tickFormatter={(v) => num(v, 0)} />
          <YAxis type="category" dataKey="category" stroke="#555" tick={{ fontSize: 9, fill: '#ccc' }} width={75} />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="total" radius={[0, 4, 4, 0]} maxBarSize={18}>
            {combined.map((d: any, i: number) => (
              <Cell key={i} fill={d.fill} opacity={0.75} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

// ─────────────────────────────────────────────
// MAIN COMPONENT
// ─────────────────────────────────────────────
export function AnalyticsDashboard({ analytics }: Props) {
  const [selectedKpi,  setSelectedKpi]  = useState(0)
  const [tsChartType,  setTsChartType]  = useState<ChartTab>('area')
  const [segFilter,    setSegFilter]    = useState('All')
  const [distIdx,      setDistIdx]      = useState(0)
  const [compIdx,      setCompIdx]      = useState(0)
  const [scatterIdx,   setScatterIdx]   = useState(0)
  const [growthIdx,    setGrowthIdx]    = useState(0)
  const [showAllCorr,  setShowAllCorr]  = useState(false)

  if (!analytics) {
    return (
      <div className="py-16 text-center text-gray-500 flex flex-col items-center gap-3">
        <Activity className="w-10 h-10 opacity-20" />
        <p>Analytics data not available yet.</p>
      </div>
    )
  }

  const kpis        = analytics.kpis         || []
  const timeSeries  = analytics.time_series  || []
  const dists       = analytics.distributions|| []
  const segments    = analytics.segments     || []
  const corr        = analytics.correlation_matrix || {}
  const pctChanges  = analytics.percentage_changes || []
  const composition = analytics.composition  || []
  const scatter     = analytics.scatter      || []
  const growth      = analytics.growth_rates || []
  const meta        = analytics.meta         || {}

  // Derived
  const ts        = timeSeries[0]
  const tsData    = ts?.data    || []
  const tsMetrics = ts?.metrics || []

  const seg = segments[0]
  const segCategories = useMemo(() => {
    if (!seg?.data) return ['All']
    const cats = [...new Set(seg.data.map((d: any) => d.category))] as string[]
    return ['All', ...cats]
  }, [seg])
  const segData = useMemo(() => {
    if (!seg?.data) return []
    const base = segFilter === 'All' ? seg.data : seg.data.filter((d: any) => d.category === segFilter)
    return base.slice(0, 15)
  }, [seg, segFilter])

  const dist      = dists[distIdx]
  const comp      = composition[compIdx]
  const compData  = comp?.data || []
  const sc        = scatter[scatterIdx]
  const scData    = sc?.data  || []
  const gr        = growth[growthIdx]
  const grData    = gr?.periods || []

  const corrCells = corr?.cells || []
  const corrBarData = corrCells
    .filter((c: any) => c.x !== c.y)
    .slice(0, showAllCorr ? 24 : 10)
    .map((c: any) => ({ pair: `${c.x} ↔ ${c.y}`, value: c.value, abs: Math.abs(c.value) }))

  const vsAvg     = pctChanges.find((x: any) => x.type === 'vs_average')
  const vsAvgData = (vsAvg?.data || []).slice(0, 14)

  // Summaries
  const tsSummary   = generateAutoSummary('time_series', ts)
  const distSummary = generateAutoSummary('distribution', dist)
  const segSummary  = generateAutoSummary('segment', seg)
  const scSummary   = generateAutoSummary('scatter', sc)
  const compSummary = generateAutoSummary('composition', comp)
  const grSummary   = generateAutoSummary('growth', gr)

  return (
    <div className="space-y-5">

      {/* ── 1. KPI OVERVIEW ── */}
      <Section title="Executive KPI Overview" subtitle="Click any card to highlight its trend"
        icon={Target} iconColor={PALETTE.gold} badge={`${kpis.length} metrics`}>
        <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-3">
          {kpis.slice(0, 8).map((kpi: any, idx: number) => (
            <KpiCard key={idx} kpi={kpi} idx={idx}
              selected={selectedKpi === idx} onClick={() => setSelectedKpi(idx)} />
          ))}
        </div>
      </Section>

      {/* ── 2. TIME SERIES + COMPOSITION ── */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-5">
        <div className="xl:col-span-2">
          <Section title={ts?.display_name || 'Trend Analysis'}
            subtitle={tsSummary || `${ts?.period || ''} data`}
            icon={TrendingUp} iconColor={PALETTE.teal}
            headerRight={<ChartTypeTabs value={tsChartType} onChange={setTsChartType} />}>
            <div className="h-[300px]">
              {tsData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  {tsChartType === 'area' ? (
                    <AreaChart data={tsData}>
                      <defs>
                        {tsMetrics.map((_m: any, i: number) => (
                          <linearGradient key={i} id={`tg-${i}`} x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%"   stopColor={COLOR_SEQ[i]} stopOpacity={0.5} />
                            <stop offset="100%" stopColor={COLOR_SEQ[i]} stopOpacity={0.02} />
                          </linearGradient>
                        ))}
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#ffffff0a" />
                      <XAxis dataKey="period" stroke="#555" tick={{ fontSize: 10, fill: '#888' }} />
                      <YAxis stroke="#555" tick={{ fontSize: 10, fill: '#888' }} tickFormatter={v => num(v, 0)} />
                      <Tooltip content={<CustomTooltip />} />
                      <Legend wrapperStyle={{ fontSize: 11, color: '#888' }} />
                      <Brush dataKey="period" height={18} stroke="#ffffff10" fill="#0f0f1a" travellerWidth={5} />
                      {tsMetrics.map((m: any, i: number) => (
                        <Area key={i} type="monotone" dataKey={m.key} name={m.display_name}
                          stroke={COLOR_SEQ[i]} strokeWidth={2} fill={`url(#tg-${i})`}
                          dot={false} activeDot={{ r: 4 }} />
                      ))}
                    </AreaChart>
                  ) : tsChartType === 'bar' ? (
                    <ComposedChart data={tsData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#ffffff0a" />
                      <XAxis dataKey="period" stroke="#555" tick={{ fontSize: 10, fill: '#888' }} />
                      <YAxis stroke="#555" tick={{ fontSize: 10, fill: '#888' }} tickFormatter={v => num(v, 0)} />
                      <Tooltip content={<CustomTooltip />} />
                      <Legend wrapperStyle={{ fontSize: 11, color: '#888' }} />
                      {tsMetrics.map((m: any, i: number) => (
                        <Bar key={i} dataKey={m.key} name={m.display_name}
                          fill={COLOR_SEQ[i]} radius={[3, 3, 0, 0]} maxBarSize={40} />
                      ))}
                    </ComposedChart>
                  ) : (
                    <LineChart data={tsData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#ffffff0a" />
                      <XAxis dataKey="period" stroke="#555" tick={{ fontSize: 10, fill: '#888' }} />
                      <YAxis stroke="#555" tick={{ fontSize: 10, fill: '#888' }} tickFormatter={v => num(v, 0)} />
                      <Tooltip content={<CustomTooltip />} />
                      <Legend wrapperStyle={{ fontSize: 11, color: '#888' }} />
                      {tsMetrics.map((m: any, i: number) => (
                        <Line key={i} type="monotone" dataKey={m.key} name={m.display_name}
                          stroke={COLOR_SEQ[i]} strokeWidth={2.5}
                          dot={{ r: 3, fill: COLOR_SEQ[i] }} activeDot={{ r: 5 }} />
                      ))}
                    </LineChart>
                  )}
                </ResponsiveContainer>
              ) : <EmptyChart label="No time-series data available" />}
            </div>
            {tsSummary && <AISummary text={tsSummary} />}
          </Section>
        </div>

        {/* Composition */}
        <Section title={comp?.display_name || 'Composition'}
          subtitle={compSummary} icon={PieIcon} iconColor={PALETTE.amber}>
          {composition.length > 1 && (
            <div className="flex gap-1 mb-3 flex-wrap">
              {composition.slice(0, 4).map((c: any, i: number) => (
                <button key={i} onClick={() => setCompIdx(i)}
                  className={`text-xs px-2 py-1 rounded-md transition-all ${
                    compIdx === i ? 'text-[#F39C12]' : 'text-gray-500 hover:text-white'
                  }`}
                  style={ compIdx === i ? { background:'rgba(243,156,18,0.12)', border:'1px solid rgba(243,156,18,0.3)' } : { background:'rgba(255,255,255,0.03)', border:'1px solid rgba(255,255,255,0.05)' } }>
                  {c.display_name?.split(' ')[0] || `Set ${i+1}`}
                </button>
              ))}
            </div>
          )}
          <div className="h-[200px]">
            {compData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={compData} dataKey="value" nameKey="name"
                    outerRadius={80} innerRadius={42} paddingAngle={2}
                    startAngle={90} endAngle={-270}>
                    {compData.map((_: any, i: number) => (
                      <Cell key={i} fill={COLOR_SEQ[i % COLOR_SEQ.length]}
                        stroke="rgba(0,0,0,0.2)" strokeWidth={1} />
                    ))}
                  </Pie>
                  <Tooltip content={<CustomTooltip />} />
                </PieChart>
              </ResponsiveContainer>
            ) : <EmptyChart label="No composition data" />}
          </div>
          <div className="mt-2 space-y-1.5">
            {compData.slice(0, 6).map((d: any, i: number) => (
              <div key={i} className="flex items-center justify-between text-xs">
                <span className="flex items-center gap-1.5 text-gray-400 truncate pr-2">
                  <span className="w-2 h-2 rounded-full shrink-0" style={{ background: COLOR_SEQ[i % COLOR_SEQ.length] }} />
                  {d.name}
                </span>
                <span className="text-gray-300 font-medium shrink-0">{pct(d.pct)}</span>
              </div>
            ))}
          </div>
          {compSummary && <AISummary text={compSummary} />}
        </Section>
      </div>

      {/* ── 3. SEGMENT PERFORMANCE ── */}
      <Section title={`Segment Performance · ${seg?.display_dimension || 'By Category'}`}
        subtitle={segSummary} icon={BarChart3} iconColor={PALETTE.emerald}
        badge={`${segData.length} segments`}>
        <FilterBar categories={segCategories} selected={segFilter} onChange={setSegFilter} />
        <div className="h-[280px]">
          {segData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={segData} layout="vertical" margin={{ left: 100 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff0a" horizontal={false} />
                <XAxis type="number" stroke="#555" tick={{ fontSize: 9, fill: '#888' }} tickFormatter={v => num(v, 0)} />
                <YAxis type="category" dataKey="category" stroke="#555" tick={{ fontSize: 9, fill: '#ccc' }} width={95} />
                <Tooltip content={<CustomTooltip />} />
                <ReferenceLine x={seg?.overall_mean} stroke={`${PALETTE.amber}80`}
                  strokeDasharray="4 2"
                  label={{ value: 'Avg', position: 'top', fill: PALETTE.amber, fontSize: 9 }} />
                <Bar dataKey="total" radius={[0, 4, 4, 0]} maxBarSize={20}>
                  {segData.map((d: any, j: number) => (
                    <Cell key={j}
                      fill={d.direction === 'above' ? PALETTE.emerald : PALETTE.coral}
                      opacity={0.7} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : <EmptyChart label="No segment data" />}
        </div>
        {segSummary && <AISummary text={segSummary} />}
      </Section>

      {/* ── 4. DISTRIBUTION + SCATTER ── */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">

        {/* Distribution */}
        <Section title={`Distribution · ${dist?.display_name || '–'}`}
          subtitle={distSummary} icon={Activity} iconColor={PALETTE.purple}>
          {dists.length > 1 && (
            <div className="flex gap-1 mb-3 flex-wrap">
              {dists.slice(0, 5).map((d: any, i: number) => (
                <button key={i} onClick={() => setDistIdx(i)}
                  className={`text-xs px-2 py-1 rounded-md transition-all ${
                    distIdx === i ? 'text-[#9B59B6]' : 'text-gray-500 hover:text-white'
                  }`}
                  style={ distIdx === i ? { background:'rgba(155,89,182,0.12)', border:'1px solid rgba(155,89,182,0.3)' } : { background:'rgba(255,255,255,0.03)', border:'1px solid rgba(255,255,255,0.05)' } }>
                  {d.display_name?.split(' ')[0] || `D${i+1}`}
                </button>
              ))}
            </div>
          )}
          <div className="h-[220px]">
            {dist?.histogram?.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={dist.histogram} margin={{ left: 0, right: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ffffff0a" vertical={false} />
                  <XAxis dataKey="label" stroke="#555" tick={{ fontSize: 9, fill: '#666' }} interval="preserveStartEnd" />
                  <YAxis stroke="#555" tick={{ fontSize: 9, fill: '#666' }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="count" radius={[3, 3, 0, 0]}>
                    {dist.histogram.map((_: any, i: number) => (
                      <Cell key={i}
                        fill={`${PALETTE.purple}${Math.round(30 + (i / dist.histogram.length) * 200).toString(16).padStart(2,'0')}`} />
                    ))}
                  </Bar>
                  {dist.stats?.mean !== undefined && (
                    <ReferenceLine x={dist.stats.mean} stroke={PALETTE.coral} strokeDasharray="4 2"
                      label={{ value: 'Avg', position: 'top', fill: PALETTE.coral, fontSize: 9 }} />
                  )}
                </BarChart>
              </ResponsiveContainer>
            ) : <EmptyChart label="No histogram data" />}
          </div>
          {dist?.stats && (
            <div className="grid grid-cols-4 gap-2 mt-3">
              {[
                { l: 'Mean',    v: dist.stats.mean },
                { l: 'Median',  v: dist.stats.median },
                { l: 'Std Dev', v: dist.stats.std },
                { l: 'Outliers',v: dist.stats.outlier_pct, s: '%' },
              ].map(s => (
                <div key={s.l} className="rounded-lg p-2 text-center" style={{ background:'rgba(212,175,55,0.05)', border:'1px solid rgba(212,175,55,0.08)' }}>
                  <div className="text-[10px] text-gray-500">{s.l}</div>
                  <div className="text-sm font-bold text-[#D4AF37] mt-0.5">{num(s.v)}{s.s || ''}</div>
                </div>
              ))}
            </div>
          )}
          {distSummary && <AISummary text={distSummary} />}
        </Section>

        {/* Scatter */}
        <Section title={sc ? `${sc.display_x} vs ${sc.display_y}` : 'Relationship Analysis'}
          subtitle={scSummary} icon={GitBranch} iconColor={PALETTE.gold}>
          {scatter.length > 1 && (
            <div className="flex gap-1 mb-3 flex-wrap">
              {scatter.slice(0, 4).map((s: any, i: number) => (
                <button key={i} onClick={() => setScatterIdx(i)}
                  className={`text-xs px-2 py-1 rounded-md transition-all ${
                    scatterIdx === i ? 'text-[#D4AF37]' : 'text-gray-500 hover:text-white'
                  }`}
                  style={ scatterIdx === i ? { background:'rgba(212,175,55,0.12)', border:'1px solid rgba(212,175,55,0.3)' } : { background:'rgba(255,255,255,0.03)', border:'1px solid rgba(255,255,255,0.05)' } }>
                  {s.display_x?.split(' ')[0]}×{s.display_y?.split(' ')[0]}
                </button>
              ))}
            </div>
          )}
          <div className="h-[220px]">
            {scData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 5, right: 5, left: 0, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ffffff0a" />
                  <XAxis type="number" dataKey="x" name={sc?.display_x} stroke="#555"
                    tick={{ fontSize: 9, fill: '#888' }} tickFormatter={v => num(v, 0)}
                    label={{ value: sc?.display_x || 'X', position: 'insideBottom', offset: -8, fill: '#666', fontSize: 9 }} />
                  <YAxis type="number" dataKey="y" name={sc?.display_y} stroke="#555"
                    tick={{ fontSize: 9, fill: '#888' }} tickFormatter={v => num(v, 0)}
                    label={{ value: sc?.display_y || 'Y', angle: -90, position: 'insideLeft', fill: '#666', fontSize: 9 }} />
                  <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: '3 3', stroke: '#ffffff15' }} />
                  <Scatter data={scData} fill={PALETTE.gold} opacity={0.7} />
                </ScatterChart>
              </ResponsiveContainer>
            ) : <EmptyChart label="Need 2+ numeric columns for scatter" />}
          </div>
          {sc && (
            <div className="flex items-center gap-2 mt-3 flex-wrap">
              {[
                { l: 'Correlation',  v: `r = ${Number(sc.correlation).toFixed(3)}`, c: Math.abs(sc.correlation) > 0.7 ? PALETTE.emerald : PALETTE.amber },
                { l: 'Strength',     v: Math.abs(sc.correlation) > 0.7 ? 'Strong' : Math.abs(sc.correlation) > 0.4 ? 'Moderate' : 'Weak', c: '#ccc' },
                { l: 'Direction',    v: sc.correlation > 0 ? 'Positive ↑' : 'Negative ↓', c: sc.correlation > 0 ? PALETTE.emerald : PALETTE.coral },
              ].map(s => (
                <div key={s.l} className="rounded-lg px-3 py-1.5 text-xs" style={{ background:'rgba(212,175,55,0.05)', border:'1px solid rgba(212,175,55,0.08)' }}>
                  <span className="text-gray-500">{s.l}: </span>
                  <span className="font-semibold" style={{ color: s.c }}>{s.v}</span>
                </div>
              ))}
            </div>
          )}
          {scSummary && <AISummary text={scSummary} />}
        </Section>
      </div>

      {/* ── 5. BOX PLOTS + PERCENTILE ── */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
        <Section title="Value Spread (Box Plot View)"
          subtitle="IQR box, whiskers, median line, and mean dot per metric"
          icon={Hash} iconColor={PALETTE.purple}>
          <BoxPlotChart distributions={dists} />
        </Section>

        <Section title={`Percentile Breakdown · ${dist?.display_name || '–'}`}
          subtitle="How values distribute across P5 → P95"
          icon={Award} iconColor={PALETTE.blue}>
          <PercentileChart dist={dist} />
          {dist?.stats && (
            <div className="mt-3 grid grid-cols-2 gap-2">
              <div className="rounded-lg p-2.5" style={{ background:'rgba(212,175,55,0.04)', border:'1px solid rgba(212,175,55,0.07)' }}>
                <div className="text-xs text-gray-500 mb-1">Skewness</div>
                <div className={`text-sm font-bold ${Math.abs(dist.stats.skewness ?? 0) < 0.5 ? 'text-emerald-400' : 'text-orange-400'}`}>
                  {num(dist.stats.skewness)}
                  <span className="text-xs text-gray-600 ml-1 font-normal">
                    {Math.abs(dist.stats.skewness ?? 0) < 0.5 ? '(symmetric)' : (dist.stats.skewness ?? 0) > 0 ? '(right-skewed)' : '(left-skewed)'}
                  </span>
                </div>
              </div>
              <div className="rounded-lg p-2.5" style={{ background:'rgba(212,175,55,0.04)', border:'1px solid rgba(212,175,55,0.07)' }}>
                <div className="text-xs text-gray-500 mb-1">Kurtosis</div>
                <div className={`text-sm font-bold ${Math.abs((dist.stats.kurtosis ?? 0) - 3) < 1 ? 'text-emerald-400' : 'text-orange-400'}`}>
                  {num(dist.stats.kurtosis)}
                  <span className="text-xs text-gray-600 ml-1 font-normal">
                    {(dist.stats.kurtosis ?? 0) > 3 ? '(heavy tails)' : '(light tails)'}
                  </span>
                </div>
              </div>
            </div>
          )}
        </Section>
      </div>

      {/* ── 6. CORRELATION PAIRS ── */}
      <Section title="Metric Correlations" subtitle="Pairs with strongest relationships"
        icon={Layers} iconColor={PALETTE.teal}
        badge={`${corrCells.filter((c: any) => c.x !== c.y).length} pairs`}>
        {corrBarData.length > 0 ? (
          <>
            <div className="h-[240px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={corrBarData} layout="vertical" margin={{ left: 140 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ffffff0a" horizontal={false} />
                  <XAxis type="number" domain={[-1, 1]} stroke="#555" tick={{ fontSize: 9, fill: '#888' }} />
                  <YAxis type="category" dataKey="pair" stroke="#555" tick={{ fontSize: 8, fill: '#bbb' }} width={135} />
                  <Tooltip content={<CustomTooltip />} />
                  <ReferenceLine x={0} stroke="#ffffff15" />
                  <ReferenceLine x={0.7}  stroke={`${PALETTE.emerald}35`} strokeDasharray="3 2" />
                  <ReferenceLine x={-0.7} stroke={`${PALETTE.coral}35`}   strokeDasharray="3 2" />
                  <Bar dataKey="value" radius={[0, 3, 3, 0]} maxBarSize={14}>
                    {corrBarData.map((d: any, i: number) => (
                      <Cell key={i} fill={d.value >= 0 ? PALETTE.teal : PALETTE.coral}
                        opacity={0.5 + d.abs * 0.5} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="flex items-center justify-between mt-2">
              <div className="flex items-center gap-4 text-[10px] text-gray-600">
                <span className="flex items-center gap-1"><span className="w-3 h-2 rounded inline-block" style={{ background: PALETTE.teal }} /> Positive</span>
                <span className="flex items-center gap-1"><span className="w-3 h-2 rounded inline-block" style={{ background: PALETTE.coral }} /> Negative</span>
                <span>| Dashed = ±0.7 strong threshold</span>
              </div>
              {corrCells.length > 10 && (
                <button onClick={() => setShowAllCorr(!showAllCorr)}
                  className="text-xs text-[#D4AF37] hover:underline flex items-center gap-1">
                  {showAllCorr ? 'Show less' : 'Show all'}
                  <ChevronDown className={`w-3 h-3 transition-transform ${showAllCorr ? 'rotate-180' : ''}`} />
                </button>
              )}
            </div>
          </>
        ) : <EmptyChart label="No correlation data" />}
      </Section>

      {/* ── 7. % CHANGE + GROWTH ── */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
        <Section title="Performance vs Average" subtitle="Segments above 0% outperform the mean"
          icon={Zap} iconColor={PALETTE.emerald}>
          <div className="h-[260px]">
            {vsAvgData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={vsAvgData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ffffff0a" vertical={false} />
                  <XAxis dataKey="category" stroke="#555"
                    tick={({ x, y, payload }: any) => (
                      <text x={x} y={y + 6} textAnchor="end" fontSize={8} fill="#888"
                        transform={`rotate(-25, ${x}, ${y})`}>
                        {payload.value}
                      </text>
                    )} height={45} />
                  <YAxis stroke="#555" tick={{ fontSize: 9, fill: '#888' }} tickFormatter={v => `${v}%`} />
                  <Tooltip content={<CustomTooltip />} />
                  <ReferenceLine y={0} stroke="#ffffff20" />
                  <Bar dataKey="pct_vs_average" name="vs Avg %" radius={[3, 3, 0, 0]} maxBarSize={32}>
                    {vsAvgData.map((d: any, i: number) => (
                      <Cell key={i} fill={(d.pct_vs_average ?? 0) >= 0 ? PALETTE.emerald : PALETTE.coral} opacity={0.75} />
                    ))}
                    <LabelList dataKey="pct_vs_average" position="top"
                      formatter={(v: number) => v !== null ? `${Number(v).toFixed(0)}%` : ''}
                      style={{ fontSize: 8, fill: '#888' }} />
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : <EmptyChart label="No vs-average data" />}
          </div>
          <AISummary text="Green = above average. Red = below. Use this to spot underperforming segments needing attention." />
        </Section>

        <Section title={`Growth Trend · ${gr?.display_name || '–'}`}
          subtitle={grSummary} icon={Clock} iconColor={PALETTE.blue}>
          {growth.length > 1 && (
            <div className="flex gap-1 mb-3 flex-wrap">
              {growth.slice(0, 4).map((g: any, i: number) => (
                <button key={i} onClick={() => setGrowthIdx(i)}
                  className={`text-xs px-2 py-1 rounded-md transition-all ${
                    growthIdx === i ? 'text-[#3498DB]' : 'text-gray-500 hover:text-white'
                  }`}
                  style={ growthIdx === i ? { background:'rgba(52,152,219,0.12)', border:'1px solid rgba(52,152,219,0.3)' } : { background:'rgba(255,255,255,0.03)', border:'1px solid rgba(255,255,255,0.05)' } }>
                  {g.display_name?.split(' ')[0] || `M${i+1}`}
                </button>
              ))}
            </div>
          )}
          <div className="h-[230px]">
            {grData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={grData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ffffff0a" />
                  <XAxis dataKey="period" stroke="#555" tick={{ fontSize: 9, fill: '#888' }} />
                  <YAxis yAxisId="l" stroke="#555" tick={{ fontSize: 9, fill: '#888' }} tickFormatter={v => num(v, 0)} />
                  <YAxis yAxisId="r" orientation="right" stroke="#555" tick={{ fontSize: 9, fill: '#888' }} tickFormatter={v => `${v}%`} />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend wrapperStyle={{ fontSize: 10, color: '#888' }} />
                  <Bar yAxisId="l" dataKey="value" name="Value" fill={`${PALETTE.blue}35`}
                    radius={[3, 3, 0, 0]} maxBarSize={28} />
                  <Line yAxisId="r" type="monotone" dataKey="growth_rate_pct" name="Growth %"
                    stroke={PALETTE.gold} strokeWidth={2.5} dot={{ r: 3, fill: PALETTE.gold }} activeDot={{ r: 5 }} />
                  <Line yAxisId="r" type="monotone" dataKey="cumulative_growth_pct" name="Cumulative %"
                    stroke={PALETTE.coral} strokeWidth={1.5} dot={false} strokeDasharray="4 2" />
                  <ReferenceLine yAxisId="r" y={0} stroke="#ffffff15" />
                </ComposedChart>
              </ResponsiveContainer>
            ) : <EmptyChart label="No growth data" />}
          </div>
          {grSummary && <AISummary text={grSummary} />}
        </Section>
      </div>

      {/* ── 8. TOP vs BOTTOM ── */}
      {seg?.data?.length >= 4 && (
        <Section title={`Top vs Bottom · ${seg.display_dimension || 'Segments'}`}
          subtitle="Best and worst performers side-by-side"
          icon={Award} iconColor={PALETTE.gold}>
          <TopBottomChart seg={seg} />
          <AISummary text={`Green bars = top 5 performers. Red bars = bottom 5. Focus resources on bottom performers or replicate top-performer strategies.`} />
        </Section>
      )}

      {/* ── 9. RADAR (multi-metric) ── */}
      {seg?.data?.length >= 3 && (
        <Section title="Multi-Metric Segment Radar"
          subtitle="Holistic view of each segment across all available metrics"
          icon={Eye} iconColor={PALETTE.pink}>
          <div className="h-[280px]">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={seg.data.slice(0, 8).map((d: any) => ({
                subject: (d.category || '').slice(0, 14),
                total: d.total ?? 0,
                avg: d.mean ?? 0,
              }))}>
                <PolarGrid stroke="#ffffff0f" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: '#777', fontSize: 9 }} />
                <PolarRadiusAxis tick={{ fill: '#555', fontSize: 7 }} />
                <Radar name="Total" dataKey="total" stroke={PALETTE.gold}
                  fill={PALETTE.gold} fillOpacity={0.12} strokeWidth={2} />
                <Radar name="Avg" dataKey="avg" stroke={PALETTE.teal}
                  fill={PALETTE.teal} fillOpacity={0.08} strokeWidth={1.5} />
                <Legend wrapperStyle={{ fontSize: 10, color: '#888' }} />
                <Tooltip content={<CustomTooltip />} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
          <AISummary text="Larger filled area = stronger performance. Compare segments visually across all metrics simultaneously." />
        </Section>
      )}

      {/* ── 10. DATASET META ── */}
      <Section title="Dataset Intelligence" subtitle="Profile & quality metadata"
        icon={Info} iconColor={PALETTE.amber}>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          {[
            { label: 'Total Rows',    value: num(meta.total_rows) },
            { label: 'Columns',       value: num(meta.total_cols) },
            { label: 'Numeric',       value: meta.numeric_cols?.length ?? '–' },
            { label: 'Categorical',   value: meta.categorical_cols?.length ?? '–' },
            { label: 'Time-aware',    value: meta.has_datetime ? 'Yes ✓' : 'No' },
            { label: 'Domain',        value: meta.domain || '–' },
          ].map(s => (
            <div key={s.label} className="rounded-xl p-3 text-center" style={{ background:'rgba(212,175,55,0.04)', border:'1px solid rgba(212,175,55,0.08)' }}>
              <div className="text-[10px] text-gray-500 mb-1">{s.label}</div>
              <div className="font-bold text-white text-sm">{s.value}</div>
            </div>
          ))}
        </div>
      </Section>

    </div>
  )
}

export default AnalyticsDashboard
