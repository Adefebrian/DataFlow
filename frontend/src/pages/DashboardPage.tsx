import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import {
  CheckCircle, Loader2, Clock, XCircle, Database,
  ArrowRight, Upload, BarChart3, TrendingUp, Zap,
} from 'lucide-react'

const API_BASE = 'http://localhost:8000'

function StatusBadge({ status }: { status: string }) {
  const cfg: Record<string, { cls: string; icon: any }> = {
    PENDING:  { cls: 'badge-yellow', icon: Clock },
    RUNNING:  { cls: 'badge-blue',   icon: Loader2 },
    COMPLETE: { cls: 'badge-green',  icon: CheckCircle },
    FAILED:   { cls: 'badge-red',    icon: XCircle },
  }
  const { cls, icon: Icon } = cfg[status] || cfg.PENDING
  return (
    <span className={`badge ${cls}`}>
      <Icon className={`w-3 h-3 ${status === 'RUNNING' ? 'animate-spin' : ''}`} />
      {status}
    </span>
  )
}

function formatDate(iso?: string) {
  if (!iso) return ''
  try {
    return new Date(iso).toLocaleString(undefined, {
      month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
    })
  } catch { return '' }
}

export function DashboardPage() {
  const { apiKey } = useAuth()

  const { data: jobs, isLoading } = useQuery({
    queryKey: ['jobs', apiKey],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/pipeline/all`, {
        headers: { 'X-API-Key': apiKey! },
      })
      if (!res.ok) return []
      return res.json()
    },
    enabled: !!apiKey,
    refetchInterval: 4000,
  })

  const stats = {
    total:    jobs?.length || 0,
    complete: jobs?.filter((j: any) => j.status === 'COMPLETE').length || 0,
    running:  jobs?.filter((j: any) => j.status === 'RUNNING').length  || 0,
    failed:   jobs?.filter((j: any) => j.status === 'FAILED').length   || 0,
  }

  return (
    <div className="fade-in">

      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white mb-1">Dashboard</h1>
          <p className="text-gray-500 text-sm">Monitor your analysis pipelines</p>
        </div>
        <Link to="/app" className="btn-gold inline-flex items-center gap-2 text-sm px-5 py-2.5">
          <Upload className="w-4 h-4" /> New Analysis
        </Link>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {[
          { label: 'Total Jobs', value: stats.total,    icon: Database,    color: '#D4AF37' },
          { label: 'Completed',  value: stats.complete, icon: CheckCircle, color: '#2ECC71' },
          { label: 'Running',    value: stats.running,  icon: Loader2,     color: '#3498DB', spin: true },
          { label: 'Failed',     value: stats.failed,   icon: XCircle,     color: '#FF6B6B' },
        ].map(s => (
          <div key={s.label} className="stat-card">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl flex items-center justify-center shrink-0"
                style={{ background: `${s.color}15` }}>
                <s.icon
                  className={`w-5 h-5 ${s.spin && s.value > 0 ? 'animate-spin' : ''}`}
                  style={{ color: s.color }}
                />
              </div>
              <div>
                <p className="text-gray-500 text-xs mb-0.5">{s.label}</p>
                <p className="text-2xl font-bold text-white">{s.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Jobs table */}
      <div className="job-card overflow-hidden">
        {/* Table header */}
        <div className="px-5 py-4 section-divider flex items-center justify-between">
          <h2 className="font-semibold text-white text-sm">Recent Jobs</h2>
          {stats.running > 0 && (
            <span className="flex items-center gap-1.5 text-xs text-blue-400">
              <Loader2 className="w-3 h-3 animate-spin" />
              {stats.running} running
            </span>
          )}
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="w-6 h-6 text-[#D4AF37] animate-spin" />
          </div>
        ) : !jobs?.length ? (
          <div className="text-center py-16 px-4">
            <div className="w-14 h-14 rounded-2xl flex items-center justify-center mx-auto mb-4"
              style={{ background: 'rgba(212,175,55,0.06)', border: '1px solid rgba(212,175,55,0.12)' }}>
              <Database className="w-7 h-7 text-[#D4AF37]/40" />
            </div>
            <h3 className="text-white font-medium mb-1">No analyses yet</h3>
            <p className="text-gray-500 text-sm mb-5">Upload a CSV to run your first AI-powered analysis</p>
            <Link to="/app" className="btn-gold inline-flex items-center gap-2 text-sm">
              <Upload className="w-4 h-4" /> Upload Data
            </Link>
          </div>
        ) : (
          <div>
            {jobs.map((job: any, i: number) => (
              <Link
                key={job.job_id}
                to={`/jobs/${job.job_id}`}
                className="flex items-center justify-between px-5 py-4 transition-all group"
                style={{
                  borderTop: i > 0 ? '1px solid rgba(212,175,55,0.05)' : 'none',
                  background: 'transparent',
                }}
                onMouseEnter={e => (e.currentTarget.style.background = 'rgba(212,175,55,0.03)')}
                onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
              >
                <div className="flex items-center gap-4 min-w-0">
                  <div className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0"
                    style={{ background: 'rgba(212,175,55,0.06)', border: '1px solid rgba(212,175,55,0.1)' }}>
                    <BarChart3 className="w-5 h-5 text-[#D4AF37]/40 group-hover:text-[#D4AF37] transition-colors" />
                  </div>
                  <div className="min-w-0">
                    <p className="font-medium text-white text-sm truncate">
                      {job.dataset_id || job.file_path?.split('/').pop() || 'Dataset'}
                    </p>
                    <p className="text-gray-600 text-xs font-mono mt-0.5 truncate">
                      {job.job_id?.slice(0, 20)}…
                    </p>
                    {job.created_at && (
                      <p className="text-gray-700 text-xs mt-0.5">{formatDate(job.created_at)}</p>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-3 shrink-0 ml-4">
                  <StatusBadge status={job.status} />
                  <ArrowRight className="w-4 h-4 text-gray-700 group-hover:text-[#D4AF37] group-hover:translate-x-0.5 transition-all" />
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* Tips */}
      {(jobs?.length ?? 0) > 0 && (
        <div className="mt-5 grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { icon: BarChart3,  color: '#D4AF37', title: 'Charts Tab',    desc: 'Filter by type — zoom any chart for full detail.' },
            { icon: TrendingUp, color: '#00CED1', title: 'Analytics Tab', desc: 'Interactive charts with drill-down and segment filters.' },
            { icon: Zap,        color: '#2ECC71', title: 'Insights Tab',  desc: 'AI findings filtered by category and impact level.' },
          ].map(t => (
            <div key={t.title} className="job-card p-4 flex items-start gap-3">
              <div className="w-8 h-8 rounded-xl flex items-center justify-center shrink-0"
                style={{ background: `${t.color}12` }}>
                <t.icon className="w-4 h-4" style={{ color: t.color }} />
              </div>
              <div>
                <p className="text-white text-xs font-semibold mb-0.5">{t.title}</p>
                <p className="text-gray-500 text-xs leading-relaxed">{t.desc}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
