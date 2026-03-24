import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import {
  Upload, FileText, Play, X, CheckCircle, Loader2, Sparkles,
  BarChart3, Brain, Shield, TrendingUp, Database
} from 'lucide-react'

const API_BASE = 'http://localhost:8000'

const PIPELINE_STEPS = [
  { icon: Database, label: 'Profile & Detect', desc: 'Schema, types, domain' },
  { icon: Brain, label: 'AI Analysis', desc: 'Patterns, correlations, KPIs' },
  { icon: BarChart3, label: 'Smart Charts', desc: 'Auto-selected visualizations' },
  { icon: Sparkles, label: 'Insights', desc: 'Business recommendations' },
]

export function UploadPage() {
  const { apiKey } = useAuth()
  const navigate = useNavigate()
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [file, setFile] = useState<File | null>(null)
  const [datasetId, setDatasetId] = useState('')
  const [uploading, setUploading] = useState(false)
  const [starting, setStarting] = useState(false)
  const [dragOver, setDragOver] = useState(false)
  const [error, setError] = useState('')

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile && (droppedFile.type === 'text/csv' || droppedFile.name.endsWith('.csv'))) {
      setFile(droppedFile)
      setError('')
    } else {
      setError('Please upload a CSV file')
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
      setError('')
    }
  }

  const handleUpload = async () => {
    if (!file || !apiKey) return
    setUploading(true)
    setError('')

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('dataset_id', datasetId || file.name.replace('.csv', ''))

      const uploadRes = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        headers: { 'X-API-Key': apiKey },
        body: formData,
      })

      if (!uploadRes.ok) {
        const err = await uploadRes.json()
        throw new Error(err.detail || 'Upload failed')
      }

      const uploadData = await uploadRes.json()
      setStarting(true)

      const pipelineRes = await fetch(`${API_BASE}/pipeline/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-API-Key': apiKey },
        body: JSON.stringify({ file_path: uploadData.file_path, dataset_id: uploadData.dataset_id }),
      })

      if (!pipelineRes.ok) {
        const err = await pipelineRes.json()
        throw new Error(err.detail || 'Failed to start pipeline')
      }

      const pipelineData = await pipelineRes.json()
      navigate(`/jobs/${pipelineData.job_id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setUploading(false)
      setStarting(false)
    }
  }

  const isLoading = uploading || starting

  return (
    <div className="max-w-3xl mx-auto fade-in">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">
          Upload Dataset
          <span className="gradient-text ml-3">→</span>
        </h1>
        <p className="text-gray-500 text-sm">Drop a CSV to start AI-powered analysis — domain detection, smart charts, and business insights in seconds.</p>
      </div>

      {!file ? (
        <div
          className="glass p-14 text-center cursor-pointer transition-all duration-300"
          style={{
            border: dragOver ? '1px solid rgba(212,175,55,0.5)' : '1px solid rgba(212,175,55,0.1)',
            background: dragOver ? 'rgba(212,175,55,0.04)' : undefined,
            transform: dragOver ? 'scale(1.01)' : undefined,
          }}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <input ref={fileInputRef} type="file" accept=".csv" className="hidden" onChange={handleFileSelect} />

          <div className={`w-20 h-20 rounded-2xl bg-[#D4AF37]/10 border border-[#D4AF37]/20 flex items-center justify-center mx-auto mb-6 transition-all duration-300 ${dragOver ? 'scale-110 bg-[#D4AF37]/20' : ''}`}>
            <Upload className={`w-9 h-9 text-[#D4AF37] transition-transform ${dragOver ? 'scale-110' : ''}`} />
          </div>

          <h3 className="text-xl font-semibold text-white mb-2">
            {dragOver ? 'Release to upload' : 'Drop your CSV file here'}
          </h3>
          <p className="text-gray-500 text-sm mb-2">or click to browse your files</p>
          <p className="text-gray-700 text-xs">Supports CSV files up to 100MB · All business domains supported</p>
        </div>
      ) : (
        <div className="glass p-6">
          <div className="flex items-start justify-between mb-6">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-xl bg-[#D4AF37]/10 border border-[#D4AF37]/20 flex items-center justify-center">
                <FileText className="w-7 h-7 text-[#D4AF37]" />
              </div>
              <div>
                <h3 className="font-semibold text-white text-lg">{file.name}</h3>
                <p className="text-gray-500 text-sm mt-0.5">
                  {(file.size / 1024).toFixed(1)} KB · CSV
                </p>
                <div className="flex items-center gap-1 mt-1">
                  <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="text-xs text-emerald-400">Ready for analysis</span>
                </div>
              </div>
            </div>
            <button
              onClick={() => { setFile(null); setError('') }}
              className="p-2 rounded-lg hover:bg-white/5 transition-colors text-gray-500 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="mb-6">
            <label className="block text-sm text-gray-400 mb-2 font-medium">
              Dataset Name <span className="text-gray-600 font-normal">(optional)</span>
            </label>
            <input
              type="text"
              value={datasetId}
              onChange={(e) => setDatasetId(e.target.value)}
              className="input-gold"
              placeholder={file.name.replace('.csv', '')}
            />
            <p className="text-gray-600 text-xs mt-1.5">Used to identify this analysis in your dashboard</p>
          </div>

          {/* Pipeline preview */}
          <div className="mb-6 rounded-xl p-4" style={{ background:'rgba(212,175,55,0.03)', border:'1px solid rgba(212,175,55,0.07)' }}>
            <p className="text-xs text-gray-500 mb-3 font-medium uppercase tracking-wide">What happens next</p>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {PIPELINE_STEPS.map((step, i) => (
                <div key={i} className="flex items-center gap-2 text-xs text-gray-400">
                  <div className="w-6 h-6 rounded-md bg-[#D4AF37]/10 flex items-center justify-center shrink-0">
                    <step.icon className="w-3.5 h-3.5 text-[#D4AF37]" />
                  </div>
                  <span>{step.label}</span>
                </div>
              ))}
            </div>
          </div>

          {error && (
            <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
              {error}
            </div>
          )}

          <button
            onClick={handleUpload}
            disabled={isLoading}
            className="btn-gold w-full flex items-center justify-center gap-2.5 py-4 text-base disabled:opacity-70 disabled:cursor-not-allowed"
          >
            {uploading ? (
              <><Loader2 className="w-5 h-5 animate-spin" /> Uploading file...</>
            ) : starting ? (
              <><Loader2 className="w-5 h-5 animate-spin" /> Starting analysis pipeline...</>
            ) : (
              <><Play className="w-5 h-5" /> Run AI Analysis</>
            )}
          </button>
        </div>
      )}

      {/* Feature cards */}
      <div className="mt-8 grid grid-cols-3 gap-4">
        {[
          { icon: TrendingUp, title: 'Smart Charts', desc: 'Auto-selects the most impactful chart type for your data.' },
          { icon: Brain, title: 'AI Insights', desc: 'LLM-generated business insights with recommended actions.' },
          { icon: Shield, title: 'Decision-Ready', desc: 'Reports formatted for executives and stakeholders.' },
        ].map((f) => (
          <div key={f.title} className="card text-center group hover:border-[#D4AF37]/20 transition-colors">
            <div className="w-10 h-10 rounded-xl bg-[#D4AF37]/8 border border-[#D4AF37]/15 flex items-center justify-center mx-auto mb-3 group-hover:bg-[#D4AF37]/15 transition-colors">
              <f.icon className="w-5 h-5 text-[#D4AF37]" />
            </div>
            <h4 className="font-semibold text-white text-sm mb-1">{f.title}</h4>
            <p className="text-gray-500 text-xs leading-relaxed">{f.desc}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
