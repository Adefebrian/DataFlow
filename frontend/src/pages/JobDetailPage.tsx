import { useEffect, useState, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { useDashboard } from '../hooks/useDashboard'
import { CurrencyProvider, useCurrency, CURRENCIES } from '../hooks/useCurrency'
import {
  ArrowLeft, Loader2, CheckCircle, XCircle, FileText,
  Sparkles, BarChart3, TrendingUp, Zap, Target, AlertTriangle,
  Activity, LayoutDashboard, BookOpen, ChevronRight, DollarSign,
  Download, Pin, BarChart2,
} from 'lucide-react'
import { VisualizationsTab } from '../components/VisualizationsTab'
import { ReportTab }         from '../components/ReportTab'

// Re-export for any component that needs it
export { useCurrency } from '../hooks/useCurrency'

const API_BASE = 'http://localhost:8000'

// ─── Currency Switcher ───────────────────────────────────────────────────────
function CurrencySwitcher() {
  const { currency, setCurrency } = useCurrency()
  const [open, setOpen] = useState(false)
  const current = CURRENCIES.find(c => c.code === currency)!
  return (
    <div className="relative">
      <button
        onClick={() => setOpen(v => !v)}
        className="flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-semibold transition-all"
        style={{ background: 'rgba(212,175,55,0.1)', border: '1px solid rgba(212,175,55,0.2)', color: 'var(--gold)' }}>
        <DollarSign className="w-3.5 h-3.5" />
        <span>{current.symbol} {current.code}</span>
        <svg className={`w-3 h-3 transition-transform ${open ? 'rotate-180' : ''}`} viewBox="0 0 12 12" fill="none">
          <path d="M2 4l4 4 4-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </button>
      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <div className="absolute right-0 top-full mt-2 z-50 w-52 rounded-2xl overflow-hidden shadow-2xl"
            style={{ background: 'var(--tooltip-bg)', border: '1px solid var(--border-mid)' }}>
            <div className="px-3 py-2" style={{ borderBottom: '1px solid var(--border-soft)' }}>
              <p className="text-[10px] uppercase tracking-widest font-medium" style={{ color: 'var(--text-muted)' }}>
                Currency
              </p>
            </div>
            {CURRENCIES.map(c => (
              <button
                key={c.code}
                onClick={() => { setCurrency(c.code); setOpen(false) }}
                className="w-full flex items-center justify-between px-3 py-2.5 text-sm transition-all hover:bg-white/3"
                style={currency === c.code
                  ? { background: 'rgba(212,175,55,0.12)', color: 'var(--gold)' }
                  : { color: 'var(--text-secondary)' }}>
                <span className="flex items-center gap-2.5">
                  <span className="w-8 text-right font-mono text-xs font-bold opacity-80">{c.symbol}</span>
                  <span>{c.label}</span>
                </span>
                <span className="text-xs font-mono opacity-50">{c.code}</span>
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  )
}

// ─── Constants ────────────────────────────────────────────────────────────────
const STAGES = [
  { key: 'profile',       label: 'Profile',   icon: FileText },
  { key: 'statistics',    label: 'Stats',     icon: Activity },
  { key: 'clean',         label: 'Clean',     icon: Sparkles },
  { key: 'charts',        label: 'Charts',    icon: BarChart3 },
  { key: 'analytics',     label: 'Analytics', icon: TrendingUp },
  { key: 'comprehensive', label: 'Deep',      icon: BarChart2 },
  { key: 'insights',      label: 'Insights',  icon: Target },
  { key: 'report',        label: 'Report',    icon: BookOpen },
]

const TABS = [
  { key: 'overview',       label: 'Overview',       icon: LayoutDashboard },
  { key: 'visualizations', label: 'Visualizations', icon: BarChart3 },
  { key: 'insights',       label: 'Insights',       icon: Sparkles },
  { key: 'report',         label: 'Report',         icon: BookOpen },
]

const IMPACT_STYLE: Record<string, string> = {
  critical: 'insight-critical', high: 'insight-high',
  medium:   'insight-medium',   low:  'insight-low',
}
const IMPACT_BADGE: Record<string, string> = {
  critical: 'text-red-400 bg-red-400/10',
  high:     'text-[#D4AF37] bg-[#D4AF37]/10',
  medium:   'text-blue-400 bg-blue-400/10',
  low:      'text-gray-500 bg-white/4',
}

function InsightIcon({ type }: { type: string }) {
  const map: Record<string, any> = {
    summary: Target, correlation: TrendingUp, anomaly: AlertTriangle,
    action: Zap, revenue_snapshot: BarChart3, strong_correlations: TrendingUp,
    segment_comparison: LayoutDashboard, next_steps: CheckCircle,
  }
  const Icon = map[type] || Sparkles
  return <Icon className="w-4 h-4" />
}

// ─── Stage Pipeline ───────────────────────────────────────────────────────────
function StagePipeline({ stages }: { stages: any[] }) {
  return (
    <div className="flex items-center gap-1 overflow-x-auto pb-1">
      {STAGES.map((stage, i) => {
        const sd     = stages.find((s: any) => s.stage_name === stage.key)
        const status = sd?.status || 'PENDING'
        const Icon   = stage.icon
        return (
          <div key={stage.key} className="flex items-center shrink-0">
            <div className="flex flex-col items-center gap-1">
              <div className={`w-8 h-8 rounded-xl flex items-center justify-center transition-all duration-300 ${
                status === 'COMPLETE' ? 'bg-emerald-500/12'
                : status === 'FAILED'  ? 'bg-red-500/12'
                : status === 'RUNNING' ? 'bg-[#D4AF37]/15 animate-pulse'
                : 'bg-white/3'
              }`} style={{
                border: status === 'COMPLETE' ? '1px solid rgba(52,211,153,0.2)'
                  : status === 'FAILED'  ? '1px solid rgba(248,113,113,0.2)'
                  : status === 'RUNNING' ? '1px solid rgba(212,175,55,0.3)'
                  : '1px solid rgba(255,255,255,0.05)',
              }}>
                {status === 'COMPLETE' ? <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
                  : status === 'FAILED'  ? <XCircle    className="w-3.5 h-3.5 text-red-400" />
                  : status === 'RUNNING' ? <Loader2    className="w-3.5 h-3.5 text-[#D4AF37] animate-spin" />
                  : <Icon className="w-3.5 h-3.5 text-gray-700" />}
              </div>
              <span className="text-[9px] font-medium" style={{
                color: status === 'COMPLETE' ? 'rgba(52,211,153,0.6)'
                  : status === 'RUNNING' ? 'rgba(212,175,55,0.6)' : 'rgba(255,255,255,0.2)',
              }}>
                {stage.label}
              </span>
            </div>
            {i < STAGES.length - 1 && (
              <div className="w-5 h-px mx-1 mb-4 transition-all duration-500" style={{
                background: stages.find((s: any) => s.stage_name === STAGES[i + 1]?.key)?.status === 'COMPLETE'
                  ? 'rgba(52,211,153,0.2)' : 'rgba(255,255,255,0.05)',
              }} />
            )}
          </div>
        )
      })}
    </div>
  )
}

// ─── Helpers ─────────────────────────────────────────────────────────────────
function parseOutput(raw: any): any {
  if (!raw) return null
  if (typeof raw === 'object') return raw
  if (typeof raw === 'string') { try { return JSON.parse(raw) } catch { return null } }
  return null
}

function extractCharts(cs: any): { all: any[]; dashboard: any[] } {
  if (!cs) return { all: [], dashboard: [] }
  let all: any[] = [], dashboard: any[] = []
  if (Array.isArray(cs))    { all = cs }
  else if (cs.charts)       { all = cs.charts; dashboard = cs.dashboard || [] }
  return {
    all:       all.filter(c => c?.image_base64 && c.image_base64.length > 100),
    dashboard: dashboard.filter(c => c?.image_base64),
  }
}

function exportToPDF(jobName: string, reportHtml: string | null, charts: any[]) {
  const html = reportHtml || `<!DOCTYPE html><html><head><title>${jobName}</title>
    <style>body{font-family:system-ui,sans-serif;padding:20px}h1{color:#996515}
    img{width:100%;margin-bottom:16px;border-radius:8px;break-inside:avoid}
    @media print{img{max-height:380px;object-fit:contain}}</style></head>
    <body><h1>${jobName} — Analysis Report</h1>
    ${charts.filter(c => c.image_base64).map(c => `
      <h3>${c.title || ''}</h3>
      <img src="data:image/png;base64,${c.image_base64}" />
    `).join('')}</body></html>`
  const win = window.open('', '_blank')
  if (!win) return
  win.document.write(html)
  win.document.close()
  setTimeout(() => win.print(), 500)
}

// ─── Inner page (inside CurrencyProvider) ────────────────────────────────────
function JobDetailInner() {
  const { jobId }                = useParams<{ jobId: string }>()
  const { apiKey }               = useAuth()
  const { addItem, hasItem }     = useDashboard()

  const [jobData,        setJobData]        = useState<any>(null)
  const [loading,        setLoading]        = useState(true)
  const [activeTab,      setActiveTab]      = useState('overview')
  const [analytics,      setAnalytics]      = useState<any>(null)
  const [insightFilter,  setInsightFilter]  = useState('All')

  // ⚠️ useCallback MUST be before any early returns (Rules of Hooks)
  const pinChart = useCallback((chart: any) => {
    if (!jobId) return
    addItem({
      jobId,
      jobName: jobData?.job?.dataset_id || 'Analysis',
      type: 'chart',
      subtype: chart.type || 'chart',
      title: chart.title || 'Chart',
      image_base64: chart.image_base64,
    })
  }, [jobId, jobData, addItem])

  useEffect(() => {
    if (!jobId || !apiKey) return

    let stopped = false
    let intervalId: ReturnType<typeof setInterval> | null = null
    let analyticsLoaded = false

    const poll = async () => {
      try {
        const res = await fetch(`${API_BASE}/pipeline/${jobId}/status`, {
          headers: { 'X-API-Key': apiKey },
        })
        if (!res.ok) return
        const data = await res.json()
        if (stopped) return
        setJobData(data)

        const status = data?.job?.status
        // Load analytics once when complete
        if (status === 'COMPLETE' && !analyticsLoaded) {
          analyticsLoaded = true
          try {
            const ar = await fetch(`${API_BASE}/pipeline/${jobId}/analytics`, {
              headers: { 'X-API-Key': apiKey },
            })
            if (ar.ok) {
              const ap = await ar.json()
              if (!stopped) setAnalytics(ap?.analytics || null)
            }
          } catch { /* analytics optional */ }
        }

        // Stop polling once terminal state reached
        if (status === 'COMPLETE' || status === 'FAILED') {
          if (intervalId) { clearInterval(intervalId); intervalId = null }
        }
      } catch { /* network error — keep polling */ }
      finally {
        if (!stopped) setLoading(false)
      }
    }

    poll()
    intervalId = setInterval(poll, 4000)

    return () => {
      stopped = true
      if (intervalId) clearInterval(intervalId)
    }
  }, [jobId, apiKey])

  if (loading) return (
    <div className="flex flex-col items-center justify-center py-24 gap-3">
      <Loader2 className="w-8 h-8 animate-spin" style={{ color: 'var(--gold)' }} />
      <p className="text-sm" style={{ color: 'var(--text-muted)' }}>Loading analysis…</p>
    </div>
  )

  if (!jobData?.job) return (
    <div className="text-center py-20">
      <p className="mb-4" style={{ color: 'var(--text-secondary)' }}>Job not found</p>
      <Link to="/jobs" className="btn-gold inline-flex items-center gap-2">Back to Dashboard</Link>
    </div>
  )

  const job    = jobData.job
  const stages = jobData.stages || []
  const stageMap: Record<string, any> = {}
  for (const s of stages) {
    const p = parseOutput(s.output)
    if (p !== null) stageMap[s.stage_name] = p
  }

  const profile       = stageMap['profile']
  const insights: any[] = stageMap['insights']?.insights || []
  const reportHtml    = stageMap['report']?.report_html   || null
  const reportSummary = stageMap['report']?.report_summary || null
  const { all: visibleCharts, dashboard: dashCharts } = extractCharts(stageMap['charts'])

  const insightCategories = ['All', ...Array.from(new Set(insights.map((i: any) => i.category || 'general')))]
  const filteredInsights  = insightFilter === 'All' ? insights : insights.filter((i: any) => i.category === insightFilter)

  const isComplete = job.status === 'COMPLETE'
  const isRunning  = job.status === 'RUNNING'
  const isFailed   = job.status === 'FAILED'
  const jobName    = job.dataset_id || 'Analysis'

  return (
    <div className="fade-in max-w-7xl mx-auto">
      {/* Back */}
      <Link to="/jobs"
        className="inline-flex items-center gap-2 mb-6 text-sm group transition-colors"
        style={{ color: 'var(--text-muted)' }}
        onMouseEnter={e => e.currentTarget.style.color = 'var(--gold)'}
        onMouseLeave={e => e.currentTarget.style.color = 'var(--text-muted)'}>
        <ArrowLeft className="w-4 h-4 group-hover:-translate-x-0.5 transition-transform" />
        Back to Dashboard
      </Link>

      {/* Job header */}
      <div className="job-card mb-5">
        <div className="p-6">
          <div className="flex items-start justify-between gap-4 mb-5">
            <div className="flex items-center gap-4">
              <div className="w-11 h-11 rounded-xl flex items-center justify-center shrink-0"
                style={{ background: 'rgba(212,175,55,0.08)', border: '1px solid rgba(212,175,55,0.15)' }}>
                <FileText className="w-5 h-5" style={{ color: 'var(--gold)' }} />
              </div>
              <div>
                <h1 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>{jobName}</h1>
                <p className="text-xs font-mono mt-0.5" style={{ color: 'var(--text-faint)' }}>{jobId}</p>
                {profile?.quality_score !== undefined && (
                  <div className="flex items-center gap-2 mt-1.5">
                    <div className="w-20 h-1 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.06)' }}>
                      <div className="h-full rounded-full bg-gradient-to-r from-[#D4AF37] to-emerald-400"
                        style={{ width: `${profile.quality_score}%` }} />
                    </div>
                    <span className="text-xs" style={{ color: 'var(--text-faint)' }}>{profile.quality_score}% quality</span>
                  </div>
                )}
              </div>
            </div>

            <div className="flex items-center gap-2 shrink-0 flex-wrap justify-end">
              <CurrencySwitcher />
              {isComplete && (
                <button
                  onClick={() => exportToPDF(jobName, reportHtml, visibleCharts)}
                  className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold transition-all"
                  style={{ background: 'rgba(46,204,113,0.1)', border: '1px solid rgba(46,204,113,0.2)', color: '#2ECC71' }}>
                  <Download className="w-3.5 h-3.5" /> Export PDF
                </button>
              )}
              <span className={`badge ${isComplete ? 'badge-green' : isFailed ? 'badge-red' : 'badge-blue'}`}>
                {isComplete ? <CheckCircle className="w-3 h-3" />
                  : isFailed ? <XCircle    className="w-3 h-3" />
                  : <Loader2 className="w-3 h-3 animate-spin" />}
                {job.status}
              </span>
            </div>
          </div>

          {/* Metrics */}
          {profile && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-5">
              {[
                { label: 'Records',      value: profile.row_count?.toLocaleString(), color: '#D4AF37' },
                { label: 'Features',     value: profile.column_count,               color: '#00CED1' },
                { label: 'Data Quality', value: `${profile.quality_score}%`,        color: profile.quality_score > 80 ? '#2ECC71' : '#F39C12' },
                { label: 'Completeness', value: `${profile.completeness}%`,         color: '#9B59B6' },
              ].map(m => (
                <div key={m.label} className="metric-tile">
                  <div className="text-2xl font-bold mb-0.5" style={{ color: m.color }}>{m.value}</div>
                  <div className="text-xs" style={{ color: 'var(--text-muted)' }}>{m.label}</div>
                </div>
              ))}
            </div>
          )}

          <StagePipeline stages={stages} />
        </div>
      </div>

      {/* Running */}
      {isRunning && (
        <div className="job-card p-12 text-center mb-5">
          <div className="relative inline-block mb-5">
            <Loader2 className="w-10 h-10 animate-spin" style={{ color: 'var(--gold)' }} />
            <div className="absolute inset-0 rounded-full border border-[#D4AF37]/15 animate-ping" />
          </div>
          <h3 className="font-semibold mb-1" style={{ color: 'var(--text-primary)' }}>Analysis in Progress</h3>
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
            Profiling data, detecting patterns, building visualizations…
          </p>
        </div>
      )}

      {/* Complete */}
      {isComplete && (
        <>
          {/* Tab bar */}
          <div className="flex items-center gap-1 mb-5 p-1 rounded-xl overflow-x-auto"
            style={{ background: 'var(--bg-input)', border: '1px solid var(--border-dim)' }}>
            {TABS.map(tab => (
              <button key={tab.key} onClick={() => setActiveTab(tab.key)}
                className="flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 whitespace-nowrap"
                style={activeTab === tab.key
                  ? { background: 'rgba(212,175,55,0.1)', border: '1px solid rgba(212,175,55,0.2)', color: 'var(--gold)' }
                  : { color: 'var(--text-muted)', border: '1px solid transparent' }}>
                <tab.icon className="w-4 h-4" />
                {tab.label}
                {tab.key === 'insights' && insights.length > 0 && (
                  <span className="text-xs px-1.5 py-0.5 rounded-md font-normal"
                    style={{ background: 'rgba(255,255,255,0.06)', color: 'var(--text-muted)' }}>
                    {insights.length}
                  </span>
                )}
              </button>
            ))}
          </div>

          {/* Overview */}
          {activeTab === 'overview' && (
            <div className="space-y-5 fade-in">
              <div className="job-card">
                <div className="px-5 py-4 section-divider flex items-center gap-3">
                  <div className="icon-pill gold"><Sparkles className="w-4 h-4" style={{ color: 'var(--gold)' }} /></div>
                  <div>
                    <h2 className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>Key Business Insights</h2>
                    <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{insights.length} insights generated</p>
                  </div>
                </div>
                <div className="p-5 space-y-3">
                  {insights.slice(0, 5).map((ins: any, i: number) => (
                    <div key={i} className={`p-4 ${IMPACT_STYLE[ins.impact] || 'insight-low'}`}>
                      <div className="flex items-start gap-3">
                        <span className="mt-0.5 shrink-0" style={{ color: 'var(--text-muted)' }}>
                          <InsightIcon type={ins.type} />
                        </span>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 flex-wrap mb-1">
                            <h4 className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>{ins.title}</h4>
                            <span className={`text-xs px-2 py-0.5 rounded-md font-medium ${IMPACT_BADGE[ins.impact] || IMPACT_BADGE.low}`}>
                              {ins.impact}
                            </span>
                          </div>
                          <p className="text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>{ins.description}</p>
                          {ins.action && (
                            <div className="mt-2.5 inline-flex items-center gap-1.5 text-xs rounded-lg px-3 py-1.5"
                              style={{ background: 'rgba(212,175,55,0.06)', border: '1px solid rgba(212,175,55,0.12)', color: 'var(--gold)' }}>
                              <Zap className="w-3 h-3 shrink-0" /> {ins.action}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                  {insights.length > 5 && (
                    <button
                      onClick={() => setActiveTab('insights')}
                      className="w-full text-center text-sm py-2 flex items-center justify-center gap-1 transition-colors"
                      style={{ color: 'var(--text-muted)' }}
                      onMouseEnter={e => e.currentTarget.style.color = 'var(--gold)'}
                      onMouseLeave={e => e.currentTarget.style.color = 'var(--text-muted)'}>
                      View all {insights.length} insights <ChevronRight className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>

              {/* Quick Analytics Preview — Recharts, no images */}
              {analytics && (
                <div className="job-card">
                  <div className="px-5 py-4 section-divider flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="icon-pill teal"><BarChart3 className="w-4 h-4" style={{ color: 'var(--teal)' }} /></div>
                      <div>
                        <h2 className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>Quick Analytics Preview</h2>
                        <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Interactive charts — click Visualizations for full view</p>
                      </div>
                    </div>
                    <button
                      onClick={() => setActiveTab('visualizations')}
                      className="text-xs flex items-center gap-1 transition-colors"
                      style={{ color: 'var(--text-muted)' }}
                      onMouseEnter={e => e.currentTarget.style.color = 'var(--gold)'}
                      onMouseLeave={e => e.currentTarget.style.color = 'var(--text-muted)'}>
                      Full dashboard <ChevronRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                  <div className="p-5">
                    <VisualizationsTab
                      charts={[]}
                      analytics={analytics}
                      jobId={jobId!}
                      jobName={jobName}
                      previewMode
                    />
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Visualizations — Recharts + matplotlib image charts */}
          {activeTab === 'visualizations' && (
            <div className="fade-in">
              <VisualizationsTab
                charts={visibleCharts}
                analytics={analytics}
                jobId={jobId!}
                jobName={jobName}
              />
            </div>
          )}

          {/* Insights */}
          {activeTab === 'insights' && (
            <div className="job-card fade-in">
              <div className="px-5 py-4 section-divider flex items-center justify-between gap-3 flex-wrap">
                <div className="flex items-center gap-3">
                  <div className="icon-pill gold"><Sparkles className="w-4 h-4" style={{ color: 'var(--gold)' }} /></div>
                  <div>
                    <h2 className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>All Insights</h2>
                    <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{insights.length} findings</p>
                  </div>
                </div>
                <div className="flex items-center gap-2 flex-wrap">
                  {insightCategories.map(c => (
                    <button key={c} onClick={() => setInsightFilter(c)}
                      className={`filter-pill ${insightFilter === c ? 'active' : ''}`}>
                      {c}
                    </button>
                  ))}
                </div>
              </div>
              <div className="p-5 space-y-3">
                {filteredInsights.map((ins: any, i: number) => (
                  <div key={i} className={`p-4 ${IMPACT_STYLE[ins.impact] || 'insight-low'}`}>
                    <div className="flex items-start gap-3">
                      <span className="mt-0.5 shrink-0" style={{ color: 'var(--text-muted)' }}>
                        <InsightIcon type={ins.type} />
                      </span>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap mb-1.5">
                          <h4 className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>{ins.title}</h4>
                          <span className={`text-xs px-2 py-0.5 rounded-md ${IMPACT_BADGE[ins.impact] || IMPACT_BADGE.low}`}>
                            {ins.impact}
                          </span>
                          <span className="text-xs" style={{ color: 'var(--text-faint)' }}>{ins.category}</span>
                          {ins.confidence !== undefined && (
                            <span className="text-xs ml-auto" style={{ color: 'var(--text-faint)' }}>
                              {ins.confidence}% confidence
                            </span>
                          )}
                        </div>
                        <p className="text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>{ins.description}</p>
                        {ins.action && (
                          <div className="mt-2.5 inline-flex items-center gap-1.5 text-xs rounded-lg px-3 py-1.5"
                            style={{ background: 'rgba(212,175,55,0.06)', border: '1px solid rgba(212,175,55,0.12)', color: 'var(--gold)' }}>
                            <Zap className="w-3 h-3 shrink-0" /> {ins.action}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Report */}
          {activeTab === 'report' && (
            <div className="fade-in">
              <ReportTab
                reportHtml={reportHtml}
                reportSummary={reportSummary}
                charts={visibleCharts}
                profile={profile}
                analytics={analytics}
                jobId={jobId!}
                jobName={jobName}
                onExportPDF={() => exportToPDF(jobName, reportHtml, visibleCharts)}
              />
            </div>
          )}
        </>
      )}

      {/* Failed */}
      {isFailed && (
        <div className="job-card p-10 text-center">
          <XCircle className="w-10 h-10 text-red-400 mx-auto mb-3" />
          <h3 className="font-semibold mb-1" style={{ color: 'var(--text-primary)' }}>Analysis Failed</h3>
          <p className="text-sm mb-4" style={{ color: 'var(--text-muted)' }}>An error occurred processing your dataset.</p>
          <Link to="/app" className="btn-gold inline-flex items-center gap-2">Try Again</Link>
        </div>
      )}
    </div>
  )
}

// ─── Root export (wrapped in CurrencyProvider) ─────────────────────────────
export function JobDetailPage() {
  return (
    <CurrencyProvider>
      <JobDetailInner />
    </CurrencyProvider>
  )
}
