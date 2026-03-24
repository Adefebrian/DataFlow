/**
 * ReportTab — Full interactive Recharts report (zero static images)
 * ✅ Executive Summary rendered as structured decision-making UI (no raw JSON)
 * ✅ ChartGrid replaced with VisualizationsTab (dynamic Recharts)
 * ✅ HTML preview still available via toggle
 * ✅ Dataset profile cards
 * ✅ PDF export
 */
import { useState } from 'react'
import {
  Download, FileText, BarChart3, Eye, ChevronDown,
  ChevronUp, Sparkles, Target, TrendingUp,
  CheckCircle, BookOpen, Zap, AlertTriangle,
  ArrowUpRight, Shield, Lightbulb, ListChecks,
  Info, BarChart2, Activity,
} from 'lucide-react'
import { VisualizationsTab } from './VisualizationsTab'

type Props = {
  reportHtml:    string | null
  reportSummary: string | null
  charts:        any[]
  profile:       any
  analytics:     any
  jobId:         string
  jobName:       string
  onExportPDF:   () => void
}

// ─── Parse reportSummary — handles JSON object, JSON string, or plain text ───
function parseSummary(raw: string | null): any {
  if (!raw) return null
  if (typeof raw === 'object') return raw
  const s = typeof raw === 'string' ? raw.trim() : ''
  // Try JSON parse
  try {
    const parsed = JSON.parse(s)
    if (typeof parsed === 'object' && parsed !== null) return parsed
    return { executive_summary: String(parsed) }
  } catch {
    // Not JSON — plain text
    return { executive_summary: s }
  }
}

