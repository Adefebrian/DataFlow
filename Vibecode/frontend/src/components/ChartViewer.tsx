import { useState, useCallback } from 'react'
import {
  BarChart3, X, ZoomIn, Sparkles, Filter,
  TrendingUp, Activity, PieChart, GitBranch,
  BarChart2, Layers, LayoutGrid,
} from 'lucide-react'

type Chart = {
  type?: string
  title?: string
  subtitle?: string
  image_base64?: string
  summary?: string
  business_insight?: string
  severity?: string
}

type Props = {
  charts: Chart[]
  showFilterBar?: boolean
  gridCols?: 1 | 2
}

const TYPE_ICON: Record<string, any> = {
  distribution:        Activity,
  correlation:         Layers,
  scatter:             GitBranch,
  scatter_matrix:      LayoutGrid,
  category:            PieChart,
  revenue_analysis:    TrendingUp,
  segment_performance: BarChart3,
  performance_comparison: BarChart3,
  rate_analysis:       BarChart2,
  executive_dashboard: BarChart3,
  default:             BarChart3,
}

const TYPE_COLOR: Record<string, string> = {
  distribution:        '#9B59B6',
  correlation:         '#00CED1',
  scatter:             '#D4AF37',
  scatter_matrix:      '#D4AF37',
  category:            '#FF6B6B',
  revenue_analysis:    '#2ECC71',
  segment_performance: '#F39C12',
  executive_dashboard: '#D4AF37',
  default:             '#888',
}

