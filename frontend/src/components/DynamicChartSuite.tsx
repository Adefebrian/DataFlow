/* eslint-disable */
// @ts-nocheck
/**
 * DynamicChartSuite — Legacy component (not used in main flow)
 */
import { useState, useMemo } from 'react'
import {
  ResponsiveContainer,
  BarChart, Bar,
  LineChart, Line,
  AreaChart, Area,
  PieChart, Pie, Cell,
  ComposedChart,
  CartesianGrid, XAxis, YAxis, Tooltip, Legend,
  ReferenceLine, LabelList,
} from 'recharts'
import {
  BarChart3, TrendingUp, TrendingDown, PieChart as PieIcon, GitBranch,
  Layers, Award, SlidersHorizontal, ChevronDown, Sparkles,
  BarChart2, ArrowLeftRight, Target,
  ArrowUpRight, ArrowDownRight, Minus,
} from 'lucide-react'

// ─── Design System ────────────────────────────────────────────────────────────
const C = {
  gold:    '#D4AF37',
  teal:    '#00CED1',
  coral:   '#FF6B6B',
  purple:  '#9B59B6',
  emerald: '#2ECC71',
  amber:   '#F39C12',
  blue:    '#3498DB',
  pink:    '#E91E63',
  gray:    '#64748B',
}
const SEQ = [C.gold, C.teal, C.emerald, C.purple, C.amber, C.blue, C.coral, C.pink]

const GRID_STROKE  = 'rgba(212,175,55,0.07)'
const AXIS_STROKE  = '#444'
const AXIS_TICK    = { fontSize: 10, fill: '#777' }
const AXIS_TICK_SM = { fontSize: 9, fill: '#666' }

// ─── Smart formatter ──────────────────────────────────────────────────────────
function fmt(v: any, compact = true): string {
  if (v === null || v === undefined || Number.isNaN(Number(v))) return '–'
  const n = Number(v)
  const a = Math.abs(n)
  const s = n < 0 ? '-' : ''
  if (!compact) return n.toLocaleString(undefined, { maximumFractionDigits: 2 })
  if (a >= 1e9) return `${s}${(a / 1e9).toFixed(1)}B`
  if (a >= 1e6) return `${s}${(a / 1e6).toFixed(1)}M`
  if (a >= 1e3) return `${s}${(a / 1e3).toFixed(1)}K`
  return n.toLocaleString(undefined, { maximumFractionDigits: 1 })
}

function fmtPct(v: any): string {
  const n = Number(v)
  return isNaN(n) ? '–' : `${n > 0 ? '+' : ''}${n.toFixed(1)}%`
}