// ─── Render a single text value — strip quotes/braces if leaked ──────────────
function clean(v: any): string {
  if (v == null) return ''
  const s = String(v)
  // Remove surrounding quotes that sometimes leak from JSON stringification
  return s.replace(/^["']|["']$/g, '').trim()
}

// ─── Executive Summary UI ────────────────────────────────────────────────────
function SummarySection({ text }: { text: string }) {
  const isHtml = typeof text === 'string' && text.trim().startsWith('<')

  // ── HTML mode (backend sent a full HTML document) ──
  if (isHtml) {
    return (
      <div className="job-card overflow-hidden">
        <div className="px-5 py-4 section-divider flex items-center gap-3">
          <div className="icon-pill gold">
            <FileText className="w-4 h-4" style={{ color: 'var(--gold)' }} />
          </div>
          <div>
            <h3 className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>Executive Summary</h3>
            <p className="text-xs" style={{ color: 'var(--text-muted)' }}>AI-generated analysis overview</p>
          </div>
        </div>
        <div className="p-1">
          <iframe
            srcDoc={text}
            className="w-full rounded-xl"
            style={{ height: '520px', border: 'none', background: '#080810' }}
            title="Executive Summary"
          />
        </div>
      </div>
    )
  }

  // ── Parse into structured object ──
  const data = parseSummary(text)
  if (!data) return null

  const execSummary     = clean(data.executive_summary  || data['Executive Summary']  || data.summary || '')
  const datasetOverview = clean(data.dataset_overview   || data['Dataset Overview']   || data.overview || '')
  const dataQuality     = clean(data.data_quality_report|| data['Data Quality Report']|| data.data_quality || '')
  const analysisScope   = clean(data.analysis_scope     || data['Analysis Scope']     || data.scope   || '')
  const limitations     = clean(data.analysis_limitations||data['Analysis Limitations']||data.limitations||'')

  // Key Findings — array or string
  const rawFindings = data.key_findings || data['Key Findings'] || data.findings || []
  const findings: string[] = Array.isArray(rawFindings)
    ? rawFindings.map((f: any) => clean(f))
    : typeof rawFindings === 'string' ? rawFindings.split('\n').filter(Boolean).map(clean) : []

  // Recommendations — array or string
  const rawRecs = data.recommendations || data['Recommendations'] || data.next_steps || []
  const recommendations: string[] = Array.isArray(rawRecs)
    ? rawRecs.map((r: any) => clean(r))
    : typeof rawRecs === 'string' ? rawRecs.split('\n').filter(Boolean).map(clean) : []

  // If we only have a plain summary string (nothing structured), render it nicely
  const isStructured = findings.length > 0 || recommendations.length > 0 || datasetOverview || dataQuality

  if (!isStructured && execSummary) {
    return <PlainSummary text={execSummary} />
  }

  return (
    <div className="space-y-4">
      {/* Header card */}
      <div className="job-card overflow-hidden">
        <div className="px-5 py-4 section-divider flex items-center gap-3">
          <div className="icon-pill gold">
            <FileText className="w-4 h-4" style={{ color: 'var(--gold)' }} />
          </div>
          <div>
            <h3 className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>Executive Summary</h3>
            <p className="text-xs" style={{ color: 'var(--text-muted)' }}>AI-generated strategic overview for decision-making</p>
          </div>
        </div>

        {/* Executive Summary text */}
        {execSummary && (
          <div className="px-5 pt-4 pb-5">
            <p className="text-sm leading-relaxed" style={{ color: 'var(--text-secondary)', lineHeight: 1.75 }}>
              {execSummary}
            </p>
          </div>
        )}

        {/* Context chips */}
        {(datasetOverview || analysisScope) && (
          <div className="px-5 pb-5 flex flex-wrap gap-3">
            {datasetOverview && (
              <div className="flex items-start gap-2 px-3 py-2.5 rounded-xl text-xs flex-1 min-w-[200px]"
                style={{ background: 'rgba(0,206,209,0.06)', border: '1px solid rgba(0,206,209,0.15)' }}>
                <BarChart2 className="w-3.5 h-3.5 mt-0.5 shrink-0" style={{ color: 'var(--teal)' }} />
                <span style={{ color: 'var(--text-secondary)', lineHeight: 1.5 }}>{datasetOverview}</span>
              </div>
            )}
            {analysisScope && (
              <div className="flex items-start gap-2 px-3 py-2.5 rounded-xl text-xs flex-1 min-w-[200px]"
                style={{ background: 'rgba(155,89,182,0.06)', border: '1px solid rgba(155,89,182,0.15)' }}>
                <Activity className="w-3.5 h-3.5 mt-0.5 shrink-0" style={{ color: 'var(--purple)' }} />
                <span style={{ color: 'var(--text-secondary)', lineHeight: 1.5 }}>{analysisScope}</span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Key Findings */}
      {findings.length > 0 && (
        <div className="job-card overflow-hidden">
          <div className="px-5 py-4 section-divider flex items-center gap-3">
            <div className="icon-pill" style={{ background: 'rgba(243,156,18,0.12)', border: '1px solid rgba(243,156,18,0.2)' }}>
              <Lightbulb className="w-4 h-4" style={{ color: '#F39C12' }} />
            </div>
            <div>
              <h3 className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>Key Findings</h3>
              <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{findings.length} critical discoveries from your data</p>
            </div>
          </div>
          <div className="p-5 space-y-3">
            {findings.map((finding, i) => (
              <div key={i} className="flex items-start gap-3 p-3.5 rounded-xl"
                style={{ background: 'rgba(243,156,18,0.04)', border: '1px solid rgba(243,156,18,0.1)' }}>
                <div className="w-6 h-6 rounded-lg flex items-center justify-center shrink-0 mt-0.5"
                  style={{ background: 'rgba(243,156,18,0.15)', border: '1px solid rgba(243,156,18,0.2)' }}>
                  <span className="text-xs font-bold" style={{ color: '#F39C12' }}>{i + 1}</span>
                </div>
                <p className="text-sm leading-relaxed flex-1" style={{ color: 'var(--text-secondary)' }}>{finding}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <div className="job-card overflow-hidden">
          <div className="px-5 py-4 section-divider flex items-center gap-3">
            <div className="icon-pill" style={{ background: 'rgba(46,204,113,0.12)', border: '1px solid rgba(46,204,113,0.2)' }}>
              <ListChecks className="w-4 h-4" style={{ color: '#2ECC71' }} />
            </div>
            <div>
              <h3 className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>Action Recommendations</h3>
              <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{recommendations.length} prioritised next steps</p>
            </div>
          </div>
          <div className="p-5 space-y-3">
            {recommendations.map((rec, i) => (
              <div key={i} className="flex items-start gap-3 p-3.5 rounded-xl"
                style={{ background: 'rgba(46,204,113,0.04)', border: '1px solid rgba(46,204,113,0.12)' }}>
                <div className="w-6 h-6 rounded-lg flex items-center justify-center shrink-0 mt-0.5"
                  style={{ background: 'rgba(46,204,113,0.15)' }}>
                  <ArrowUpRight className="w-3.5 h-3.5" style={{ color: '#2ECC71' }} />
                </div>
                <p className="text-sm leading-relaxed flex-1" style={{ color: 'var(--text-secondary)' }}>{rec}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Data Quality + Limitations */}
      {(dataQuality || limitations) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {dataQuality && (
            <div className="job-card overflow-hidden">
              <div className="px-5 py-4 section-divider flex items-center gap-3">
                <div className="icon-pill" style={{ background: 'rgba(52,152,219,0.12)', border: '1px solid rgba(52,152,219,0.2)' }}>
                  <Shield className="w-4 h-4" style={{ color: '#3498DB' }} />
                </div>
                <h3 className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>Data Quality</h3>
              </div>
              <div className="px-5 pb-5 pt-3">
                <p className="text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>{dataQuality}</p>
              </div>
            </div>
          )}
          {limitations && (
            <div className="job-card overflow-hidden">
              <div className="px-5 py-4 section-divider flex items-center gap-3">
                <div className="icon-pill" style={{ background: 'rgba(255,107,107,0.1)', border: '1px solid rgba(255,107,107,0.2)' }}>
                  <AlertTriangle className="w-4 h-4" style={{ color: '#FF6B6B' }} />
                </div>
                <h3 className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>Limitations</h3>
              </div>
              <div className="px-5 pb-5 pt-3">
                <p className="text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>{limitations}</p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// ─── Plain text fallback (expandable) ────────────────────────────────────────
function PlainSummary({ text }: { text: string }) {
  const [expanded, setExpanded] = useState(false)
  const paragraphs = text.split(/\n\n+/).filter(Boolean)
  const preview    = paragraphs.slice(0, 3)
  const rest       = paragraphs.slice(3)

  return (
    <div className="job-card overflow-hidden">
      <div className="px-5 py-4 section-divider flex items-center gap-3">
        <div className="icon-pill gold">
          <FileText className="w-4 h-4" style={{ color: 'var(--gold)' }} />
        </div>
        <div>
          <h3 className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>Executive Summary</h3>
          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>AI-generated analysis overview</p>
        </div>
      </div>
      <div className="px-5 pb-5 pt-4 space-y-3">
        {(expanded ? paragraphs : preview).map((p, i) => (
          <p key={i} className="text-sm leading-relaxed" style={{ color: 'var(--text-secondary)', lineHeight: 1.75 }}>
            {p}
          </p>
        ))}
        {rest.length > 0 && (
          <button onClick={() => setExpanded(e => !e)}
            className="mt-2 flex items-center gap-1.5 text-xs transition-colors"
            style={{ color: 'var(--text-muted)' }}
            onMouseEnter={e => (e.currentTarget.style.color = 'var(--gold)')}
            onMouseLeave={e => (e.currentTarget.style.color = 'var(--text-muted)')}>
            {expanded
              ? <><ChevronUp   className="w-3.5 h-3.5" /> Show less</>
              : <><ChevronDown className="w-3.5 h-3.5" /> Read more ({rest.length} more sections)</>}
          </button>
        )}
      </div>
    </div>
  )
}

// ─── Dataset Profile Card ─────────────────────────────────────────────────────
function DataProfileCard({ profile }: { profile: any }) {
  if (!profile) return null
  const metrics = [
    { label: 'Total Records', value: profile.row_count?.toLocaleString(),  icon: Target,      color: '#D4AF37' },
    { label: 'Features',      value: profile.column_count,                  icon: BarChart3,   color: '#00CED1' },
    { label: 'Data Quality',  value: `${profile.quality_score}%`,           icon: CheckCircle, color: profile.quality_score > 80 ? '#2ECC71' : '#F39C12' },
    { label: 'Completeness',  value: `${profile.completeness}%`,            icon: TrendingUp,  color: '#9B59B6' },
  ]
  return (
    <div className="job-card overflow-hidden">
      <div className="px-5 py-4 section-divider flex items-center gap-3">
        <div className="icon-pill purple">
          <Sparkles className="w-4 h-4" style={{ color: 'var(--purple)' }} />
        </div>
        <div>
          <h3 className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>Dataset Profile</h3>
          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Data quality and structure overview</p>
        </div>
      </div>
      <div className="p-5 grid grid-cols-2 md:grid-cols-4 gap-3">
        {metrics.map(m => (
          <div key={m.label} className="metric-tile text-center">
            <m.icon className="w-5 h-5 mx-auto mb-2" style={{ color: m.color }} />
            <div className="text-2xl font-bold mb-1" style={{ color: m.color }}>{m.value}</div>
            <div className="text-xs" style={{ color: 'var(--text-muted)' }}>{m.label}</div>
          </div>
        ))}
      </div>
      {profile.numeric_columns?.length > 0 && (
        <div className="px-5 pb-5">
          <p className="text-xs mb-2" style={{ color: 'var(--text-muted)' }}>Numeric columns:</p>
          <div className="flex flex-wrap gap-1.5">
            {profile.numeric_columns.map((col: string) => (
              <span key={col} className="text-xs px-2.5 py-1 rounded-lg font-mono"
                style={{ background: 'rgba(212,175,55,0.08)', color: 'var(--gold)', border: '1px solid rgba(212,175,55,0.15)' }}>
                {col}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// ─── Main ReportTab ───────────────────────────────────────────────────────────
export function ReportTab({
  reportHtml, reportSummary, charts, profile, analytics, jobId, jobName, onExportPDF
}: Props) {
  const [htmlView, setHtmlView] = useState(false)

  const hasContent = reportSummary || (analytics && Object.keys(analytics).length > 0)

  if (!hasContent && !reportHtml) {
    return (
      <div className="job-card p-16 text-center">
        <BookOpen className="w-12 h-12 mx-auto mb-4" style={{ color: 'var(--text-faint)' }} />
        <h3 className="font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>Report Not Ready</h3>
        <p className="text-sm max-w-sm mx-auto" style={{ color: 'var(--text-muted)' }}>
          The report is generated after analysis completes.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-5 fade-in">
      {/* Toolbar */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h2 className="font-bold" style={{ color: 'var(--text-primary)' }}>Analysis Report</h2>
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>{jobName}</p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          {reportHtml && (
            <button onClick={() => setHtmlView(v => !v)}
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold transition-all"
              style={{
                background: htmlView ? 'rgba(0,206,209,0.12)' : 'var(--bg-input)',
                border: `1px solid ${htmlView ? 'rgba(0,206,209,0.3)' : 'var(--border-faint)'}`,
                color: htmlView ? 'var(--teal)' : 'var(--text-muted)',
              }}>
              <Eye className="w-3.5 h-3.5" />
              {htmlView ? 'Structured View' : 'HTML Preview'}
            </button>
          )}
          <button onClick={onExportPDF}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold transition-all"
            style={{ background: 'rgba(46,204,113,0.1)', border: '1px solid rgba(46,204,113,0.2)', color: '#2ECC71' }}>
            <Download className="w-3.5 h-3.5" /> Export PDF
          </button>
        </div>
      </div>

      {/* HTML Preview */}
      {htmlView && reportHtml ? (
        <div className="job-card overflow-hidden">
          <div className="px-5 py-4 section-divider flex items-center gap-2">
            <Eye className="w-4 h-4" style={{ color: 'var(--teal)' }} />
            <span className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>HTML Report Preview</span>
          </div>
          <div className="p-1">
            <iframe srcDoc={reportHtml} className="w-full rounded-xl"
              style={{ height: '700px', border: 'none' }} title="Report Preview" />
          </div>
        </div>
      ) : (
        <>
          <DataProfileCard profile={profile} />

          {/* Executive Summary — structured, no raw JSON */}
          {reportSummary && <SummarySection text={
            typeof reportSummary === 'string' ? reportSummary : JSON.stringify(reportSummary)
          } />}

          {/* Interactive Charts */}
          {analytics && (
            <div className="job-card overflow-hidden">
              <div className="px-5 py-4 section-divider flex items-center gap-3">
                <div className="icon-pill teal">
                  <BarChart3 className="w-4 h-4" style={{ color: 'var(--teal)' }} />
                </div>
                <div>
                  <h3 className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>
                    Interactive Visual Analysis
                  </h3>
                  <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                    Dynamic charts — switch types, filter, zoom
                  </p>
                </div>
              </div>
              <div className="p-5">
                <VisualizationsTab analytics={analytics} jobId={jobId} jobName={jobName} />
              </div>
            </div>
          )}

          {/* Export CTA */}
          <div className="job-card p-5 flex items-center justify-between flex-wrap gap-4"
            style={{ background: 'linear-gradient(135deg, rgba(212,175,55,0.06), rgba(46,204,113,0.04))' }}>
            <div className="flex items-start gap-3">
              <div className="icon-pill gold"><Download className="w-4 h-4" style={{ color: 'var(--gold)' }} /></div>
              <div>
                <p className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>Export Full Report</p>
                <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>
                  Download as PDF with all charts and insights
                </p>
              </div>
            </div>
            <button onClick={onExportPDF} className="btn-gold text-sm px-5 py-2.5 flex items-center gap-2">
              <Download className="w-4 h-4" /> Download PDF
            </button>
          </div>
        </>
      )}
    </div>
  )
}