function ZoomModal({ chart, onClose }: { chart: Chart; onClose: () => void }) {
  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4" onClick={onClose}>
      <div className="absolute inset-0" style={{ background: 'rgba(8,8,16,0.85)', backdropFilter: 'blur(8px)' }} />
      <div
        className="relative z-10 max-w-6xl w-full job-card overflow-hidden shadow-2xl fade-in"
        onClick={e => e.stopPropagation()}
      >
        <div className="px-5 py-4 section-divider flex items-center justify-between">
          <div>
            <h3 className="font-bold text-white">{chart.title}</h3>
            {chart.subtitle && <p className="text-gray-500 text-sm mt-0.5">{chart.subtitle}</p>}
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl transition-colors text-gray-500 hover:text-white"
            style={{ background: 'rgba(255,255,255,0.04)' }}
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="p-5">
          <img
            src={`data:image/png;base64,${chart.image_base64}`}
            alt={chart.title}
            className="w-full rounded-xl"
          />
          {chart.summary && (
            <div className="mt-4 p-4 rounded-xl text-sm text-gray-400 whitespace-pre-line leading-relaxed"
              style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(212,175,55,0.06)' }}>
              {chart.summary}
            </div>
          )}
          {chart.business_insight && (
            <div className="mt-3 flex items-start gap-2 p-3 rounded-xl text-sm text-[#D4AF37] leading-relaxed"
              style={{ background: 'rgba(212,175,55,0.06)', border: '1px solid rgba(212,175,55,0.12)' }}>
              <Sparkles className="w-3.5 h-3.5 mt-0.5 shrink-0" />
              {chart.business_insight}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function ChartCard({ chart, isWide, onZoom }: { chart: Chart; isWide?: boolean; onZoom: () => void }) {
  const [imgLoaded, setImgLoaded] = useState(false)
  const typeKey = chart.type || 'default'
  const Icon    = TYPE_ICON[typeKey]  || TYPE_ICON.default
  const color   = TYPE_COLOR[typeKey] || TYPE_COLOR.default

  return (
    <div className={`job-card overflow-hidden chart-enter group ${isWide ? 'col-span-full' : ''}`}>
      {/* Header */}
      <div className="px-5 py-4 section-divider flex items-start justify-between gap-3">
        <div className="flex items-start gap-3 min-w-0">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 mt-0.5"
            style={{ background: `${color}15` }}>
            <Icon className="w-4 h-4" style={{ color }} />
          </div>
          <div className="min-w-0">
            <h3 className="font-bold text-white text-sm leading-tight">{chart.title || 'Chart'}</h3>
            {chart.subtitle && (
              <p className="text-gray-600 text-xs mt-0.5 truncate">{chart.subtitle}</p>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          {chart.type && (
            <span className="text-[10px] uppercase tracking-wider px-2 py-1 rounded-lg font-medium"
              style={{ color, background: `${color}12` }}>
              {chart.type.replace(/_/g, ' ')}
            </span>
          )}
          <button
            onClick={onZoom}
            className="p-1.5 rounded-lg text-gray-600 hover:text-white transition-all opacity-0 group-hover:opacity-100"
            style={{ background: 'rgba(255,255,255,0.04)' }}
            title="Expand"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Image */}
      <div className="p-5">
        {!imgLoaded && (
          <div className="h-60 rounded-xl" style={{ background: 'rgba(255,255,255,0.03)', animation: 'pulse 1.5s ease-in-out infinite' }} />
        )}
        <img
          src={`data:image/png;base64,${chart.image_base64}`}
          alt={chart.title}
          className={`w-full rounded-xl cursor-zoom-in hover:opacity-95 transition-opacity ${imgLoaded ? '' : 'hidden'}`}
          style={{ border: '1px solid rgba(212,175,55,0.08)' }}
          loading="lazy"
          onLoad={() => setImgLoaded(true)}
          onClick={onZoom}
        />

        {/* Summary */}
        {chart.summary && (
          <div className="mt-4 p-4 rounded-xl text-sm text-gray-400 whitespace-pre-line leading-relaxed"
            style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(212,175,55,0.05)' }}>
            {chart.summary}
          </div>
        )}

        {/* Business insight */}
        {chart.business_insight && (
          <div className="mt-3 flex items-start gap-2 p-3 rounded-xl text-sm text-[#D4AF37] leading-relaxed"
            style={{ background: 'rgba(212,175,55,0.06)', border: '1px solid rgba(212,175,55,0.1)' }}>
            <Sparkles className="w-3.5 h-3.5 mt-0.5 shrink-0" />
            {chart.business_insight}
          </div>
        )}
      </div>
    </div>
  )
}

export function ChartViewer({ charts, showFilterBar = true, gridCols = 2 }: Props) {
  const [filter,    setFilter]    = useState('All')
  const [zoomChart, setZoomChart] = useState<Chart | null>(null)

  // Accept all charts that have valid base64 image data
  const visibleCharts = charts.filter(c =>
    c && c.image_base64 && c.image_base64.length > 100 &&
    c.type !== 'skipped' && c.type !== 'error' && c.type !== 'empty'
  )

  const typeList = ['All', ...Array.from(new Set(visibleCharts.map(c => c.type || 'chart')))]

  const filtered = filter === 'All'
    ? visibleCharts
    : visibleCharts.filter(c => (c.type || 'chart') === filter)

  const handleZoom  = useCallback((chart: Chart) => setZoomChart(chart), [])
  const handleClose = useCallback(() => setZoomChart(null), [])

  if (visibleCharts.length === 0) {
    return (
      <div className="job-card p-12 text-center">
        <BarChart3 className="w-12 h-12 mx-auto mb-4 text-gray-700" />
        <h3 className="text-gray-400 font-medium mb-1">No Visualizations Available</h3>
        <p className="text-gray-600 text-sm max-w-sm mx-auto">
          Charts are generated from your data. Make sure your CSV has numeric columns with meaningful values.
        </p>
      </div>
    )
  }

  return (
    <>
      {zoomChart && <ZoomModal chart={zoomChart} onClose={handleClose} />}

      {/* Filter bar */}
      {showFilterBar && typeList.length > 2 && (
        <div className="flex items-center gap-2 flex-wrap mb-4">
          <Filter className="w-3.5 h-3.5 text-gray-600 shrink-0" />
          {typeList.map(t => (
            <button key={t} onClick={() => setFilter(t)}
              className={`filter-pill ${filter === t ? 'active' : ''}`}>
              {t.replace(/_/g, ' ')}
            </button>
          ))}
          <span className="text-xs text-gray-700 ml-auto">
            {filtered.length} / {visibleCharts.length}
          </span>
        </div>
      )}

      {/* Grid */}
      <div className={`grid grid-cols-1 ${gridCols === 2 ? '2xl:grid-cols-2' : ''} gap-5`}>
        {filtered.map((chart, i) => (
          <ChartCard
            key={i}
            chart={chart}
            isWide={i === 0 && gridCols === 2}
            onZoom={() => handleZoom(chart)}
          />
        ))}
      </div>
    </>
  )
}