function dname(col: string): string {
  return col.replace(/_/g, ' ').replace(/-/g, ' ')
    .split(' ').map((w: string) => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
}

// Describe what a value means in plain English
function describe(value: number, mean: number, std: number): string {
  if (std === 0) return 'typical value'
  const z = (value - mean) / std
  if (z > 2)  return '🔥 exceptional — top 2%'
  if (z > 1)  return '✅ above average'
  if (z > -1) return '➡️ typical range'
  if (z > -2) return '⚠️ below average'
  return '🔴 very low'
}

// ─── Rich Tooltip ─────────────────────────────────────────────────────────────
function RichTip({
  active, payload, label, mean, unit = '', extraLine,
}: any) {
  if (!active || !payload?.length) return null
  return (
    <div className="rounded-2xl p-4 shadow-2xl text-sm max-w-[260px]"
      style={{ background: '#0e0e1a', border: '1px solid rgba(212,175,55,0.2)' }}>
      {label !== undefined && (
        <p className="text-[#D4AF37] text-xs font-bold mb-2.5 pb-2"
          style={{ borderBottom: '1px solid rgba(212,175,55,0.1)' }}>{label}</p>
      )}
      {payload.map((p: any, i: number) => {
        const val = Number(p.value ?? 0)
        const color = p.color || p.fill || C.gold
        return (
          <div key={i} className="mb-1.5">
            <div className="flex items-center justify-between gap-3 mb-0.5">
              <span className="flex items-center gap-1.5 text-gray-400 text-xs">
                <span className="w-2 h-2 rounded-full shrink-0" style={{ background: color }} />
                {p.name}
              </span>
              <span className="font-bold text-white">{fmt(val)}{unit}</span>
            </div>
            {mean !== undefined && i === 0 && (
              <p className="text-[10px] pl-3.5" style={{ color: val > mean ? C.emerald : C.coral }}>
                {describe(val, mean, 1)} · {fmtPct(((val - mean) / Math.abs(mean || 1)) * 100)} vs avg
              </p>
            )}
          </div>
        )
      })}
      {extraLine && (
        <p className="text-[10px] text-gray-500 mt-2 pt-2 border-t border-white/5">{extraLine}</p>
      )}
    </div>
  )
}

// ─── Chart Card ───────────────────────────────────────────────────────────────
function ChartCard({
  title, question, badge, badgeColor = C.gold,
  icon: Icon = BarChart3, iconColor = C.gold,
  insight, insightType = 'neutral',
  children, controls, fullWidth = false,
}: {
  title: string
  question?: string    // "What does this answer?" — plain English
  badge?: string
  badgeColor?: string
  icon?: any
  iconColor?: string
  insight?: string
  insightType?: 'positive' | 'negative' | 'warning' | 'neutral'
  children: React.ReactNode
  controls?: React.ReactNode
  fullWidth?: boolean
}) {
  const insightColors = {
    positive: { bg: 'rgba(46,204,113,0.06)', border: 'rgba(46,204,113,0.15)', text: C.emerald },
    negative: { bg: 'rgba(255,107,107,0.06)', border: 'rgba(255,107,107,0.15)', text: C.coral },
    warning:  { bg: 'rgba(243,156,18,0.06)',  border: 'rgba(243,156,18,0.15)',  text: C.amber },
    neutral:  { bg: 'rgba(212,175,55,0.05)',  border: 'rgba(212,175,55,0.12)',  text: C.gold },
  }
  const ic = insightColors[insightType]

  return (
    <div className={`job-card overflow-hidden chart-enter ${fullWidth ? 'col-span-full' : ''}`}>
      {/* Header */}
      <div className="px-5 py-4 section-divider">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-3 min-w-0">
            <div className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 mt-0.5"
              style={{ background: `${iconColor}15` }}>
              <Icon className="w-4 h-4" style={{ color: iconColor }} />
            </div>
            <div className="min-w-0">
              <h3 className="font-bold text-white text-sm leading-tight">{title}</h3>
              {question && (
                <p className="text-gray-500 text-xs mt-0.5 leading-relaxed">{question}</p>
              )}
            </div>
          </div>
          {badge && (
            <span className="text-[10px] uppercase tracking-wider px-2 py-1 rounded-lg font-semibold shrink-0"
              style={{ color: badgeColor, background: `${badgeColor}12` }}>
              {badge}
            </span>
          )}
        </div>
      </div>

      {/* Controls */}
      {controls && (
        <div className="px-5 py-2.5 flex items-center gap-2 flex-wrap"
          style={{ borderBottom: '1px solid rgba(212,175,55,0.05)' }}>
          {controls}
        </div>
      )}

      {/* Chart */}
      <div className="p-5">{children}</div>

      {/* Insight */}
      {insight && (
        <div className="px-5 pb-5">
          <div className="flex items-start gap-2.5 p-3.5 rounded-xl text-xs leading-relaxed"
            style={{ background: ic.bg, border: `1px solid ${ic.border}` }}>
            <Sparkles className="w-3.5 h-3.5 mt-0.5 shrink-0" style={{ color: ic.text }} />
            <p style={{ color: ic.text === C.gold ? '#c4a035' : ic.text }}>{insight}</p>
          </div>
        </div>
      )}
    </div>
  )
}

// ─── Controls ─────────────────────────────────────────────────────────────────
function Sel({
  value, onChange, options, label,
}: { value: string; onChange: (v: string) => void; options: { v: string; l: string }[]; label?: string }) {
  return (
    <div className="flex items-center gap-1.5">
      {label && <span className="text-xs text-gray-600 shrink-0">{label}:</span>}
      <div className="relative">
        <select value={value} onChange={e => onChange(e.target.value)}
          className="text-xs rounded-lg pl-2.5 pr-6 py-1.5 appearance-none cursor-pointer"
          style={{ background: 'rgba(212,175,55,0.07)', border: '1px solid rgba(212,175,55,0.18)', color: '#ccc', outline: 'none' }}>
          {options.map(o => (
            <option key={o.v} value={o.v} style={{ background: '#12121e' }}>{o.l}</option>
          ))}
        </select>
        <ChevronDown className="absolute right-1.5 top-1/2 -translate-y-1/2 w-3 h-3 text-gray-500 pointer-events-none" />
      </div>
    </div>
  )
}

function TopN({ value, onChange, opts = [5, 10, 15, 20] }: { value: number; onChange: (n: number) => void; opts?: number[] }) {
  return (
    <div className="flex items-center gap-1">
      <span className="text-xs text-gray-600 mr-0.5">Top</span>
      {opts.map(n => (
        <button key={n} onClick={() => onChange(n)}
          className="text-xs w-7 h-6 rounded-md transition-all font-medium"
          style={value === n
            ? { background: 'rgba(212,175,55,0.18)', border: '1px solid rgba(212,175,55,0.4)', color: C.gold }
            : { background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.05)', color: '#555' }
          }>{n}</button>
      ))}
    </div>
  )
}

// ─── Mini Stat Badge ──────────────────────────────────────────────────────────
function StatBadge({ label, value, sub, color = C.gold }: { label: string; value: string; sub?: string; color?: string }) {
  return (
    <div className="rounded-xl p-3 text-center flex-1"
      style={{ background: `${color}08`, border: `1px solid ${color}15` }}>
      <div className="text-[10px] text-gray-500 mb-0.5">{label}</div>
      <div className="text-sm font-bold" style={{ color }}>{value}</div>
      {sub && <div className="text-[9px] text-gray-600 mt-0.5">{sub}</div>}
    </div>
  )
}

// ─── CHART 1: Executive KPI Cards with Sparklines ─────────────────────────────
function KpiDashboard({ kpis }: { kpis: any[] }) {
  const [expanded, setExpanded] = useState<number | null>(null)
  if (!kpis?.length) return null

  const topKpis = kpis.slice(0, 8)

  return (
    <ChartCard
      title="Key Performance Indicators"
      question="How are our main metrics performing right now?"
      badge="KPIs"
      icon={Target}
      iconColor={C.gold}
      fullWidth
      insight={(() => {
        const pos = topKpis.filter(k => (k.pct_change ?? 0) > 0).length
        const neg = topKpis.filter(k => (k.pct_change ?? 0) < 0).length
        if (pos > neg) return `${pos} of ${topKpis.length} metrics are trending upward. Positive momentum overall — maintain the strategies driving growth.`
        if (neg > pos) return `${neg} of ${topKpis.length} metrics are declining. Needs attention — review which areas are underperforming and why.`
        return `Mixed signals — half the metrics are up, half are down. Deep-dive into individual trends to identify root causes.`
      })()}
      insightType={
        topKpis.filter(k => (k.pct_change ?? 0) > 0).length > topKpis.length / 2
          ? 'positive' : 'warning'
      }
    >
      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-3">
        {topKpis.map((kpi, i) => {
          const color     = SEQ[i % SEQ.length]
          const pct       = kpi.pct_change
          const isPos     = (pct ?? 0) > 0
          const isNeutral = Math.abs(pct ?? 0) < 0.5
          const spark     = (kpi.sparkline || []).map((v: number, j: number) => ({ j, v }))
          const isExp     = expanded === i

          return (
            <button key={i} onClick={() => setExpanded(isExp ? null : i)}
              className="rounded-2xl p-4 text-left transition-all duration-300 group"
              style={{
                background: isExp ? `${color}10` : 'rgba(255,255,255,0.02)',
                border: `1px solid ${isExp ? `${color}30` : 'rgba(212,175,55,0.08)'}`,
                boxShadow: isExp ? `0 0 20px ${color}15` : 'none',
              }}>
              {/* Header */}
              <div className="flex items-start justify-between mb-2">
                <p className="text-xs text-gray-500 leading-tight pr-1 line-clamp-2">
                  {kpi.display_name}
                </p>
                {pct !== null && pct !== undefined && (
                  <span className={`flex items-center gap-0.5 text-xs font-bold shrink-0 ${
                    isNeutral ? 'text-gray-500'
                    : isPos ? 'text-emerald-400' : 'text-red-400'
                  }`}>
                    {isNeutral ? <Minus className="w-3 h-3" />
                      : isPos ? <ArrowUpRight className="w-3 h-3" />
                      : <ArrowDownRight className="w-3 h-3" />}
                    {Math.abs(pct).toFixed(1)}%
                  </span>
                )}
              </div>

              {/* Value */}
              <div className="text-2xl font-bold mb-1" style={{ color }}>
                {kpi.formatted_value || fmt(kpi.value)}
              </div>
              <div className="text-xs text-gray-600 mb-3">
                Total: {kpi.formatted_total || fmt(kpi.total)}
              </div>

              {/* Sparkline */}
              {spark.length > 2 && (
                <div className="h-12 -mx-1">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={spark}>
                      <defs>
                        <linearGradient id={`k${i}`} x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor={color} stopOpacity={0.4} />
                          <stop offset="100%" stopColor={color} stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <Area type="monotone" dataKey="v" stroke={color} strokeWidth={1.5}
                        fill={`url(#k${i})`} dot={false} />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              )}

              {/* Expanded stats */}
              {isExp && kpi.min !== undefined && (
                <div className="mt-3 pt-3 grid grid-cols-3 gap-1.5 text-center"
                  style={{ borderTop: `1px solid ${color}20` }}>
                  {[
                    { l: 'Min',    v: fmt(kpi.min) },
                    { l: 'Avg',    v: fmt(kpi.value) },
                    { l: 'Max',    v: fmt(kpi.max) },
                  ].map(s => (
                    <div key={s.l}>
                      <div className="text-[9px] text-gray-600">{s.l}</div>
                      <div className="text-xs font-bold text-gray-300">{s.v}</div>
                    </div>
                  ))}
                </div>
              )}
            </button>
          )
        })}
      </div>
    </ChartCard>
  )
}

// ─── CHART 2: Ranked Leaderboard with Pareto Line ─────────────────────────────
function LeaderboardChart({ segments }: { segments: any[] }) {
  const [topN,     setTopN]     = useState(10)
  const [segIdx,   setSegIdx]   = useState(0)
  const [metric,   setMetric]   = useState<'total' | 'mean'>('total')
  const [showPareto, setPareto] = useState(true)

  const seg = segments[segIdx]
  if (!seg?.data?.length) return null

  const allSorted = [...seg.data].sort((a, b) => (b[metric] ?? 0) - (a[metric] ?? 0))
  const data      = allSorted.slice(0, topN)
  const grandTotal = allSorted.reduce((s, d) => s + (d[metric] ?? 0), 0)

  // Add cumulative % for Pareto line
  let cum = 0
  const withPareto = data.map(d => {
    cum += (d[metric] ?? 0)
    return {
      name:       (d.category?.toString() || '').slice(0, 22),
      value:      d[metric] ?? 0,
      share:      d.share_pct ?? 0,
      pareto:     grandTotal > 0 ? (cum / grandTotal) * 100 : 0,
      direction:  d.direction,
    }
  })

  // Find 80% cutoff (Pareto)
  const paretoIdx = withPareto.findIndex(d => d.pareto >= 80)

  const top    = withPareto[0]
  const bottom = withPareto[withPareto.length - 1]
  const gapPct = top && bottom && bottom.value > 0
    ? ((top.value - bottom.value) / bottom.value * 100).toFixed(0)
    : null

  const segOpts = segments.slice(0, 5).map((s, i) => ({
    v: String(i),
    l: `${dname(s.display_dimension)} by ${dname(s.display_metric)}`,
  }))

  return (
    <ChartCard
      title={`${dname(seg.display_dimension)} Performance Ranking`}
      question={`Who are the top ${topN} performers? Where should we focus?`}
      badge="Ranking"
      icon={Award}
      iconColor={C.gold}
      insight={(() => {
        if (!top) return ''
        const paretoN = paretoIdx >= 0 ? paretoIdx + 1 : null
        return `"${top.name}" is #1 with ${fmt(top.value)} (${top.share.toFixed(1)}% of total).${
          gapPct ? ` The top-bottom gap is ${gapPct}% — huge opportunity in low performers.` : ''
        }${paretoN ? ` Pareto rule: top ${paretoN} segments = 80% of all value. Focus here first.` : ''}`
      })()}
      insightType="neutral"
      controls={
        <>
          <TopN value={topN} onChange={setTopN} opts={[5, 10, 15]} />
          <Sel value={metric} onChange={v => setMetric(v as any)}
            options={[{ v: 'total', l: 'Total' }, { v: 'mean', l: 'Average' }]}
            label="Metric" />
          {segments.length > 1 && (
            <Sel value={String(segIdx)} onChange={v => setSegIdx(Number(v))}
              options={segOpts} label="Dimension" />
          )}
          <button onClick={() => setPareto(v => !v)}
            className="text-xs px-2.5 py-1.5 rounded-lg transition-all"
            style={showPareto
              ? { background: 'rgba(243,156,18,0.12)', border: '1px solid rgba(243,156,18,0.3)', color: C.amber }
              : { background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)', color: '#555' }
            }>
            Pareto 80%
          </button>
        </>
      }
    >
      <div style={{ height: Math.max(200, topN * 30 + 30) }}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={withPareto} layout="vertical"
            margin={{ left: 10, right: showPareto ? 55 : 70, top: 5, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={GRID_STROKE} horizontal={false} />
            <XAxis type="number" stroke={AXIS_STROKE} tick={AXIS_TICK_SM} tickFormatter={v => fmt(v)} />
            <YAxis type="category" dataKey="name" stroke={AXIS_STROKE} tick={AXIS_TICK_SM} width={130} />
            {showPareto && (
              <YAxis yAxisId="pareto" orientation="right" stroke={AXIS_STROKE}
                tick={AXIS_TICK_SM} tickFormatter={v => `${v}%`} domain={[0, 100]} />
            )}
            <Tooltip content={({ active, payload, label }) => {
              if (!active || !payload?.length) return null
              const d = payload[0]?.payload
              return (
                <div className="rounded-2xl p-4 shadow-2xl text-sm max-w-[220px]"
                  style={{ background: '#0e0e1a', border: '1px solid rgba(212,175,55,0.2)' }}>
                  <p className="font-bold text-white mb-2">{label}</p>
                  <div className="flex justify-between gap-3 mb-1">
                    <span className="text-gray-400 text-xs">Value</span>
                    <span className="font-bold text-[#D4AF37]">{fmt(d?.value)}</span>
                  </div>
                  <div className="flex justify-between gap-3 mb-1">
                    <span className="text-gray-400 text-xs">Share of total</span>
                    <span className="font-bold text-white">{d?.share?.toFixed(1)}%</span>
                  </div>
                  {showPareto && (
                    <div className="flex justify-between gap-3">
                      <span className="text-gray-400 text-xs">Cumulative</span>
                      <span className="font-bold text-amber-400">{d?.pareto?.toFixed(1)}%</span>
                    </div>
                  )}
                </div>
              )
            }} />
            {/* 80% Pareto reference line */}
            {showPareto && paretoIdx >= 0 && (
              <ReferenceLine yAxisId="pareto" y={80}
                stroke={`${C.amber}60`} strokeDasharray="5 3"
                label={{ value: '80%', position: 'right', fill: C.amber, fontSize: 9 }} />
            )}
            <Bar dataKey="value" name={dname(seg.display_metric)}
              radius={[0, 5, 5, 0]} maxBarSize={24}>
              {withPareto.map((d, i) => (
                <Cell key={i}
                  fill={i === 0 ? C.gold
                    : d.pareto <= 80 ? `${C.gold}${Math.round(160 - i * 10).toString(16).padStart(2,'0')}`
                    : `${C.gray}60`}
                />
              ))}
              <LabelList dataKey="value" position="right"
                formatter={(v: number) => fmt(v)}
                style={{ fontSize: 9, fill: '#888' }} />
            </Bar>
            {showPareto && (
              <Line yAxisId="pareto" type="monotone" dataKey="pareto" name="Cumulative %"
                stroke={C.amber} strokeWidth={2} dot={false} strokeDasharray="4 2" />
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </ChartCard>
  )
}

// ─── CHART 3: Trend + Annotations ─────────────────────────────────────────────
function TrendChart({ timeSeries }: { timeSeries: any[] }) {
  const [mIdx, setMIdx] = useState(0)
  const [mode, setMode] = useState<'abs' | 'mom' | 'yoy'>('abs')

  const ts = timeSeries[0]
  if (!ts?.data?.length) return null
  const metrics = ts.metrics || []
  const m       = metrics[mIdx]
  if (!m) return null

  const baseKey = m.key
  const dataKey = mode === 'abs' ? baseKey
    : mode === 'mom' ? `${baseKey}_pct_change`
    : `${baseKey}_cumulative_pct`

  const data = ts.data
    .filter((d: any) => d[dataKey] !== null && d[dataKey] !== undefined)
    .map((d: any) => ({ ...d, _v: Number(d[dataKey] ?? 0) }))

  const vals  = data.map((d: any) => d._v)
  const avg   = vals.length ? vals.reduce((a: number, b: number) => a + b, 0) / vals.length : 0
  const maxV  = vals.length ? Math.max(...vals) : 0
  const minV  = vals.length ? Math.min(...vals) : 0
  const last  = vals[vals.length - 1] ?? 0
  const first = vals[0] ?? 0
  const totalChange = first !== 0 ? ((last - first) / Math.abs(first)) * 100 : 0

  // Find peak and trough indices
  const peakIdx  = vals.indexOf(maxV)
  const troughIdx = vals.indexOf(minV)

  const isTrendUp = last > avg

  const metOpts = metrics.slice(0, 5).map((me: any, i: number) => ({
    v: String(i), l: me.display_name,
  }))

  return (
    <ChartCard
      title={`${m.display_name} — ${ts.period || 'Time'} Trend`}
      question={`Is ${m.display_name} going up or down over time?`}
      badge="Trend"
      icon={isTrendUp ? TrendingUp : TrendingDown}
      iconColor={isTrendUp ? C.emerald : C.coral}
      fullWidth
      insight={`Overall ${totalChange > 0 ? 'growth' : 'decline'} of ${Math.abs(totalChange).toFixed(1)}% from start to end. `
        + `Peak was ${fmt(maxV)} (period ${data[peakIdx]?.period || peakIdx + 1}). `
        + (Math.abs(totalChange) > 20
          ? totalChange > 0
            ? `Strong positive momentum — investigate key drivers to replicate this growth.`
            : `Significant decline needs root cause analysis — what changed?`
          : `Relatively stable performance. Monitor for emerging directional shifts.`
        )}
      insightType={totalChange > 5 ? 'positive' : totalChange < -5 ? 'negative' : 'neutral'}
      controls={
        <>
          {metrics.length > 1 && (
            <Sel value={String(mIdx)} onChange={v => setMIdx(Number(v))}
              options={metOpts} label="Metric" />
          )}
          <Sel value={mode} onChange={v => setMode(v as any)}
            options={[
              { v: 'abs', l: 'Actual Value' },
              { v: 'mom', l: 'Period-over-Period %' },
              { v: 'yoy', l: 'Cumulative Growth %' },
            ]} label="View" />
        </>
      }
    >
      <div className="mb-4 flex gap-3">
        <StatBadge label="Change" value={fmtPct(totalChange)}
          color={totalChange >= 0 ? C.emerald : C.coral}
          sub="start → end" />
        <StatBadge label="Peak" value={fmt(maxV)}
          color={C.gold} sub={data[peakIdx]?.period || '-'} />
        <StatBadge label="Avg / Period" value={fmt(avg)}
          color={C.teal} sub="baseline" />
        <StatBadge label="Low" value={fmt(minV)}
          color={C.gray} sub={data[troughIdx]?.period || '-'} />
      </div>

      <div className="h-[260px]">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 5 }}>
            <defs>
              <linearGradient id="tg" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={isTrendUp ? C.emerald : C.coral} stopOpacity={0.35} />
                <stop offset="100%" stopColor={isTrendUp ? C.emerald : C.coral} stopOpacity={0.02} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke={GRID_STROKE} />
            <XAxis dataKey="period" stroke={AXIS_STROKE} tick={AXIS_TICK_SM}
              interval="preserveStartEnd" />
            <YAxis stroke={AXIS_STROKE} tick={AXIS_TICK} tickFormatter={v => fmt(v)} />
            <Tooltip content={({ active, payload, label }) => {
              if (!active || !payload?.length) return null
              const v = Number(payload[0]?.value ?? 0)
              return (
                <div className="rounded-2xl p-4 shadow-2xl text-sm"
                  style={{ background: '#0e0e1a', border: '1px solid rgba(212,175,55,0.2)' }}>
                  <p className="text-[#D4AF37] text-xs font-bold mb-2">{label}</p>
                  <div className="flex justify-between gap-4 mb-1">
                    <span className="text-gray-400 text-xs">{mode === 'abs' ? 'Value' : mode === 'mom' ? 'vs prev period' : 'vs start'}</span>
                    <span className="font-bold text-white">{fmt(v)}{mode !== 'abs' ? '%' : ''}</span>
                  </div>
                  {mode === 'abs' && avg > 0 && (
                    <p className="text-[10px] mt-1" style={{ color: v >= avg ? C.emerald : C.coral }}>
                      {v >= avg ? '↑ above' : '↓ below'} avg ({fmt(avg)})
                    </p>
                  )}
                </div>
              )
            }} />
            {/* Average reference line */}
            {mode === 'abs' && (
              <ReferenceLine y={avg} stroke={`${C.amber}70`} strokeDasharray="6 3"
                label={{ value: `Avg ${fmt(avg)}`, position: 'right', fill: C.amber, fontSize: 9 }} />
            )}
            {mode !== 'abs' && (
              <ReferenceLine y={0} stroke="rgba(255,255,255,0.15)" />
            )}
            <Area type="monotone" dataKey="_v"
              name={mode === 'abs' ? m.display_name : mode === 'mom' ? '% vs prev' : 'Cumulative %'}
              stroke={isTrendUp ? C.emerald : C.coral}
              strokeWidth={2.5} fill="url(#tg)" dot={false} activeDot={{ r: 4 }} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </ChartCard>
  )
}

// ─── CHART 4: Segment vs Average (Diverging) ──────────────────────────────────
function SegmentVsAvgChart({ pctChanges, segments }: { pctChanges: any[]; segments: any[] }) {
  const [topN, setTopN]   = useState(12)
  const [sort, setSort]   = useState<'best' | 'worst' | 'alpha'>('best')
  const [segIdx, setSegIdx] = useState(0)

  const vsAvg = pctChanges.find((x: any) => x.type === 'vs_average')

  // Build data from vs_average or fall back to segment data
  const rawData = useMemo(() => {
    if (vsAvg?.data?.length) return vsAvg.data
    const seg = segments[segIdx]
    if (!seg?.data?.length) return []
    const overallMean = seg.overall_mean || 0
    return seg.data.map((d: any) => ({
      category: d.category,
      pct_vs_average: overallMean > 0 ? ((d.mean - overallMean) / overallMean) * 100 : 0,
      value: d.mean,
    }))
  }, [vsAvg, segments, segIdx])

  if (!rawData.length) return null

  const segOpts = segments.slice(0, 4).map((s: any, i: number) => ({
    v: String(i), l: `${dname(s.display_dimension)} by ${dname(s.display_metric)}`,
  }))

  const sorted = [...rawData].sort((a, b) => {
    if (sort === 'best')  return (b.pct_vs_average ?? 0) - (a.pct_vs_average ?? 0)
    if (sort === 'worst') return (a.pct_vs_average ?? 0) - (b.pct_vs_average ?? 0)
    return String(a.category).localeCompare(String(b.category))
  }).slice(0, topN)

  const above = sorted.filter(d => (d.pct_vs_average ?? 0) > 0).length
  const below = sorted.length - above
  const maxGap = Math.max(...sorted.map(d => Math.abs(d.pct_vs_average ?? 0)))

  return (
    <ChartCard
      title="Who's Above vs Below Average?"
      question="Which segments are outperforming or underperforming the average?"
      badge="Compare"
      icon={ArrowLeftRight}
      iconColor={C.emerald}
      insight={`${above} segments beat the average, ${below} are below. ${
        above > below
          ? `Majority is outperforming — build on this momentum.`
          : `Majority is underperforming — identify root causes in the red segments.`
      } Largest gap: ${maxGap.toFixed(0)}% — significant spread in performance.`}
      insightType={above > below ? 'positive' : 'warning'}
      controls={
        <>
          <TopN value={topN} onChange={setTopN} opts={[8, 12, 20]} />
          <Sel value={sort} onChange={v => setSort(v as any)}
            options={[
              { v: 'best',  l: '🏆 Best First' },
              { v: 'worst', l: '⚠️ Worst First' },
              { v: 'alpha', l: 'A → Z' },
            ]} label="Order" />
          {!vsAvg && segments.length > 1 && (
            <Sel value={String(segIdx)} onChange={v => setSegIdx(Number(v))}
              options={segOpts} label="Segment" />
          )}
        </>
      }
    >
      {/* Legend */}
      <div className="flex items-center gap-4 mb-4 text-xs text-gray-500">
        <span className="flex items-center gap-1.5">
          <span className="w-3 h-2 rounded inline-block" style={{ background: C.emerald }} />
          Above average
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-3 h-2 rounded inline-block" style={{ background: C.coral }} />
          Below average
        </span>
        <span className="ml-auto font-medium" style={{ color: C.amber }}>
          0 = average baseline
        </span>
      </div>
      <div style={{ height: Math.max(220, sorted.length * 28 + 20) }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={sorted} layout="vertical"
            margin={{ left: 10, right: 55, top: 5, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={GRID_STROKE} horizontal={false} />
            <XAxis type="number" stroke={AXIS_STROKE} tick={AXIS_TICK_SM}
              tickFormatter={v => `${v > 0 ? '+' : ''}${v}%`} />
            <YAxis type="category" dataKey="category" stroke={AXIS_STROKE}
              tick={AXIS_TICK_SM} width={115} />
            <Tooltip content={({ active, payload, label }) => {
              if (!active || !payload?.length) return null
              const v = Number(payload[0]?.value ?? 0)
              return (
                <div className="rounded-2xl p-4 shadow-2xl text-sm"
                  style={{ background: '#0e0e1a', border: '1px solid rgba(212,175,55,0.2)' }}>
                  <p className="font-bold text-white mb-2">{label}</p>
                  <p className="text-xs mb-1" style={{ color: v >= 0 ? C.emerald : C.coral }}>
                    {v >= 0 ? `+${v.toFixed(1)}% above average` : `${v.toFixed(1)}% below average`}
                  </p>
                  <p className="text-[10px] text-gray-500">
                    {Math.abs(v) > 20 ? 'Significant deviation — investigate' : 'Within normal range'}
                  </p>
                </div>
              )
            }} />
            <ReferenceLine x={0} stroke="rgba(255,255,255,0.2)" strokeWidth={1.5} />
            <Bar dataKey="pct_vs_average" name="vs Average" radius={[0, 4, 4, 0]} maxBarSize={20}>
              {sorted.map((d: any, i: number) => (
                <Cell key={i}
                  fill={(d.pct_vs_average ?? 0) >= 0 ? C.emerald : C.coral}
                  opacity={0.6 + Math.min(Math.abs(d.pct_vs_average ?? 0) / 100, 0.4)} />
              ))}
              <LabelList dataKey="pct_vs_average" position="right"
                formatter={(v: number) => `${v > 0 ? '+' : ''}${v?.toFixed(0)}%`}
                style={{ fontSize: 9, fill: '#888' }} />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </ChartCard>
  )
}

// ─── CHART 5: Distribution with Normal Curve Context ──────────────────────────
function DistributionChart({ distributions }: { distributions: any[] }) {
  const [dIdx, setDIdx] = useState(0)
  const [view, setView] = useState<'hist' | 'pct'>('hist')

  const good = useMemo(() => distributions.filter(d => {
    const s = d.stats
    if (!s) return false
    const cv = Math.abs(s.std / (s.mean || 1)) * 100
    if (cv < 1) return false   // near-zero variance = boring
    if (s.min >= 0 && s.max <= 1 && s.max - s.min < 0.05) return false  // binary
    return d.histogram?.length >= 4
  }), [distributions])

  if (!good.length) return null
  const dist = good[Math.min(dIdx, good.length - 1)]
  const s    = dist?.stats
  const hist = dist?.histogram || []
  const pcts = dist?.percentile_data || []

  // Classify the shape for plain-English
  const shape = !s ? '' : (() => {
    const skew = s.skewness ?? 0
    if (Math.abs(skew) < 0.5) return 'bell-shaped — most values cluster around the middle'
    if (skew > 1.5)  return 'right-tailed — most values are low with a few very high outliers'
    if (skew > 0.5)  return 'slightly right-skewed — median is better than mean here'
    if (skew < -1.5) return 'left-tailed — most values are high with a few very low outliers'
    return 'slightly left-skewed — strong majority performing above average'
  })()

  const distOpts = good.slice(0, 8).map((d, i) => ({ v: String(i), l: d.display_name }))

  return (
    <ChartCard
      title={`How is "${dist?.display_name}" Distributed?`}
      question="Where do most values fall? Are there outliers or unusual patterns?"
      badge="Distribution"
      icon={BarChart2}
      iconColor={C.purple}
      insight={s
        ? `Distribution is ${shape}. Typical value (median): ${fmt(s.median)}. Average: ${fmt(s.mean)}. `
          + `${Math.abs((s.mean - s.median) / (s.std || 1)) > 0.5
            ? `Gap between mean and median = skew is present — use MEDIAN not mean for reporting.`
            : `Mean and median are close — averages are reliable here.`
          }${s.outlier_pct > 5 ? ` ⚠️ ${s.outlier_pct}% outliers detected — these deserve individual investigation.` : ''}`
        : ''}
      insightType={s?.outlier_pct > 10 ? 'warning' : 'neutral'}
      controls={
        <>
          {good.length > 1 && (
            <Sel value={String(dIdx)} onChange={v => setDIdx(Number(v))}
              options={distOpts} label="Column" />
          )}
          <Sel value={view} onChange={v => setView(v as any)}
            options={[{ v: 'hist', l: 'Frequency' }, { v: 'pct', l: 'Percentiles P5–P95' }]}
            label="View" />
        </>
      }
    >
      <div className="h-[230px]">
        <ResponsiveContainer width="100%" height="100%">
          {view === 'hist' ? (
            <BarChart data={hist} margin={{ top: 10, right: 10, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={GRID_STROKE} vertical={false} />
              <XAxis dataKey="label" stroke={AXIS_STROKE} tick={AXIS_TICK_SM}
                interval="preserveStartEnd" />
              <YAxis stroke={AXIS_STROKE} tick={AXIS_TICK_SM}
                label={{ value: 'Count', angle: -90, position: 'insideLeft', fill: '#555', fontSize: 9 }} />
              <Tooltip content={({ active, payload, label }) => {
                if (!active || !payload?.length) return null
                const p = payload[0]?.payload
                return (
                  <div className="rounded-2xl p-4 shadow-2xl text-sm"
                    style={{ background: '#0e0e1a', border: '1px solid rgba(212,175,55,0.2)' }}>
                    <p className="text-gray-400 text-xs mb-1">Range: {label}</p>
                    <div className="flex justify-between gap-3">
                      <span className="text-gray-400 text-xs">Records in this range</span>
                      <span className="font-bold text-white">{p?.count?.toLocaleString()}</span>
                    </div>
                    <p className="text-[10px] text-gray-500 mt-1">{p?.pct}% of all data</p>
                  </div>
                )
              }} />
              <Bar dataKey="count" name="Records" radius={[3, 3, 0, 0]}>
                {hist.map((_: any, i: number) => (
                  <Cell key={i} fill={`${C.purple}${Math.round(50 + (i / hist.length) * 160).toString(16).padStart(2,'0')}`} />
                ))}
              </Bar>
              {s?.mean !== undefined && (
                <ReferenceLine
                  x={hist.find((h: any) => h.bin_start <= s.mean && h.bin_end > s.mean)?.label
                     || hist[Math.floor(hist.length / 2)]?.label}
                  stroke={C.coral} strokeDasharray="4 2" strokeWidth={1.5}
                  label={{ value: `Mean ${fmt(s.mean)}`, position: 'top', fill: C.coral, fontSize: 9 }} />
              )}
              {s?.median !== undefined && (
                <ReferenceLine
                  x={hist.find((h: any) => h.bin_start <= s.median && h.bin_end > s.median)?.label
                     || hist[Math.floor(hist.length / 2)]?.label}
                  stroke={C.gold} strokeDasharray="4 2" strokeWidth={1.5}
                  label={{ value: `Median ${fmt(s.median)}`, position: 'insideTopRight', fill: C.gold, fontSize: 9 }} />
              )}
            </BarChart>
          ) : (
            <BarChart data={pcts} margin={{ top: 10, right: 5, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={GRID_STROKE} vertical={false} />
              <XAxis dataKey="label" stroke={AXIS_STROKE} tick={AXIS_TICK} />
              <YAxis stroke={AXIS_STROKE} tick={AXIS_TICK} tickFormatter={v => fmt(v)} />
              <Tooltip content={({ active, payload, label }) => {
                if (!active || !payload?.length) return null
                const v = Number(payload[0]?.value ?? 0)
                const descs: Record<string, string> = {
                  P5:  '5% of records are below this value',
                  P25: '25% of records are below (bottom quarter)',
                  P50: 'Half are below, half above (median)',
                  P75: '75% of records are below (top quarter)',
                  P95: '95% of records are below this value',
                }
                return (
                  <div className="rounded-2xl p-4 shadow-2xl text-sm"
                    style={{ background: '#0e0e1a', border: '1px solid rgba(212,175,55,0.2)' }}>
                    <p className="font-bold text-white mb-2">{label}</p>
                    <p className="text-[#D4AF37] text-sm font-bold mb-1">{fmt(v)}</p>
                    <p className="text-[10px] text-gray-500">{descs[label] || ''}</p>
                  </div>
                )
              }} />
              <Bar dataKey="value" name="Value at percentile" radius={[4, 4, 0, 0]}>
                {pcts.map((_: any, i: number) => <Cell key={i} fill={SEQ[i % SEQ.length]} />)}
              </Bar>
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>

      {/* Stats row */}
      {s && (
        <div className="flex gap-2 mt-4">
          <StatBadge label="Median" value={fmt(s.median)} sub="typical value" color={C.gold} />
          <StatBadge label="Mean" value={fmt(s.mean)} sub="average" color={C.teal} />
          <StatBadge label="Spread (Std)" value={fmt(s.std)} sub="variation" color={C.purple} />
          <StatBadge label="Outliers" value={`${s.outlier_pct ?? 0}%`}
            sub={s.outlier_pct > 5 ? '⚠️ high' : 'normal'}
            color={s.outlier_pct > 10 ? C.coral : s.outlier_pct > 5 ? C.amber : C.gray} />
        </div>
      )}
    </ChartCard>
  )
}

// ─── CHART 6: Composition with totals ─────────────────────────────────────────
function CompositionChart({ composition }: { composition: any[] }) {
  const [cIdx, setCIdx] = useState(0)
  const [topN, setTopN] = useState(8)
  const comp = composition[cIdx]
  if (!comp?.data?.length) return null

  const sorted = [...comp.data].sort((a, b) => (b.value ?? 0) - (a.value ?? 0))
  const sliced = sorted.slice(0, topN)
  const rest   = sorted.slice(topN)
  const restSum = rest.reduce((s, d) => s + (d.value ?? 0), 0)
  const data    = restSum > 0
    ? [...sliced, { name: `Others (${rest.length})`, value: restSum, pct: rest.reduce((s, d) => s + (d.pct ?? 0), 0) }]
    : sliced

  const top      = sorted[0]
  const topShare = top?.pct ?? 0
  const hhi      = sorted.reduce((s, d) => s + Math.pow(d.pct ?? 0, 2), 0) // Herfindahl index
  const concentration = hhi > 2500 ? 'highly concentrated' : hhi > 1000 ? 'moderately concentrated' : 'well diversified'

  const compOpts = composition.slice(0, 4).map((c, i) => ({ v: String(i), l: c.display_name || `Set ${i + 1}` }))

  return (
    <ChartCard
      title={comp.display_name || 'Share of Total'}
      question="How is the total split across groups? Who dominates?"
      badge="Composition"
      icon={PieIcon}
      iconColor={C.amber}
      insight={`"${top?.name}" holds ${topShare.toFixed(1)}% — ${
        topShare > 60 ? 'dominant position, high dependency risk'
        : topShare > 40 ? 'leading position, but room for challengers'
        : 'competitive landscape with no dominant player'
      }. Market is ${concentration} (HHI = ${hhi.toFixed(0)}).`}
      insightType={topShare > 60 ? 'warning' : 'neutral'}
      controls={
        <>
          <TopN value={topN} onChange={setTopN} opts={[5, 8, 12]} />
          {composition.length > 1 && (
            <Sel value={String(cIdx)} onChange={v => setCIdx(Number(v))}
              options={compOpts} label="Metric" />
          )}
        </>
      }
    >
      <div className="flex items-center gap-5">
        {/* Donut */}
        <div style={{ width: 200, height: 200, flexShrink: 0 }}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={data} dataKey="value" nameKey="name"
                outerRadius={90} innerRadius={55} paddingAngle={2}
                startAngle={90} endAngle={-270}>
                {data.map((_: any, i: number) => (
                  <Cell key={i} fill={SEQ[i % SEQ.length]}
                    stroke="rgba(0,0,0,0.3)" strokeWidth={1} />
                ))}
              </Pie>
              <Tooltip content={({ active, payload }) => {
                if (!active || !payload?.length) return null
                const d = payload[0]?.payload
                return (
                  <div className="rounded-2xl p-3 shadow-2xl text-sm"
                    style={{ background: '#0e0e1a', border: '1px solid rgba(212,175,55,0.2)' }}>
                    <p className="font-bold text-white text-xs mb-1">{d?.name}</p>
                    <p style={{ color: C.gold }} className="font-bold">{fmt(d?.value)}</p>
                    <p className="text-[10px] text-gray-400">{(d?.pct ?? 0).toFixed(1)}% of total</p>
                  </div>
                )
              }} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Legend with bars */}
        <div className="flex-1 space-y-2">
          {data.slice(0, 9).map((d: any, i: number) => (
            <div key={i} className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full shrink-0" style={{ background: SEQ[i % SEQ.length] }} />
              <span className="text-xs text-gray-400 truncate flex-1" style={{ maxWidth: 120 }}>{d.name}</span>
              <div className="flex-1 h-1.5 rounded-full overflow-hidden mx-2"
                style={{ background: 'rgba(255,255,255,0.05)', minWidth: 40 }}>
                <div className="h-full rounded-full transition-all"
                  style={{ width: `${d.pct ?? 0}%`, background: SEQ[i % SEQ.length] }} />
              </div>
              <span className="text-xs font-bold text-gray-300 shrink-0 w-10 text-right">
                {(d.pct ?? 0).toFixed(1)}%
              </span>
            </div>
          ))}
        </div>
      </div>
    </ChartCard>
  )
}

// ─── CHART 7: X vs Y with Trend Line ──────────────────────────────────────────
function XvsYChart({ scatter }: { scatter: any[] }) {
  const [sIdx, setSIdx] = useState(0)
  const sc = scatter[sIdx]
  if (!scatter.length || !sc) return null

  const r    = Number(sc.correlation ?? 0)
  const rAbs = Math.abs(r)
  const dir  = r > 0 ? 'positive' : 'negative'

  // Compute linear trend line
  const data = (sc.data || []).slice(0, 800)
  let trendLine: { x: number; trend: number }[] = []
  if (data.length > 2) {
    const xs   = data.map((d: any) => d.x)
    const ys   = data.map((d: any) => d.y)
    const n    = xs.length
    const xAvg = xs.reduce((a: number, b: number) => a + b, 0) / n
    const yAvg = ys.reduce((a: number, b: number) => a + b, 0) / n
    const num  = xs.reduce((s: number, x: number, i: number) => s + (x - xAvg) * (ys[i] - yAvg), 0)
    const den  = xs.reduce((s: number, x: number) => s + (x - xAvg) ** 2, 0)
    const slope = den !== 0 ? num / den : 0
    const inter = yAvg - slope * xAvg
    const xMin  = Math.min(...xs), xMax = Math.max(...xs)
    trendLine = [
      { x: xMin, trend: slope * xMin + inter },
      { x: xMax, trend: slope * xMax + inter },
    ]
  }

  const scOpts = scatter.slice(0, 8).map((s, i) => ({
    v: String(i), l: `${dname(s.display_x)} vs ${dname(s.display_y)}`,
  }))

  const strengthLabel = rAbs > 0.8 ? 'very strong' : rAbs > 0.6 ? 'strong'
    : rAbs > 0.4 ? 'moderate' : rAbs > 0.2 ? 'weak' : 'very weak'

  return (
    <ChartCard
      title={`${dname(sc.display_x)} vs ${dname(sc.display_y)}`}
      question={`If ${dname(sc.display_x)} changes, does ${dname(sc.display_y)} follow?`}
      badge="Relationship"
      icon={GitBranch}
      iconColor={rAbs > 0.5 ? C.emerald : C.gray}
      insight={`${strengthLabel.charAt(0).toUpperCase() + strengthLabel.slice(1)} ${dir} relationship (r = ${r.toFixed(2)}). `
        + (rAbs > 0.6
          ? `These two metrics are closely linked — when ${dname(sc.display_x)} ${r > 0 ? 'rises' : 'falls'}, ${dname(sc.display_y)} tends to ${r > 0 ? 'rise' : 'fall'} too. Use this for forecasting.`
          : rAbs > 0.3
          ? `Some connection exists, but other factors also influence ${dname(sc.display_y)}. Useful signal, not a definitive predictor.`
          : `These metrics are mostly independent — changes in one don't reliably predict the other.`)}
      insightType={rAbs > 0.6 ? 'positive' : rAbs > 0.3 ? 'neutral' : 'neutral'}
      controls={
        scatter.length > 1 ? (
          <Sel value={String(sIdx)} onChange={v => setSIdx(Number(v))}
            options={scOpts} label="Pair" />
        ) : undefined
      }
    >
      {/* Correlation badge row */}
      <div className="flex gap-3 mb-4">
        <StatBadge label="Correlation r" value={r.toFixed(3)}
          color={rAbs > 0.6 ? C.emerald : rAbs > 0.3 ? C.amber : C.gray}
          sub={strengthLabel} />
        <StatBadge label="Strength" value={rAbs > 0.6 ? 'Strong' : rAbs > 0.3 ? 'Moderate' : 'Weak'}
          color={rAbs > 0.6 ? C.emerald : rAbs > 0.3 ? C.amber : C.gray}
          sub={`${(rAbs * 100).toFixed(0)}% explained`} />
        <StatBadge label="Direction" value={r > 0 ? '↑ Positive' : '↓ Negative'}
          color={r > 0 ? C.teal : C.coral} sub={r > 0 ? 'move together' : 'move apart'} />
      </div>

      <div className="h-[260px]">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart margin={{ top: 10, right: 10, left: 0, bottom: 30 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={GRID_STROKE} />
            <XAxis type="number" dataKey="x" stroke={AXIS_STROKE} tick={AXIS_TICK_SM}
              tickFormatter={v => fmt(v)}
              label={{ value: dname(sc.display_x), position: 'insideBottom', offset: -12, fill: '#666', fontSize: 10 }} />
            <YAxis stroke={AXIS_STROKE} tick={AXIS_TICK_SM} tickFormatter={v => fmt(v)}
              label={{ value: dname(sc.display_y), angle: -90, position: 'insideLeft', fill: '#666', fontSize: 10 }} />
            <Tooltip content={({ active, payload }) => {
              if (!active || !payload?.length) return null
              const d = payload.find(p => p.name === 'data')?.payload
              if (!d) return null
              return (
                <div className="rounded-2xl p-3 shadow-2xl text-sm"
                  style={{ background: '#0e0e1a', border: '1px solid rgba(212,175,55,0.2)' }}>
                  <div className="flex justify-between gap-3 mb-1">
                    <span className="text-gray-400 text-xs">{dname(sc.display_x)}</span>
                    <span className="font-bold text-white">{fmt(d.x)}</span>
                  </div>
                  <div className="flex justify-between gap-3">
                    <span className="text-gray-400 text-xs">{dname(sc.display_y)}</span>
                    <span className="font-bold text-white">{fmt(d.y)}</span>
                  </div>
                </div>
              )
            }} />
            <Scatter name="data" data={data} fill={C.gold} opacity={0.5} />
            {trendLine.length === 2 && (
              <Line name="trend" data={trendLine} dataKey="trend" type="linear"
                stroke={rAbs > 0.5 ? C.emerald : C.gray} strokeWidth={2}
                dot={false} strokeDasharray={rAbs > 0.5 ? undefined : '5 3'} />
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </div>
      <p className="text-[10px] text-gray-600 mt-2 text-center">
        Dashed/gray line = weak trend line. Points clustered around it = stronger relationship.
      </p>
    </ChartCard>
  )
}

// ─── CHART 8: Correlation Rankings ────────────────────────────────────────────
function CorrelationRankingChart({ corrMatrix }: { corrMatrix: any }) {
  const [minR, setMinR] = useState(0.2)

  const pairs = useMemo(() => {
    const cells = corrMatrix?.cells || []
    const seen  = new Set<string>()
    return cells
      .filter((c: any) => c.x !== c.y && Math.abs(c.value) >= minR)
      .reduce((acc: any[], c: any) => {
        const key = [c.x, c.y].sort().join('||')
        if (!seen.has(key)) { seen.add(key); acc.push(c) }
        return acc
      }, [])
      .sort((a: any, b: any) => Math.abs(b.value) - Math.abs(a.value))
      .slice(0, 14)
      .map((c: any) => ({
        pair:    `${dname(c.x)} ↔ ${dname(c.y)}`,
        value:   c.value,
        abs:     Math.abs(c.value),
        label:   Math.abs(c.value) > 0.7 ? 'Strong' : Math.abs(c.value) > 0.4 ? 'Moderate' : 'Weak',
      }))
  }, [corrMatrix, minR])

  if (!pairs.length) return null

  const strong = pairs.filter(p => p.abs >= 0.7).length

  return (
    <ChartCard
      title="Which Metrics Influence Each Other?"
      question="What drives what? Find hidden dependencies and leverage points."
      badge="Correlation"
      icon={Layers}
      iconColor={C.teal}
      insight={strong > 0
        ? `${strong} strong link${strong > 1 ? 's' : ''} found (|r| ≥ 0.7). Strongest: "${pairs[0]?.pair}" at r = ${pairs[0]?.value?.toFixed(2)}. `
          + `These are LEVERAGE POINTS — improving one metric will likely lift the other. Prioritize these for maximum ROI.`
        : `No strong correlations above 0.7. All metrics are mostly independent. `
          + `Try lowering the filter threshold to see weaker connections.`}
      insightType={strong > 0 ? 'positive' : 'neutral'}
      controls={
        <Sel value={String(minR)} onChange={v => setMinR(Number(v))}
          options={[
            { v: '0.1', l: 'Show All (r≥0.1)' },
            { v: '0.2', l: 'Weak+ (r≥0.2)' },
            { v: '0.4', l: 'Moderate+ (r≥0.4)' },
            { v: '0.7', l: 'Strong Only (r≥0.7)' },
          ]} label="Filter" />
      }
    >
      <div style={{ height: Math.max(160, pairs.length * 28 + 20) }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={pairs} layout="vertical"
            margin={{ left: 10, right: 55, top: 5, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={GRID_STROKE} horizontal={false} />
            <XAxis type="number" domain={[-1, 1]} stroke={AXIS_STROKE} tick={AXIS_TICK_SM} />
            <YAxis type="category" dataKey="pair" stroke={AXIS_STROKE}
              tick={AXIS_TICK_SM} width={165} />
            <Tooltip content={({ active, payload, label }) => {
              if (!active || !payload?.length) return null
              const v = Number(payload[0]?.value ?? 0)
              const a = Math.abs(v)
              return (
                <div className="rounded-2xl p-4 shadow-2xl text-sm"
                  style={{ background: '#0e0e1a', border: '1px solid rgba(212,175,55,0.2)' }}>
                  <p className="font-bold text-white text-xs mb-2">{label}</p>
                  <p className="text-xs mb-1" style={{ color: v >= 0 ? C.teal : C.coral }}>
                    r = {v.toFixed(3)} · {a > 0.7 ? 'Strong' : a > 0.4 ? 'Moderate' : 'Weak'} {v > 0 ? 'positive' : 'negative'}
                  </p>
                  <p className="text-[10px] text-gray-500">
                    {a > 0.7 ? '✅ Reliable leverage point for strategy'
                      : a > 0.4 ? '⚠️ Some connection — investigate further'
                      : '➡️ Weak link — likely independent'}
                  </p>
                </div>
              )
            }} />
            <ReferenceLine x={0}    stroke="rgba(255,255,255,0.12)" />
            <ReferenceLine x={0.7}  stroke={`${C.emerald}35`} strokeDasharray="4 2"
              label={{ value: 'Strong', position: 'top', fill: C.emerald, fontSize: 8 }} />
            <ReferenceLine x={-0.7} stroke={`${C.coral}35`} strokeDasharray="4 2" />
            <Bar dataKey="value" name="r" radius={[0, 4, 4, 0]} maxBarSize={16}>
              {pairs.map((d, i) => (
                <Cell key={i}
                  fill={d.value >= 0 ? C.teal : C.coral}
                  opacity={0.35 + d.abs * 0.65} />
              ))}
              <LabelList dataKey="value" position="right"
                formatter={(v: number) => v.toFixed(2)}
                style={{ fontSize: 9, fill: '#888' }} />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </ChartCard>
  )
}

// ─── CHART 9: Period Growth + Momentum ────────────────────────────────────────
function GrowthChart({ growth }: { growth: any[] }) {
  const [gIdx, setGIdx] = useState(0)
  const gr = growth[gIdx]
  if (!gr?.periods?.length) return null

  const data  = gr.periods.filter((p: any) =>
    p.growth_rate_pct !== null && p.growth_rate_pct !== undefined)
  const rates = data.map((d: any) => d.growth_rate_pct ?? 0)
  const avg   = rates.length ? rates.reduce((a: number, b: number) => a + b, 0) / rates.length : 0
  const pos   = rates.filter((r: number) => r > 0).length
  const last3 = rates.slice(-3)
  const momentum = last3.length
    ? last3.reduce((a: number, b: number) => a + b, 0) / last3.length
    : avg
  const accelerating = momentum > avg

  const gOpts = growth.slice(0, 5).map((g, i) => ({
    v: String(i), l: g.display_name || `Metric ${i + 1}`,
  }))

  return (
    <ChartCard
      title={`${gr.display_name} — Growth Momentum`}
      question="Is the growth rate speeding up or slowing down recently?"
      badge="Growth"
      icon={accelerating ? TrendingUp : TrendingDown}
      iconColor={accelerating ? C.emerald : C.coral}
      insight={`${pos} of ${rates.length} periods grew (${(pos / rates.length * 100).toFixed(0)}% hit rate). `
        + `Average period growth: ${avg.toFixed(1)}%. `
        + `Recent momentum (last 3 periods avg): ${momentum.toFixed(1)}% — `
        + (accelerating
          ? `ACCELERATING ↑ — growth is speeding up. Double down on current strategies.`
          : `DECELERATING ↓ — growth is slowing. Investigate what changed and course-correct.`
        )}
      insightType={accelerating ? 'positive' : 'warning'}
      controls={
        growth.length > 1 ? (
          <Sel value={String(gIdx)} onChange={v => setGIdx(Number(v))}
            options={gOpts} label="Metric" />
        ) : undefined
      }
    >
      <div className="flex gap-3 mb-4">
        <StatBadge label="Avg Growth" value={`${avg.toFixed(1)}%`}
          color={avg >= 0 ? C.emerald : C.coral} sub="per period" />
        <StatBadge label="Recent Trend" value={`${momentum.toFixed(1)}%`}
          color={accelerating ? C.emerald : C.coral}
          sub={accelerating ? '↑ accelerating' : '↓ decelerating'} />
        <StatBadge label="Positive Periods" value={`${pos}/${rates.length}`}
          color={pos > rates.length / 2 ? C.gold : C.amber}
          sub={`${(pos / rates.length * 100).toFixed(0)}% hit rate`} />
      </div>

      <div className="h-[230px]">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={GRID_STROKE} />
            <XAxis dataKey="period" stroke={AXIS_STROKE} tick={AXIS_TICK_SM}
              interval="preserveStartEnd" />
            <YAxis yAxisId="l" stroke={AXIS_STROKE} tick={AXIS_TICK} tickFormatter={v => fmt(v)} />
            <YAxis yAxisId="r" orientation="right" stroke={AXIS_STROKE}
              tick={AXIS_TICK_SM} tickFormatter={v => `${v}%`} />
            <Tooltip content={({ active, payload, label }) => {
              if (!active || !payload?.length) return null
              const gRate = payload.find(p => p.name === 'Growth %')?.value
              const val   = payload.find(p => p.name === 'Value')?.value
              return (
                <div className="rounded-2xl p-4 shadow-2xl text-sm"
                  style={{ background: '#0e0e1a', border: '1px solid rgba(212,175,55,0.2)' }}>
                  <p className="text-[#D4AF37] text-xs font-bold mb-2">{label}</p>
                  {val !== undefined && (
                    <div className="flex justify-between gap-3 mb-1">
                      <span className="text-gray-400 text-xs">Value</span>
                      <span className="font-bold text-white">{fmt(val as number)}</span>
                    </div>
                  )}
                  {gRate !== undefined && (
                    <div className="flex justify-between gap-3">
                      <span className="text-gray-400 text-xs">Period growth</span>
                      <span className="font-bold" style={{ color: Number(gRate) >= 0 ? C.emerald : C.coral }}>
                        {Number(gRate) > 0 ? '+' : ''}{Number(gRate).toFixed(1)}%
                      </span>
                    </div>
                  )}
                </div>
              )
            }} />
            <Legend wrapperStyle={{ fontSize: 10, color: '#888' }} />
            <Bar yAxisId="l" dataKey="value" name="Value"
              fill={`${C.blue}25`} radius={[3, 3, 0, 0]} maxBarSize={28} />
            <Line yAxisId="r" type="monotone" dataKey="growth_rate_pct" name="Growth %"
              stroke={accelerating ? C.emerald : C.coral}
              strokeWidth={2.5} dot={{ r: 3, fill: accelerating ? C.emerald : C.coral }}
              activeDot={{ r: 5 }} />
            <ReferenceLine yAxisId="r" y={0} stroke="rgba(255,255,255,0.15)" />
            <ReferenceLine yAxisId="r" y={avg} stroke={`${C.amber}50`} strokeDasharray="4 2"
              label={{ value: `Avg ${avg.toFixed(1)}%`, position: 'right', fill: C.amber, fontSize: 9 }} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </ChartCard>
  )
}

// ─── Main Orchestrator ────────────────────────────────────────────────────────
export function DynamicChartSuite({ analytics }: { analytics: any }) {
  const [section, setSection] = useState('all')

  if (!analytics) {
    return (
      <div className="job-card p-12 text-center">
        <BarChart3 className="w-10 h-10 mx-auto mb-4 text-gray-700" />
        <h3 className="text-gray-400 font-semibold mb-1">Charts Loading…</h3>
        <p className="text-gray-600 text-sm">Complete the analysis pipeline first.</p>
      </div>
    )
  }

  const kpis    = analytics.kpis          || []
  const ts      = analytics.time_series   || []
  const dists   = analytics.distributions || []
  const segs    = analytics.segments      || []
  const scat    = analytics.scatter       || []
  const corr    = analytics.correlation_matrix || {}
  const pctCh   = analytics.percentage_changes || []
  const comp    = analytics.composition   || []
  const growth  = analytics.growth_rates  || []

  const avail = {
    kpi:    kpis.length >= 1,
    trend:  ts.length > 0 && ts[0]?.data?.length > 2,
    rank:   segs.length > 0,
    vsAvg:  pctCh.some((x: any) => x.type === 'vs_average') || segs.length > 0,
    scat:   scat.length > 0,
    dist:   dists.some((d: any) => {
      const s = d.stats
      if (!s) return false
      return Math.abs(s.std / (s.mean || 1)) * 100 > 1
    }),
    comp:   comp.length > 0,
    corr:   (corr?.cells?.length || 0) > 2,
    growth: growth.length > 0 && growth[0]?.periods?.length > 2,
  }

  const SECTIONS = [
    { key: 'all',      label: '✦ All' },
    { key: 'kpi',      label: '📊 KPIs',         show: avail.kpi },
    { key: 'ranking',  label: '🏆 Rankings',      show: avail.rank },
    { key: 'trend',    label: '📈 Trends',        show: avail.trend || avail.growth },
    { key: 'compare',  label: '↔ Compare',        show: avail.vsAvg || avail.scat },
    { key: 'dist',     label: '📉 Distributions', show: avail.dist || avail.comp },
    { key: 'relate',   label: '🔗 Relationships', show: avail.corr },
  ].filter(s => s.key === 'all' || s.show)

  const show = (keys: string[]) => section === 'all' || keys.includes(section)

  // Summary stats for top bar
  const totalCharts = Object.values(avail).filter(Boolean).length

  return (
    <div>
      {/* Section nav */}
      <div className="flex items-center gap-2 mb-5 flex-wrap">
        <SlidersHorizontal className="w-3.5 h-3.5 text-gray-600 shrink-0" />
        {SECTIONS.map(s => (
          <button key={s.key} onClick={() => setSection(s.key)}
            className="filter-pill text-xs transition-all"
            style={section === s.key ? {
              background: 'rgba(212,175,55,0.15)',
              border: '1px solid rgba(212,175,55,0.35)',
              color: C.gold,
            } : {}}>
            {s.label}
          </button>
        ))}
        <span className="ml-auto text-xs text-gray-600">{totalCharts} chart types available</span>
      </div>

      {/* Chart grid — deduplication: each type rendered ONCE per section */}
      <div className="grid grid-cols-1 2xl:grid-cols-2 gap-5">

        {/* KPI Dashboard — always full width */}
        {show(['kpi', 'all']) && avail.kpi && (
          <div className="col-span-full">
            <KpiDashboard kpis={kpis} />
          </div>
        )}

        {/* Trend — full width */}
        {show(['trend', 'all']) && avail.trend && (
          <div className="col-span-full">
            <TrendChart timeSeries={ts} />
          </div>
        )}

        {/* Leaderboard */}
        {show(['ranking', 'all']) && avail.rank && (
          <LeaderboardChart segments={segs} />
        )}

        {/* vs Average */}
        {show(['compare', 'ranking', 'all']) && avail.vsAvg && (
          <SegmentVsAvgChart pctChanges={pctCh} segments={segs} />
        )}

        {/* X vs Y */}
        {show(['compare', 'relate', 'all']) && avail.scat && (
          <XvsYChart scatter={scat} />
        )}

        {/* Correlation */}
        {show(['relate', 'compare', 'all']) && avail.corr && (
          <CorrelationRankingChart corrMatrix={corr} />
        )}

        {/* Distribution */}
        {show(['dist', 'all']) && avail.dist && (
          <DistributionChart distributions={dists} />
        )}

        {/* Composition */}
        {show(['dist', 'ranking', 'all']) && avail.comp && (
          <CompositionChart composition={comp} />
        )}

        {/* Growth */}
        {show(['trend', 'all']) && avail.growth && (
          <GrowthChart growth={growth} />
        )}
      </div>
    </div>
  )
}
