/**
 * Custom Analytics — Tableau / Power BI–style free-form workspace
 * ════════════════════════════════════════════════════════════════
 * Features:
 *  • Load 1 or 2 CSV datasets (drag-drop or browse)
 *  • Drag-and-drop field pills onto X / Y / Color / Size / Tooltip slots
 *  • 16+ chart types grouped by category with icon preview
 *  • Multi-select Y columns (overlaid as series)
 *  • Value labeling toggle (show values on bars/points)
 *  • Column renaming / axis labeling
 *  • Per-column filters (range slider for numeric, checkbox list for categorical)
 *  • Color palette selector (6 themes)
 *  • Aggregation function per Y field
 *  • Custom chart title, subtitle, axis labels
 *  • Row limit slider
 *  • AI Insight via Claude API
 *  • Export chart as PNG (html2canvas)
 *  • ➕ Add any chart view to My Dashboard (useDashboard)
 *  • Multi-chart tabs (up to 8 simultaneous views)
 *  • Dataset source selector when both A+B loaded (A / B / Merged)
 *  • Smart type-detection: number / date / string
 */

import { useState, useCallback, useMemo, useRef } from 'react'
import {
  BarChart, Bar, LineChart, Line, AreaChart, Area,
  ScatterChart, Scatter, PieChart, Pie, Cell,
  ComposedChart, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  CartesianGrid, XAxis, YAxis, ZAxis, Tooltip, Legend,
  ResponsiveContainer, ReferenceLine, Treemap, FunnelChart, Funnel, LabelList,
} from 'recharts'
import {
  Upload, ChevronDown, ChevronUp, Plus, Trash2, Play, Download,
  Sparkles, Filter, Sliders, Palette, RefreshCw, X,
  BarChart2, TrendingUp, PieChart as PieIcon, GitBranch,
  Activity, Layers, Database, Zap, Pin, Check,
  Tag, Hash, Type, LayoutGrid, SlidersHorizontal,
} from 'lucide-react'
import { useDashboard } from '../hooks/useDashboard'

// ─── Constants ────────────────────────────────────────────────────────────────
const C = {
  gold:'#D4AF37', teal:'#00CED1', coral:'#FF6B6B', purple:'#9B59B6',
  green:'#2ECC71', amber:'#F39C12', blue:'#3498DB', pink:'#E91E63',
  cyan:'#00BCD4', lime:'#8BC34A', orange:'#FF9800', indigo:'#5C6BC0',
}
const PALETTES: Record<string, string[]> = {
  Gold:    [C.gold, C.amber, C.coral, C.teal, C.purple, C.blue],
  Ocean:   ['#0EA5E9','#06B6D4','#10B981','#3B82F6','#6366F1','#8B5CF6'],
  Sunset:  ['#F59E0B','#EF4444','#EC4899','#8B5CF6','#6366F1','#3B82F6'],
  Forest:  ['#22C55E','#16A34A','#84CC16','#CA8A04','#D97706','#B45309'],
  Mono:    ['#F8FAFC','#CBD5E1','#94A3B8','#64748B','#475569','#334155'],
  Vibrant: ['#FF6B6B','#4ECDC4','#45B7D1','#96CEB4','#FFEAA7','#DDA0DD'],
}

const CHART_TYPES = [
  { id:'bar',       label:'Bar',        icon:'▮', cat:'Comparison' },
  { id:'hbar',      label:'H-Bar',      icon:'▬', cat:'Comparison' },
  { id:'line',      label:'Line',       icon:'⌇', cat:'Trend' },
  { id:'area',      label:'Area',       icon:'◿', cat:'Trend' },
  { id:'composed',  label:'Composed',   icon:'⊞', cat:'Trend' },
  { id:'step',      label:'Step Line',  icon:'⌐', cat:'Trend' },
  { id:'scatter',   label:'Scatter',    icon:'●', cat:'Correlation' },
  { id:'bubble',    label:'Bubble',     icon:'◉', cat:'Correlation' },
  { id:'pie',       label:'Pie',        icon:'◔', cat:'Part-of-Whole' },
  { id:'donut',     label:'Donut',      icon:'◎', cat:'Part-of-Whole' },
  { id:'treemap',   label:'Treemap',    icon:'▦', cat:'Part-of-Whole' },
  { id:'radar',     label:'Radar',      icon:'⬡', cat:'Comparison' },
  { id:'funnel',    label:'Funnel',     icon:'▽', cat:'Flow' },
  { id:'histogram', label:'Histogram',  icon:'▮', cat:'Distribution' },
  { id:'waterfall', label:'Waterfall',  icon:'⧗', cat:'Change' },
  { id:'lollipop',  label:'Lollipop',   icon:'◉', cat:'Comparison' },
]
const CHART_CATS = ['All','Comparison','Trend','Correlation','Part-of-Whole','Distribution','Flow','Change']
const AGG_FNS = ['sum','mean','median','count','min','max','std']
const FILTER_OPS = ['=','!=','>','<','>=','<=','contains','not contains']

// ─── Types ────────────────────────────────────────────────────────────────────
interface ColMeta { name: string; type: 'number'|'string'|'date'; vals: any[]; min?: number; max?: number }
interface Dataset { name: string; rows: Record<string,any>[]; cols: ColMeta[] }
interface FilterDef { col: string; op: string; val: string; active: boolean }
interface ColLabel { [col: string]: string }   // custom axis label per col
interface ChartConfig {
  title: string
  subtitle: string
  chartType: string
  xCol: string
  yCols: string[]
  colorCol: string
  sizeCol: string
  aggregation: string
  palette: string
  showGrid: boolean
  showLegend: boolean
  showLabels: boolean
  showTrendline: boolean
  xLabel: string
  yLabel: string
  filters: FilterDef[]
  dataset: 'a'|'b'|'merge'
  limit: number
  colLabels: ColLabel
  sortBy: 'value_desc'|'value_asc'|'label_asc'|'label_desc'|'none'
  annotations: string
}

// ─── CSV Parser ───────────────────────────────────────────────────────────────
function parseCSV(text: string): Record<string,any>[] {
  const lines = text.trim().split(/\r?\n/)
  if (lines.length < 2) return []
  const headers = lines[0].split(',').map(h => h.trim().replace(/^"|"$/g,''))
  return lines.slice(1).map(line => {
    const vals: string[] = []
    let cur = '', inQ = false
    for (const ch of line) {
      if (ch === '"') { inQ = !inQ } else if (ch === ',' && !inQ) { vals.push(cur); cur = '' } else cur += ch
    }
    vals.push(cur)
    const row: Record<string,any> = {}
    headers.forEach((h,i) => {
      const v = (vals[i]||'').trim().replace(/^"|"$/g,'')
      const n = parseFloat(v)
      row[h] = !isNaN(n) && v !== '' ? n : v
    })
    return row
  }).filter(r => Object.values(r).some(v => v !== ''))
}

function inferCols(rows: Record<string,any>[]): ColMeta[] {
  if (!rows.length) return []
  return Object.keys(rows[0]).map(name => {
    const vals = rows.map(r => r[name]).filter(v => v !== '' && v != null)
    const numVals = vals.filter(v => typeof v === 'number') as number[]
    const type: ColMeta['type'] =
      numVals.length > vals.length * 0.7 ? 'number' :
      vals.some(v => typeof v === 'string' && /\d{4}[-/]\d{2}[-/]\d{2}/.test(v)) ? 'date' :
      'string'
    const min = numVals.length ? Math.min(...numVals) : undefined
    const max = numVals.length ? Math.max(...numVals) : undefined
    return { name, type, vals: [...new Set(vals)].slice(0,200), min, max }
  })
}

// ─── Data Processing ──────────────────────────────────────────────────────────
function applyFilters(rows: Record<string,any>[], filters: FilterDef[]) {
  return rows.filter(row => filters.filter(f=>f.active&&f.col&&f.val!=='').every(f => {
    const v = row[f.col], fv = f.val
    if (f.op === '=')           return String(v) === fv
    if (f.op === '!=')          return String(v) !== fv
    if (f.op === '>')           return parseFloat(String(v)) > parseFloat(fv)
    if (f.op === '<')           return parseFloat(String(v)) < parseFloat(fv)
    if (f.op === '>=')          return parseFloat(String(v)) >= parseFloat(fv)
    if (f.op === '<=')          return parseFloat(String(v)) <= parseFloat(fv)
    if (f.op === 'contains')    return String(v).toLowerCase().includes(fv.toLowerCase())
    if (f.op === 'not contains')return !String(v).toLowerCase().includes(fv.toLowerCase())
    return true
  }))
}

function aggregateData(rows: Record<string,any>[], xCol: string, yCols: string[], agg: string, limit: number, sortBy: string): Record<string,any>[] {
  if (!xCol || !yCols.length) return rows.slice(0,limit)
  const groups: Record<string, Record<string, number[]>> = {}
  rows.forEach(row => {
    const key = String(row[xCol] ?? '')
    if (!groups[key]) groups[key] = {}
    yCols.forEach(yc => {
      if (!groups[key][yc]) groups[key][yc] = []
      const v = parseFloat(String(row[yc]))
      if (!isNaN(v)) groups[key][yc].push(v)
    })
  })
  const fn = (arr: number[]) => {
    if (!arr.length) return 0
    if (agg === 'sum')    return arr.reduce((a,b)=>a+b,0)
    if (agg === 'mean')   return arr.reduce((a,b)=>a+b,0)/arr.length
    if (agg === 'median') { const s=[...arr].sort((a,b)=>a-b); return s[Math.floor(s.length/2)] }
    if (agg === 'count')  return arr.length
    if (agg === 'min')    return Math.min(...arr)
    if (agg === 'max')    return Math.max(...arr)
    if (agg === 'std') { const m=arr.reduce((a,b)=>a+b,0)/arr.length; return Math.sqrt(arr.reduce((a,b)=>a+(b-m)**2,0)/arr.length) }
    return arr.reduce((a,b)=>a+b,0)
  }
  let result = Object.entries(groups).map(([key, byCol]) => {
    const row: Record<string,any> = { [xCol]: key }
    yCols.forEach(yc => { row[yc] = parseFloat(fn(byCol[yc]||[]).toFixed(3)) })
    return row
  })
  if (sortBy === 'value_desc' && yCols[0]) result.sort((a,b) => (b[yCols[0]]||0) - (a[yCols[0]]||0))
  if (sortBy === 'value_asc'  && yCols[0]) result.sort((a,b) => (a[yCols[0]]||0) - (b[yCols[0]]||0))
  if (sortBy === 'label_asc')  result.sort((a,b) => String(a[xCol]).localeCompare(String(b[xCol])))
  if (sortBy === 'label_desc') result.sort((a,b) => String(b[xCol]).localeCompare(String(a[xCol])))
  return result.slice(0,limit)
}

// ─── Helpers ──────────────────────────────────────────────────────────────────
const nf = (v:any, d=1) => {
  if (v==null||isNaN(+v)) return '–'
  const n=+v, a=Math.abs(n)
  if (a>=1e9) return `${(n/1e9).toFixed(d)}B`
  if (a>=1e6) return `${(n/1e6).toFixed(d)}M`
  if (a>=1e3) return `${(n/1e3).toFixed(d)}K`
  return n.toLocaleString(undefined,{maximumFractionDigits:2})
}

// ─── Custom Tooltip ───────────────────────────────────────────────────────────
function CustomTip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null
  return (
    <div style={{background:'#10101c',border:'1px solid rgba(212,175,55,.2)',borderRadius:12,padding:'10px 14px',minWidth:160,boxShadow:'0 8px 24px rgba(0,0,0,.5)'}}>
      {label!=null&&<p style={{color:'rgba(255,255,255,.35)',fontSize:10,fontWeight:600,marginBottom:6,paddingBottom:6,borderBottom:'1px solid rgba(212,175,55,.08)'}}>{label}</p>}
      {payload.map((p:any,i:number)=>(
        <div key={i} style={{display:'flex',alignItems:'center',justifyContent:'space-between',gap:12,padding:'2px 0'}}>
          <span style={{display:'flex',alignItems:'center',gap:6,color:'rgba(255,255,255,.5)',fontSize:11}}>
            <span style={{width:8,height:8,borderRadius:'50%',background:p.color??p.fill??C.gold,flexShrink:0}}/>
            {p.name}
          </span>
          <span style={{color:'#fff',fontWeight:700,fontSize:11}}>{typeof p.value==='number'?nf(p.value):String(p.value??'–')}</span>
        </div>
      ))}
    </div>
  )
}

// ─── UI Atoms ─────────────────────────────────────────────────────────────────
function Panel({ title, icon:Icon, children, defaultOpen=true, extra }: { title:string; icon?:any; children:React.ReactNode; defaultOpen?:boolean; extra?: React.ReactNode }) {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <div style={{background:'rgba(255,255,255,.02)',border:'1px solid rgba(255,255,255,.07)',borderRadius:14,overflow:'hidden',marginBottom:10}}>
      <button onClick={()=>setOpen(o=>!o)} style={{width:'100%',display:'flex',alignItems:'center',justifyContent:'space-between',padding:'11px 14px',background:'transparent',border:'none',cursor:'pointer',color:C.gold}}>
        <span style={{display:'flex',alignItems:'center',gap:8,fontSize:12,fontWeight:700}}>
          {Icon&&<Icon style={{width:13,height:13}}/>}{title}
        </span>
        <div style={{display:'flex',gap:6,alignItems:'center'}}>
          {extra}
          {open?<ChevronUp style={{width:12,height:12,color:'rgba(255,255,255,.3)'}}/>:<ChevronDown style={{width:12,height:12,color:'rgba(255,255,255,.3)'}}/>}
        </div>
      </button>
      {open&&<div style={{padding:'0 14px 14px'}}>{children}</div>}
    </div>
  )
}

function Lbl({ children }: { children: React.ReactNode }) {
  return <p style={{fontSize:10,color:'rgba(255,255,255,.35)',fontWeight:700,marginBottom:4,marginTop:8,textTransform:'uppercase',letterSpacing:.5}}>{children}</p>
}

function SelInput({ opts, val, onChange, placeholder }: { opts:string[]; val:string; onChange:(v:string)=>void; placeholder?:string }) {
  return (
    <div style={{position:'relative'}}>
      <select value={val} onChange={e=>onChange(e.target.value)} style={{width:'100%',padding:'7px 28px 7px 9px',borderRadius:8,fontSize:12,background:'rgba(255,255,255,.05)',border:'1px solid rgba(255,255,255,.08)',color:val?'rgba(255,255,255,.8)':'rgba(255,255,255,.35)',appearance:'none',outline:'none'}}>
        {placeholder&&<option value="">{placeholder}</option>}
        {opts.map(o=><option key={o} value={o}>{o}</option>)}
      </select>
      <ChevronDown style={{position:'absolute',right:8,top:'50%',transform:'translateY(-50%)',width:11,height:11,color:'rgba(255,255,255,.3)',pointerEvents:'none'}}/>
    </div>
  )
}

function TxtInput({ val, onChange, placeholder }: { val:string; onChange:(v:string)=>void; placeholder?:string }) {
  return <input value={val} onChange={e=>onChange(e.target.value)} placeholder={placeholder} style={{width:'100%',padding:'7px 9px',borderRadius:8,fontSize:12,background:'rgba(255,255,255,.05)',border:'1px solid rgba(255,255,255,.08)',color:'rgba(255,255,255,.8)',outline:'none',boxSizing:'border-box'}}/>
}

function Toggle({ val, onChange, label }: { val:boolean; onChange:(v:boolean)=>void; label:string }) {
  return (
    <label style={{display:'flex',alignItems:'center',justifyContent:'space-between',cursor:'pointer',padding:'3px 0'}}>
      <span style={{fontSize:12,color:'rgba(255,255,255,.55)'}}>{label}</span>
      <div onClick={()=>onChange(!val)} style={{width:30,height:17,borderRadius:9,background:val?C.gold:'rgba(255,255,255,.1)',position:'relative',transition:'all .2s',cursor:'pointer',border:`1px solid ${val?C.gold:'rgba(255,255,255,.15)'}`}}>
        <div style={{position:'absolute',top:1,left:val?12:1,width:13,height:13,borderRadius:'50%',background:'#fff',transition:'all .2s'}}/>
      </div>
    </label>
  )
}

// ─── Field Pill ──────────────────────────────────────────────────────────────
function FieldPill({ col, type, selected, onClick }: { col:ColMeta; type?:string; selected?:boolean; onClick?:()=>void }) {
  const icon = col.type==='number'?'#':col.type==='date'?'📅':'A'
  const col_c = col.type==='number'?C.teal:col.type==='date'?C.purple:C.amber
  return (
    <button onClick={onClick} style={{display:'flex',alignItems:'center',gap:5,padding:'4px 10px',borderRadius:20,fontSize:11,cursor:'pointer',fontWeight:selected?700:400,background:selected?`${col_c}20`:'rgba(255,255,255,.04)',border:`1px solid ${selected?col_c:'rgba(255,255,255,.08)'}`,color:selected?col_c:'rgba(255,255,255,.5)',whiteSpace:'nowrap',transition:'all .15s'}}>
      <span style={{fontSize:10}}>{icon}</span>{col.name}
    </button>
  )
}

// ─── Slot Drop Zone ───────────────────────────────────────────────────────────
function SlotZone({ label, col, onRemove, children }: { label:string; col?:string; onRemove?:()=>void; children?:React.ReactNode }) {
  return (
    <div style={{marginBottom:8}}>
      <p style={{fontSize:9,color:'rgba(255,255,255,.3)',fontWeight:700,textTransform:'uppercase',letterSpacing:.6,marginBottom:3}}>{label}</p>
      <div style={{minHeight:34,padding:'4px 8px',borderRadius:8,border:'1px dashed rgba(255,255,255,.12)',background:'rgba(255,255,255,.02)',display:'flex',alignItems:'center',gap:6,flexWrap:'wrap'}}>
        {col ? (
          <div style={{display:'flex',alignItems:'center',gap:6,padding:'3px 10px',borderRadius:20,background:'rgba(212,175,55,.12)',border:'1px solid rgba(212,175,55,.3)',color:C.gold,fontSize:11,fontWeight:600}}>
            {col}
            {onRemove&&<button onClick={onRemove} style={{background:'none',border:'none',cursor:'pointer',color:'rgba(255,255,255,.4)',padding:0,lineHeight:1,display:'flex'}}><X style={{width:11,height:11}}/></button>}
          </div>
        ) : (
          <span style={{fontSize:11,color:'rgba(255,255,255,.2)'}}>— none —</span>
        )}
        {children}
      </div>
    </div>
  )
}

// ─── Dataset Upload Card ──────────────────────────────────────────────────────
function DatasetCard({ label, ds, onLoad, onClear }: { label:string; ds:Dataset|null; onLoad:(d:Dataset)=>void; onClear:()=>void }) {
  const [dragging, setDragging] = useState(false)
  const handleFile = useCallback(async (file: File) => {
    if (!file.name.endsWith('.csv')) return
    const text = await file.text()
    const rows = parseCSV(text)
    const cols = inferCols(rows)
    onLoad({ name: file.name.replace('.csv',''), rows, cols })
  }, [onLoad])
  return (
    <div
      onDragOver={e=>{e.preventDefault();setDragging(true)}}
      onDragLeave={()=>setDragging(false)}
      onDrop={e=>{e.preventDefault();setDragging(false);const f=e.dataTransfer.files[0];if(f)handleFile(f)}}
      style={{border:`2px dashed ${dragging?C.gold:'rgba(255,255,255,.1)'}`,borderRadius:12,padding:14,background:dragging?'rgba(212,175,55,.04)':'rgba(255,255,255,.02)',transition:'all .15s'}}>
      <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',marginBottom:6}}>
        <span style={{fontSize:10,fontWeight:700,color:C.gold,textTransform:'uppercase',letterSpacing:.5}}>{label}</span>
        {ds&&<button onClick={onClear} style={{background:'none',border:'none',cursor:'pointer',color:'rgba(255,255,255,.3)',padding:2}}><X style={{width:13,height:13}}/></button>}
      </div>
      {ds ? (
        <div>
          <div style={{display:'flex',alignItems:'center',gap:8,marginBottom:5}}>
            <Database style={{width:15,height:15,color:C.teal}}/>
            <span style={{fontSize:12,fontWeight:600,color:'#fff'}}>{ds.name}</span>
          </div>
          <div style={{display:'flex',gap:10,marginBottom:6}}>
            <span style={{fontSize:10,color:'rgba(255,255,255,.4)'}}>{ds.rows.length.toLocaleString()} rows</span>
            <span style={{fontSize:10,color:'rgba(255,255,255,.4)'}}>{ds.cols.length} cols</span>
          </div>
          <div style={{display:'flex',flexWrap:'wrap',gap:3}}>
            {ds.cols.slice(0,8).map(c=>(
              <span key={c.name} style={{fontSize:9,padding:'2px 6px',borderRadius:20,background:'rgba(255,255,255,.06)',color:'rgba(255,255,255,.45)',border:'1px solid rgba(255,255,255,.06)'}}>
                {c.type==='number'?'#':c.type==='date'?'📅':'A'} {c.name}
              </span>
            ))}
            {ds.cols.length>8&&<span style={{fontSize:9,color:'rgba(255,255,255,.25)'}}>+{ds.cols.length-8} more</span>}
          </div>
        </div>
      ) : (
        <label style={{display:'flex',flexDirection:'column',alignItems:'center',gap:6,cursor:'pointer',padding:'10px 0'}}>
          <input type="file" accept=".csv" style={{display:'none'}} onChange={e=>{const f=e.target.files?.[0];if(f)handleFile(f)}}/>
          <Upload style={{width:22,height:22,color:'rgba(255,255,255,.2)'}}/>
          <span style={{fontSize:11,color:'rgba(255,255,255,.3)',textAlign:'center'}}>Drop CSV or click to browse</span>
        </label>
      )}
    </div>
  )
}

// ─── Chart Renderer ───────────────────────────────────────────────────────────
function ChartRenderer({ cfg, data, labels }: { cfg: ChartConfig; data: Record<string,any>[]; labels: ColLabel }) {
  const colors = PALETTES[cfg.palette] || PALETTES.Gold
  const { xCol, yCols, chartType, showGrid, showLegend, showLabels, xLabel, yLabel } = cfg
  const xl = labels[xCol] || xLabel || xCol
  const yl = yCols[0] ? (labels[yCols[0]] || yLabel || yCols[0]) : yLabel

  if (!data.length || !xCol) return (
    <div style={{height:340,display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',gap:8,color:'rgba(255,255,255,.2)',fontSize:13}}>
      <BarChart2 style={{width:32,height:32,opacity:.3}}/>
      Configure columns to preview chart
    </div>
  )

  const AXS = { stroke:'rgba(255,255,255,.06)', tick:{fill:'rgba(255,255,255,.35)',fontSize:10} as any }
  const H = 340

  if (chartType === 'pie' || chartType === 'donut') {
    const inner = chartType==='donut'?80:0
    const pieData = data.slice(0,20).map(r=>({name:String(r[xCol]),value:parseFloat(String(r[yCols[0]]||0))||0}))
    return (
      <ResponsiveContainer width="100%" height={H}>
        <PieChart>
          <Pie data={pieData} dataKey="value" nameKey="name" outerRadius={130} innerRadius={inner} paddingAngle={2} startAngle={90} endAngle={-270}>
            {pieData.map((_,i)=><Cell key={i} fill={colors[i%colors.length]}/>)}
            {showLabels&&<LabelList dataKey="name" position="outside" style={{fontSize:10,fill:'rgba(255,255,255,.5)'}}/>}
          </Pie>
          <Tooltip content={<CustomTip/>}/>
          {showLegend&&<Legend wrapperStyle={{fontSize:11}}/>}
        </PieChart>
      </ResponsiveContainer>
    )
  }

  if (chartType === 'radar') {
    return (
      <ResponsiveContainer width="100%" height={H}>
        <RadarChart data={data.slice(0,12)}>
          <PolarGrid stroke="rgba(255,255,255,.08)"/>
          <PolarAngleAxis dataKey={xCol} tick={{fill:'rgba(255,255,255,.4)',fontSize:10}}/>
          <PolarRadiusAxis tick={{fill:'rgba(255,255,255,.2)',fontSize:7}}/>
          {yCols.map((yc,i)=><Radar key={yc} name={labels[yc]||yc} dataKey={yc} stroke={colors[i%colors.length]} fill={colors[i%colors.length]} fillOpacity={.15} strokeWidth={2}/>)}
          {showLegend&&<Legend wrapperStyle={{fontSize:11}}/>}
          <Tooltip content={<CustomTip/>}/>
        </RadarChart>
      </ResponsiveContainer>
    )
  }

  if (chartType === 'scatter' || chartType === 'bubble') {
    const yc0=yCols[0]||'', yc1=yCols[1]||''
    const scData = data.slice(0,300).map(r=>({x:parseFloat(String(r[xCol]))||0,y:parseFloat(String(r[yc0]))||0,z:parseFloat(String(r[yc1]))||20}))
    return (
      <ResponsiveContainer width="100%" height={H}>
        <ScatterChart margin={{top:10,right:20,bottom:30,left:10}}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.06)"/>
          <XAxis type="number" dataKey="x" {...AXS} name={xl} label={{value:xl,position:'insideBottom',offset:-10,fill:'rgba(255,255,255,.3)',fontSize:10}}/>
          <YAxis type="number" dataKey="y" {...AXS} name={yl} label={{value:yl,angle:-90,position:'insideLeft',fill:'rgba(255,255,255,.3)',fontSize:10}}/>
          {chartType==='bubble'&&<ZAxis type="number" dataKey="z" range={[40,400]}/>}
          <Tooltip content={<CustomTip/>}/>
          <Scatter data={scData} fill={colors[0]} opacity={.75}/>
        </ScatterChart>
      </ResponsiveContainer>
    )
  }

  if (chartType === 'treemap') {
    const tmData = data.slice(0,40).map((r,i)=>({name:String(r[xCol]),size:Math.abs(parseFloat(String(r[yCols[0]]||1)))||1,fill:colors[i%colors.length]}))
    const TmNode = (props:any)=>{const{x,y,width,height,name,fill}=props;if(!width||!height||width<20)return null;return<g><rect x={x+1} y={y+1} width={width-2} height={height-2} rx={3} style={{fill,fillOpacity:.8,stroke:'rgba(0,0,0,.3)',strokeWidth:1}}/>{width>50&&height>25&&<text x={x+width/2} y={y+height/2+4} textAnchor="middle" fill="#fff" fontSize={Math.min(12,width/8)} style={{pointerEvents:'none'}}>{String(name).slice(0,14)}</text>}</g>}
    return (
      <ResponsiveContainer width="100%" height={H}>
        <Treemap data={tmData} dataKey="size" content={<TmNode/>}><Tooltip content={<CustomTip/>}/></Treemap>
      </ResponsiveContainer>
    )
  }

  if (chartType === 'funnel') {
    const fnData = data.slice(0,8).map((r,i)=>({name:String(r[xCol]),value:parseFloat(String(r[yCols[0]]||0))||0,fill:colors[i%colors.length]}))
    return (
      <ResponsiveContainer width="100%" height={H}>
        <FunnelChart>
          <Tooltip content={<CustomTip/>}/>
          <Funnel dataKey="value" data={fnData} isAnimationActive>
            {fnData.map((_,i)=><Cell key={i} fill={colors[i%colors.length]}/>)}
          </Funnel>
        </FunnelChart>
      </ResponsiveContainer>
    )
  }

  if (chartType === 'histogram') {
    const numVals = data.map(r=>parseFloat(String(r[yCols[0]||xCol]))).filter(v=>!isNaN(v))
    if (!numVals.length) return <div style={{height:H,display:'flex',alignItems:'center',justifyContent:'center',color:'rgba(255,255,255,.2)'}}>No numeric data</div>
    const min=Math.min(...numVals), max=Math.max(...numVals), bins=20, step=(max-min)/bins||1
    const buckets=Array.from({length:bins},(_,i)=>({x:`${(min+i*step).toFixed(1)}`,count:numVals.filter(v=>v>=min+i*step&&v<min+(i+1)*step).length}))
    return (
      <ResponsiveContainer width="100%" height={H}>
        <BarChart data={buckets} margin={{top:5,right:10,bottom:30,left:0}}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false}/>
          <XAxis dataKey="x" {...AXS} tick={{fill:'rgba(255,255,255,.25)',fontSize:8}} label={{value:yl,position:'insideBottom',offset:-10,fill:'rgba(255,255,255,.3)',fontSize:10}}/>
          <YAxis {...AXS}/>
          <Tooltip content={<CustomTip/>}/>
          <Bar dataKey="count" radius={[3,3,0,0]}>{buckets.map((_,i)=><Cell key={i} fill={`${colors[0]}${Math.round(80+i*(175/bins)).toString(16).padStart(2,'0')}`}/>)}</Bar>
        </BarChart>
      </ResponsiveContainer>
    )
  }

  if (chartType === 'waterfall') {
    let running = 0
    const wfData = data.slice(0,20).map(r=>{
      const v=parseFloat(String(r[yCols[0]]||0))||0
      const entry={[xCol]:r[xCol],value:v,start:running,_pos:v>=0}; running+=v; return entry
    })
    return (
      <ResponsiveContainer width="100%" height={H}>
        <BarChart data={wfData} margin={{top:5,right:10,bottom:30,left:0}}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false}/>
          <XAxis dataKey={xCol} {...AXS}/>
          <YAxis {...AXS} tickFormatter={v=>nf(v,0)}/>
          <Tooltip content={<CustomTip/>}/>
          <ReferenceLine y={0} stroke="rgba(255,255,255,.2)" strokeWidth={1.5}/>
          <Bar dataKey="value" radius={[3,3,0,0]} maxBarSize={32}>{wfData.map((d:any,i:number)=><Cell key={i} fill={d._pos?C.green:C.coral} opacity={.85}/>)}</Bar>
        </BarChart>
      </ResponsiveContainer>
    )
  }

  if (chartType === 'lollipop') {
    return (
      <ResponsiveContainer width="100%" height={H}>
        <ComposedChart data={data} margin={{top:5,right:10,bottom:30,left:0}}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false}/>
          <XAxis dataKey={xCol} {...AXS} tick={{fill:'rgba(255,255,255,.3)',fontSize:9}}/>
          <YAxis {...AXS} tickFormatter={v=>nf(v,0)}/>
          <Tooltip content={<CustomTip/>}/>
          {yCols.slice(0,1).map((yc,i)=><Bar key={yc} dataKey={yc} name={labels[yc]||yc} fill={`${colors[i]}30`} radius={[3,3,0,0]} maxBarSize={4}/>)}
          {yCols.map((yc,i)=><Line key={`dot_${yc}`} type="monotone" dataKey={yc} name={labels[yc]||yc} stroke={colors[i%colors.length]} strokeWidth={0} dot={{r:6,fill:colors[i%colors.length],strokeWidth:0}} activeDot={{r:8}}/>)}
        </ComposedChart>
      </ResponsiveContainer>
    )
  }

  if (chartType === 'hbar') {
    return (
      <ResponsiveContainer width="100%" height={Math.max(H,data.length*34+80)}>
        <BarChart data={data} layout="vertical" margin={{left:120,right:48,top:5,bottom:5}}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" horizontal={false}/>
          <XAxis type="number" {...AXS} tickFormatter={v=>nf(v,0)} label={xl?{value:xl,position:'insideBottom',offset:-5,fill:'rgba(255,255,255,.3)',fontSize:10}:undefined}/>
          <YAxis type="category" dataKey={xCol} {...AXS} width={115}/>
          <Tooltip content={<CustomTip/>}/>
          {showLegend&&<Legend wrapperStyle={{fontSize:11}}/>}
          {yCols.map((yc,i)=>(
            <Bar key={yc} dataKey={yc} name={labels[yc]||yc} fill={colors[i%colors.length]} radius={[0,4,4,0]} maxBarSize={28} opacity={.85}>
              {showLabels&&<LabelList dataKey={yc} position="right" style={{fill:'rgba(255,255,255,.5)',fontSize:10}} formatter={(v:any)=>nf(v,0)}/>}
            </Bar>
          ))}
        </BarChart>
      </ResponsiveContainer>
    )
  }

  if (chartType === 'area') {
    return (
      <ResponsiveContainer width="100%" height={H}>
        <AreaChart data={data} margin={{top:5,right:10,bottom:30,left:0}}>
          <defs>{yCols.map((yc,i)=><linearGradient key={i} id={`ag${i}`} x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={colors[i%colors.length]} stopOpacity={.4}/><stop offset="100%" stopColor={colors[i%colors.length]} stopOpacity={.02}/></linearGradient>)}</defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false}/>
          <XAxis dataKey={xCol} {...AXS} label={xl?{value:xl,position:'insideBottom',offset:-10,fill:'rgba(255,255,255,.3)',fontSize:10}:undefined}/>
          <YAxis {...AXS} tickFormatter={v=>nf(v,0)} label={yl?{value:yl,angle:-90,position:'insideLeft',fill:'rgba(255,255,255,.3)',fontSize:10}:undefined}/>
          <Tooltip content={<CustomTip/>}/>
          {showLegend&&<Legend wrapperStyle={{fontSize:11}}/>}
          {yCols.map((yc,i)=><Area key={yc} type="monotone" dataKey={yc} name={labels[yc]||yc} stroke={colors[i%colors.length]} strokeWidth={2.5} fill={`url(#ag${i})`} dot={false} activeDot={{r:4}}>
            {showLabels&&<LabelList dataKey={yc} position="top" style={{fill:'rgba(255,255,255,.45)',fontSize:9}} formatter={(v:any)=>nf(v,0)}/>}
          </Area>)}
        </AreaChart>
      </ResponsiveContainer>
    )
  }

  if (chartType === 'step') {
    return (
      <ResponsiveContainer width="100%" height={H}>
        <LineChart data={data} margin={{top:5,right:10,bottom:30,left:0}}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false}/>
          <XAxis dataKey={xCol} {...AXS}/>
          <YAxis {...AXS} tickFormatter={v=>nf(v,0)}/>
          <Tooltip content={<CustomTip/>}/>
          {showLegend&&<Legend wrapperStyle={{fontSize:11}}/>}
          {yCols.map((yc,i)=><Line key={yc} type="stepAfter" dataKey={yc} name={labels[yc]||yc} stroke={colors[i%colors.length]} strokeWidth={2.5} dot={false}/>)}
        </LineChart>
      </ResponsiveContainer>
    )
  }

  if (chartType === 'composed') {
    return (
      <ResponsiveContainer width="100%" height={H}>
        <ComposedChart data={data} margin={{top:5,right:20,bottom:30,left:0}}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false}/>
          <XAxis dataKey={xCol} {...AXS}/>
          <YAxis {...AXS} tickFormatter={v=>nf(v,0)}/>
          <Tooltip content={<CustomTip/>}/>
          {showLegend&&<Legend wrapperStyle={{fontSize:11}}/>}
          {yCols.slice(0,1).map((yc,i)=><Bar key={yc} dataKey={yc} name={labels[yc]||yc} fill={`${colors[i]}50`} radius={[3,3,0,0]} maxBarSize={32}/>)}
          {yCols.slice(1).map((yc,i)=><Line key={yc} type="monotone" dataKey={yc} name={labels[yc]||yc} stroke={colors[(i+1)%colors.length]} strokeWidth={2.5} dot={{r:3}}/>)}
        </ComposedChart>
      </ResponsiveContainer>
    )
  }

  if (chartType === 'line') {
    return (
      <ResponsiveContainer width="100%" height={H}>
        <LineChart data={data} margin={{top:5,right:10,bottom:30,left:0}}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false}/>
          <XAxis dataKey={xCol} {...AXS} label={xl?{value:xl,position:'insideBottom',offset:-10,fill:'rgba(255,255,255,.3)',fontSize:10}:undefined}/>
          <YAxis {...AXS} tickFormatter={v=>nf(v,0)} label={yl?{value:yl,angle:-90,position:'insideLeft',fill:'rgba(255,255,255,.3)',fontSize:10}:undefined}/>
          <Tooltip content={<CustomTip/>}/>
          {showLegend&&<Legend wrapperStyle={{fontSize:11}}/>}
          {yCols.map((yc,i)=><Line key={yc} type="monotone" dataKey={yc} name={labels[yc]||yc} stroke={colors[i%colors.length]} strokeWidth={2.5} dot={{r:2}} activeDot={{r:4}}>
            {showLabels&&<LabelList dataKey={yc} position="top" style={{fill:'rgba(255,255,255,.45)',fontSize:9}} formatter={(v:any)=>nf(v,0)}/>}
          </Line>)}
        </LineChart>
      </ResponsiveContainer>
    )
  }

  // Default: vertical bar
  return (
    <ResponsiveContainer width="100%" height={H}>
      <BarChart data={data} margin={{top:5,right:10,bottom:30,left:0}}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false}/>
        <XAxis dataKey={xCol} {...AXS} tick={{fill:'rgba(255,255,255,.3)',fontSize:9}} label={xl?{value:xl,position:'insideBottom',offset:-10,fill:'rgba(255,255,255,.3)',fontSize:10}:undefined}/>
        <YAxis {...AXS} tickFormatter={v=>nf(v,0)} label={yl?{value:yl,angle:-90,position:'insideLeft',fill:'rgba(255,255,255,.3)',fontSize:10}:undefined}/>
        <Tooltip content={<CustomTip/>}/>
        {showLegend&&<Legend wrapperStyle={{fontSize:11}}/>}
        {yCols.map((yc,i)=>(
          <Bar key={yc} dataKey={yc} name={labels[yc]||yc} fill={colors[i%colors.length]} radius={[4,4,0,0]} maxBarSize={48} opacity={.85}>
            {showLabels&&<LabelList dataKey={yc} position="top" style={{fill:'rgba(255,255,255,.5)',fontSize:10}} formatter={(v:any)=>nf(v,0)}/>}
          </Bar>
        ))}
      </BarChart>
    </ResponsiveContainer>
  )
}

// ─── Default config ───────────────────────────────────────────────────────────
const defaultCfg = (): ChartConfig => ({
  title:'', subtitle:'', chartType:'bar', xCol:'', yCols:[],
  colorCol:'', sizeCol:'', aggregation:'sum', palette:'Gold',
  showGrid:true, showLegend:true, showLabels:false, showTrendline:false,
  xLabel:'', yLabel:'', filters:[], dataset:'a', limit:50,
  colLabels:{}, sortBy:'none', annotations:'',
})

// ─── Main Page ────────────────────────────────────────────────────────────────
export function CustomAnalyticsPage() {
  const { addItem, hasItem } = useDashboard()

  const [dsA, setDsA] = useState<Dataset|null>(null)
  const [dsB, setDsB] = useState<Dataset|null>(null)
  const [configs, setConfigs] = useState<ChartConfig[]>([defaultCfg()])
  const [activeIdx, setActiveIdx] = useState(0)
  const [chartCat, setChartCat] = useState('All')
  const [insightQ, setInsightQ] = useState('')
  const [insightRes, setInsightRes] = useState('')
  const [insightLoading, setInsightLoading] = useState(false)
  const [editingLabel, setEditingLabel] = useState<string|null>(null)
  const chartRef = useRef<HTMLDivElement>(null)

  const cfg = configs[activeIdx] ?? defaultCfg()

  const activeCols: ColMeta[] = useMemo(() => {
    if (cfg.dataset === 'b') return dsB?.cols ?? []
    if (cfg.dataset === 'merge') {
      const ac = dsA?.cols ?? [], bc = dsB?.cols ?? []
      const names = new Set([...ac.map(c=>c.name), ...bc.map(c=>c.name)])
      return [...names].map(n => ac.find(c=>c.name===n) ?? bc.find(c=>c.name===n)!)
    }
    return dsA?.cols ?? []
  }, [cfg.dataset, dsA, dsB])

  const numCols  = useMemo(()=>activeCols.filter(c=>c.type==='number').map(c=>c.name), [activeCols])
  const catCols  = useMemo(()=>activeCols.filter(c=>c.type!=='number').map(c=>c.name), [activeCols])
  const allCols  = useMemo(()=>activeCols.map(c=>c.name), [activeCols])

  const activeRows = useMemo(() => {
    if (cfg.dataset === 'b') return dsB?.rows ?? []
    if (cfg.dataset === 'merge') return [...(dsA?.rows??[]), ...(dsB?.rows??[])]
    return dsA?.rows ?? []
  }, [cfg.dataset, dsA, dsB])

  const chartData = useMemo(() => {
    if (!activeRows.length || !cfg.xCol) return []
    let rows = applyFilters(activeRows, cfg.filters)
    if (cfg.yCols.length) rows = aggregateData(rows, cfg.xCol, cfg.yCols, cfg.aggregation, cfg.limit, cfg.sortBy)
    else rows = rows.slice(0, cfg.limit)
    return rows
  }, [activeRows, cfg])

  const patch = useCallback((update: Partial<ChartConfig>) => {
    setConfigs(prev => prev.map((c,i) => i===activeIdx ? {...c,...update} : c))
  }, [activeIdx])

  const addChart = () => { setConfigs(prev=>[...prev, defaultCfg()]); setActiveIdx(configs.length) }
  const removeChart = (i: number) => {
    if (configs.length === 1) return
    setConfigs(prev => prev.filter((_,idx)=>idx!==i))
    setActiveIdx(Math.max(0, i-1))
  }

  const toggleYCol = (col: string) => {
    patch({ yCols: cfg.yCols.includes(col) ? cfg.yCols.filter(c=>c!==col) : [...cfg.yCols, col] })
  }

  const addFilter = () => {
    if (!allCols.length) return
    patch({ filters: [...cfg.filters, { col: allCols[0], op: '=', val: '', active: true }] })
  }
  const removeFilter = (i: number) => patch({ filters: cfg.filters.filter((_,idx)=>idx!==i) })
  const patchFilter = (i: number, update: Partial<FilterDef>) => {
    patch({ filters: cfg.filters.map((f,idx)=>idx===i?{...f,...update}:f) })
  }

  const setColLabel = (col: string, label: string) => {
    patch({ colLabels: { ...cfg.colLabels, [col]: label } })
  }

  // ── Pin to Dashboard ────────────────────────────────────────────────────
  const pinTitle = cfg.title || `Custom: ${cfg.chartType} — ${cfg.yCols.slice(0,2).join(', ')} by ${cfg.xCol}` || `Chart ${activeIdx+1}`
  const isPinned = hasItem('custom', pinTitle)

  const pinToDashboard = () => {
    addItem({
      jobId: 'custom',
      jobName: cfg.title || 'Custom Analytics',
      type: 'recharts',
      subtype: cfg.chartType,
      title: pinTitle,
      analyticsSlice: chartData,
      chartConfig: { ...cfg },
    })
  }

  // ── AI Insight ──────────────────────────────────────────────────────────
  const askInsight = async () => {
    if (!insightQ.trim() || !activeRows.length) return
    setInsightLoading(true); setInsightRes('')
    try {
      const sample = chartData.slice(0,20)
      const dsName = cfg.dataset==='a'?dsA?.name:cfg.dataset==='b'?dsB?.name:'Merged'
      const prompt = `You are a concise data analyst. Dataset: "${dsName}" (${activeRows.length} rows). Chart: ${cfg.chartType} of ${cfg.yCols.join(', ')} by ${cfg.xCol}. Aggregation: ${cfg.aggregation}. Sample data (first 20 rows): ${JSON.stringify(sample,null,2)}\n\nUser question: ${insightQ}\n\nRespond in 2-4 sentences with actionable insight. Be specific with numbers.`
      const res = await fetch('https://api.anthropic.com/v1/messages', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ model:'claude-sonnet-4-20250514', max_tokens:400, messages:[{role:'user',content:prompt}] }),
      })
      const data = await res.json()
      setInsightRes(data.content?.[0]?.text ?? 'No response.')
    } catch { setInsightRes('Unable to fetch insight. Check your connection.') }
    setInsightLoading(false)
  }

  const exportPNG = () => {
    if (!chartRef.current) return
    import('html2canvas').then(({default:h2c})=>{
      h2c(chartRef.current!).then(canvas=>{
        const a=document.createElement('a'); a.download=`${cfg.title||'chart'}.png`; a.href=canvas.toDataURL(); a.click()
      })
    }).catch(()=>alert('Run: npm install html2canvas'))
  }

  const filteredChartTypes = chartCat==='All' ? CHART_TYPES : CHART_TYPES.filter(c=>c.cat===chartCat)
  const hasData = !!dsA || !!dsB

  return (
    <div style={{minHeight:'100vh',color:'#e0e0e0',fontFamily:'-apple-system,system-ui,sans-serif'}}>

      {/* ── Page Header ── */}
      <div style={{marginBottom:20}}>
        <div style={{display:'flex',alignItems:'center',gap:12,marginBottom:4}}>
          <div style={{width:36,height:36,borderRadius:10,background:'linear-gradient(135deg,#D4AF37,#996515)',display:'flex',alignItems:'center',justifyContent:'center',flexShrink:0}}>
            <SlidersHorizontal style={{width:18,height:18,color:'#000'}}/>
          </div>
          <div>
            <h1 style={{fontSize:22,fontWeight:800,color:'#fff',margin:0}}>Custom Analytics</h1>
            <p style={{fontSize:12,color:'rgba(255,255,255,.4)',margin:0}}>Tableau-style · Multi-dataset · Full control · AI insights</p>
          </div>
        </div>
      </div>

      <div style={{display:'grid',gridTemplateColumns:'290px 1fr',gap:18,alignItems:'start'}}>

        {/* ══════════ LEFT PANEL ══════════ */}
        <div style={{position:'sticky',top:80,maxHeight:'calc(100vh - 100px)',overflowY:'auto',paddingRight:4}}>

          {/* Datasets */}
          <Panel title="Datasets" icon={Database}>
            <DatasetCard label="Dataset A" ds={dsA} onLoad={setDsA} onClear={()=>{setDsA(null);patch({dataset:'a'})}}/>
            <div style={{height:8}}/>
            <DatasetCard label="Dataset B (optional)" ds={dsB} onLoad={setDsB} onClear={()=>{setDsB(null);if(cfg.dataset!=='a')patch({dataset:'a'})}}/>
            {dsA && dsB && (
              <div style={{marginTop:10}}>
                <Lbl>Active source</Lbl>
                <div style={{display:'grid',gridTemplateColumns:'1fr 1fr 1fr',gap:5}}>
                  {(['a','b','merge'] as const).map(ds=>(
                    <button key={ds} onClick={()=>patch({dataset:ds})} style={{padding:'6px',borderRadius:8,fontSize:11,fontWeight:600,cursor:'pointer',background:cfg.dataset===ds?'rgba(212,175,55,.15)':'rgba(255,255,255,.03)',border:`1px solid ${cfg.dataset===ds?'rgba(212,175,55,.4)':'rgba(255,255,255,.08)'}`,color:cfg.dataset===ds?C.gold:'rgba(255,255,255,.4)'}}>
                      {ds==='merge'?'Merged':ds==='a'?dsA.name.slice(0,8):dsB.name.slice(0,8)}
                    </button>
                  ))}
                </div>
                <p style={{fontSize:10,color:'rgba(255,255,255,.25)',marginTop:4}}>
                  {cfg.dataset==='merge'?`${(dsA.rows.length+dsB.rows.length).toLocaleString()} rows combined`:cfg.dataset==='a'?`${dsA.rows.length.toLocaleString()} rows`:dsB?`${dsB.rows.length.toLocaleString()} rows`:''}
                </p>
              </div>
            )}
          </Panel>

          {/* Chart Type */}
          <Panel title="Chart Type" icon={BarChart2}>
            <div style={{display:'flex',gap:3,flexWrap:'wrap',marginBottom:8}}>
              {CHART_CATS.map(cat=>(
                <button key={cat} onClick={()=>setChartCat(cat)} style={{padding:'3px 8px',borderRadius:20,fontSize:10,fontWeight:600,cursor:'pointer',background:chartCat===cat?'rgba(212,175,55,.15)':'rgba(255,255,255,.04)',border:`1px solid ${chartCat===cat?'rgba(212,175,55,.4)':'rgba(255,255,255,.08)'}`,color:chartCat===cat?C.gold:'rgba(255,255,255,.45)'}}>
                  {cat}
                </button>
              ))}
            </div>
            <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:5}}>
              {filteredChartTypes.map(ct=>(
                <button key={ct.id} onClick={()=>patch({chartType:ct.id})} style={{display:'flex',alignItems:'center',gap:6,padding:'7px 9px',borderRadius:8,fontSize:12,cursor:'pointer',background:cfg.chartType===ct.id?'rgba(212,175,55,.12)':'rgba(255,255,255,.03)',border:`1px solid ${cfg.chartType===ct.id?'rgba(212,175,55,.35)':'rgba(255,255,255,.07)'}`,color:cfg.chartType===ct.id?C.gold:'rgba(255,255,255,.55)',fontWeight:cfg.chartType===ct.id?700:400}}>
                  <span style={{fontSize:14,width:18}}>{ct.icon}</span>{ct.label}
                </button>
              ))}
            </div>
          </Panel>

          {/* Fields / Axes */}
          <Panel title="Fields & Axes" icon={Layers} extra={<span style={{fontSize:9,color:'rgba(255,255,255,.25)',border:'1px solid rgba(255,255,255,.08)',borderRadius:20,padding:'1px 6px'}}>click pill to assign</span>}>
            {!hasData && <p style={{fontSize:12,color:'rgba(255,255,255,.25)',textAlign:'center',padding:'12px 0'}}>Load a dataset first</p>}
            {hasData && (
              <>
                {/* X Axis slot */}
                <SlotZone label="X Axis / Dimension" col={cfg.xCol} onRemove={()=>patch({xCol:''})}>
                  {!cfg.xCol && <span style={{fontSize:10,color:'rgba(255,255,255,.15)'}}>click a column below →</span>}
                </SlotZone>

                {/* Y Axis slot — multi */}
                <div style={{marginBottom:8}}>
                  <p style={{fontSize:9,color:'rgba(255,255,255,.3)',fontWeight:700,textTransform:'uppercase',letterSpacing:.6,marginBottom:3}}>Y Axis / Measures (multi-select)</p>
                  <div style={{minHeight:34,padding:'4px 8px',borderRadius:8,border:'1px dashed rgba(255,255,255,.12)',background:'rgba(255,255,255,.02)',display:'flex',flexWrap:'wrap',gap:5,alignItems:'center'}}>
                    {cfg.yCols.length ? cfg.yCols.map(yc=>(
                      <div key={yc} style={{display:'flex',alignItems:'center',gap:5,padding:'3px 8px',borderRadius:20,background:`${C.teal}18`,border:`1px solid ${C.teal}50`,color:C.teal,fontSize:11,fontWeight:600}}>
                        {cfg.colLabels[yc]||yc}
                        <button onClick={()=>toggleYCol(yc)} style={{background:'none',border:'none',cursor:'pointer',color:'rgba(255,255,255,.4)',padding:0,lineHeight:1,display:'flex'}}><X style={{width:10,height:10}}/></button>
                      </div>
                    )) : <span style={{fontSize:10,color:'rgba(255,255,255,.2)'}}>click numeric columns below →</span>}
                  </div>
                </div>

                {/* Aggregation */}
                <div style={{marginBottom:8}}>
                  <Lbl>Aggregation function</Lbl>
                  <SelInput opts={AGG_FNS} val={cfg.aggregation} onChange={v=>patch({aggregation:v})}/>
                </div>

                {/* Sort */}
                <div style={{marginBottom:10}}>
                  <Lbl>Sort rows by</Lbl>
                  <SelInput opts={['none','value_desc','value_asc','label_asc','label_desc']} val={cfg.sortBy} onChange={v=>patch({sortBy:v as any})}/>
                </div>

                {/* Column pills */}
                <div>
                  <Lbl>All columns — click to assign X or Y</Lbl>
                  <div style={{display:'flex',flexWrap:'wrap',gap:5}}>
                    {activeCols.map(col=>{
                      const isX = cfg.xCol === col.name
                      const isY = cfg.yCols.includes(col.name)
                      return (
                        <button key={col.name} onClick={()=>{
                          if (col.type==='number' && !isY && cfg.xCol!==col.name) toggleYCol(col.name)
                          else if (!isX) { patch({xCol:col.name}); if(isY)patch({yCols:cfg.yCols.filter(c=>c!==col.name)}) }
                        }}
                          title={col.type==='number'?'Click to add to Y Axis':'Click to set as X Axis'}
                          style={{display:'flex',alignItems:'center',gap:4,padding:'4px 9px',borderRadius:20,fontSize:11,cursor:'pointer',background:isX?'rgba(212,175,55,.15)':isY?`${C.teal}15`:'rgba(255,255,255,.04)',border:`1px solid ${isX?'rgba(212,175,55,.4)':isY?`${C.teal}45`:'rgba(255,255,255,.08)'}`,color:isX?C.gold:isY?C.teal:'rgba(255,255,255,.55)',fontWeight:isX||isY?700:400,transition:'all .15s'}}>
                          <span style={{fontSize:10,opacity:.7}}>{col.type==='number'?'#':col.type==='date'?'📅':'A'}</span>
                          {col.name}
                          {isX&&<span style={{fontSize:9,color:C.gold,fontWeight:700}}>X</span>}
                          {isY&&<span style={{fontSize:9,color:C.teal,fontWeight:700}}>Y</span>}
                        </button>
                      )
                    })}
                  </div>
                </div>

                {/* Row limit */}
                <div style={{marginTop:10}}>
                  <Lbl>Max rows: {cfg.limit}</Lbl>
                  <input type="range" min={10} max={500} step={10} value={cfg.limit} onChange={e=>patch({limit:parseInt(e.target.value)})} style={{width:'100%',accentColor:C.gold,margin:'4px 0'}}/>
                </div>
              </>
            )}
          </Panel>

          {/* Labels / Renaming */}
          <Panel title="Labels & Renaming" icon={Tag} defaultOpen={false}>
            <p style={{fontSize:11,color:'rgba(255,255,255,.3)',marginBottom:8}}>Rename columns for display (won't affect data)</p>
            {cfg.yCols.length===0 && cfg.xCol==='' && <p style={{fontSize:11,color:'rgba(255,255,255,.2)'}}>Assign columns first</p>}
            {[cfg.xCol, ...cfg.yCols].filter(Boolean).map(col=>(
              <div key={col} style={{marginBottom:8}}>
                <Lbl>{col}</Lbl>
                <TxtInput val={cfg.colLabels[col]||''} onChange={v=>setColLabel(col,v)} placeholder={`Display name for "${col}"`}/>
              </div>
            ))}
            <div style={{marginTop:10}}>
              <Lbl>X Axis label</Lbl>
              <TxtInput val={cfg.xLabel} onChange={v=>patch({xLabel:v})} placeholder="Override X axis label"/>
            </div>
            <div style={{marginTop:8}}>
              <Lbl>Y Axis label</Lbl>
              <TxtInput val={cfg.yLabel} onChange={v=>patch({yLabel:v})} placeholder="Override Y axis label"/>
            </div>
            <div style={{marginTop:8}}>
              <Lbl>Annotation / note</Lbl>
              <TxtInput val={cfg.annotations} onChange={v=>patch({annotations:v})} placeholder="Shown below chart"/>
            </div>
          </Panel>

          {/* Filters */}
          <Panel title={`Filters${cfg.filters.filter(f=>f.active).length>0?` (${cfg.filters.filter(f=>f.active).length} active)`:''}`} icon={Filter} defaultOpen={false}>
            {cfg.filters.length===0&&<p style={{fontSize:12,color:'rgba(255,255,255,.3)',marginBottom:10}}>No filters applied</p>}
            <div style={{display:'flex',flexDirection:'column',gap:8,marginBottom:10}}>
              {cfg.filters.map((f,i)=>(
                <div key={i}>
                  <div style={{display:'grid',gridTemplateColumns:'1fr auto 1fr auto auto',gap:4,alignItems:'center'}}>
                    <SelInput opts={allCols} val={f.col} onChange={v=>patchFilter(i,{col:v})}/>
                    <SelInput opts={FILTER_OPS} val={f.op} onChange={v=>patchFilter(i,{op:v})}/>
                    {/* Smart value input */}
                    {activeCols.find(c=>c.name===f.col)?.type!=='number' ? (
                      activeCols.find(c=>c.name===f.col)?.vals && activeCols.find(c=>c.name===f.col)!.vals.length <= 30 ? (
                        <SelInput opts={activeCols.find(c=>c.name===f.col)!.vals.map(String)} val={f.val} onChange={v=>patchFilter(i,{val:v})} placeholder="value"/>
                      ) : (
                        <TxtInput val={f.val} onChange={v=>patchFilter(i,{val:v})} placeholder="value"/>
                      )
                    ) : (
                      <TxtInput val={f.val} onChange={v=>patchFilter(i,{val:v})} placeholder="number"/>
                    )}
                    {/* Active toggle */}
                    <button onClick={()=>patchFilter(i,{active:!f.active})} style={{padding:'4px 6px',borderRadius:6,border:'none',cursor:'pointer',background:f.active?'rgba(46,204,113,.15)':'rgba(255,255,255,.05)',color:f.active?C.green:'rgba(255,255,255,.3)'}}>
                      {f.active?<Check style={{width:12,height:12}}/>:<X style={{width:12,height:12}}/>}
                    </button>
                    <button onClick={()=>removeFilter(i)} style={{background:'none',border:'none',cursor:'pointer',color:C.coral,padding:4}}><Trash2 style={{width:12,height:12}}/></button>
                  </div>
                </div>
              ))}
            </div>
            <button onClick={addFilter} disabled={!allCols.length} style={{display:'flex',alignItems:'center',gap:5,padding:'6px 11px',borderRadius:8,fontSize:11,cursor:'pointer',background:'rgba(255,255,255,.05)',border:'1px solid rgba(255,255,255,.1)',color:'rgba(255,255,255,.6)'}}>
              <Plus style={{width:12,height:12}}/> Add Filter
            </button>
          </Panel>

          {/* Style */}
          <Panel title="Style" icon={Palette} defaultOpen={false}>
            <div>
              <Lbl>Color palette</Lbl>
              <div style={{display:'grid',gridTemplateColumns:'repeat(3,1fr)',gap:5}}>
                {Object.entries(PALETTES).map(([name,cols])=>(
                  <button key={name} onClick={()=>patch({palette:name})} style={{padding:'7px 5px',borderRadius:8,cursor:'pointer',background:cfg.palette===name?'rgba(255,255,255,.08)':'rgba(255,255,255,.03)',border:`1px solid ${cfg.palette===name?'rgba(212,175,55,.4)':'rgba(255,255,255,.07)'}`,display:'flex',flexDirection:'column',alignItems:'center',gap:4}}>
                    <div style={{display:'flex',gap:2}}>{cols.slice(0,4).map((c,i)=><span key={i} style={{width:10,height:10,borderRadius:'50%',background:c}}/>)}</div>
                    <span style={{fontSize:10,color:cfg.palette===name?C.gold:'rgba(255,255,255,.4)',fontWeight:cfg.palette===name?700:400}}>{name}</span>
                  </button>
                ))}
              </div>
            </div>
            <div style={{marginTop:10}}>
              <Toggle val={cfg.showGrid}   onChange={v=>patch({showGrid:v})}   label="Show grid lines"/>
              <Toggle val={cfg.showLegend} onChange={v=>patch({showLegend:v})} label="Show legend"/>
              <Toggle val={cfg.showLabels} onChange={v=>patch({showLabels:v})} label="Show value labels"/>
            </div>
          </Panel>

        </div>

        {/* ══════════ RIGHT PANEL ══════════ */}
        <div>
          {/* Chart tabs row */}
          <div style={{display:'flex',alignItems:'center',gap:6,marginBottom:14,flexWrap:'wrap'}}>
            {configs.map((c,i)=>(
              <div key={i} style={{display:'flex',alignItems:'center',gap:3}}>
                <button onClick={()=>setActiveIdx(i)} style={{padding:'6px 12px',borderRadius:8,fontSize:12,fontWeight:i===activeIdx?700:400,cursor:'pointer',background:i===activeIdx?'rgba(212,175,55,.12)':'rgba(255,255,255,.04)',border:`1px solid ${i===activeIdx?'rgba(212,175,55,.35)':'rgba(255,255,255,.08)'}`,color:i===activeIdx?C.gold:'rgba(255,255,255,.5)'}}>
                  {c.title||`Chart ${i+1}`}
                </button>
                {configs.length>1&&<button onClick={()=>removeChart(i)} style={{background:'none',border:'none',cursor:'pointer',color:'rgba(255,255,255,.25)',padding:2}}><X style={{width:11,height:11}}/></button>}
              </div>
            ))}
            {configs.length<8&&<button onClick={addChart} style={{display:'flex',alignItems:'center',gap:4,padding:'6px 11px',borderRadius:8,fontSize:12,cursor:'pointer',background:'rgba(255,255,255,.04)',border:'1px dashed rgba(255,255,255,.15)',color:'rgba(255,255,255,.4)'}}>
              <Plus style={{width:12,height:12}}/> Add View
            </button>}
          </div>

          {/* Chart canvas */}
          <div ref={chartRef} style={{background:'rgba(255,255,255,.02)',border:'1px solid rgba(255,255,255,.07)',borderRadius:16,padding:20,marginBottom:14}}>

            {/* Title & subtitle */}
            <div style={{marginBottom:12}}>
              <input value={cfg.title} onChange={e=>patch({title:e.target.value})} placeholder="Click to add chart title…" style={{width:'100%',background:'transparent',border:'none',outline:'none',fontSize:17,fontWeight:700,color:'#fff',fontFamily:'inherit',cursor:'text'}}/>
              <input value={cfg.subtitle} onChange={e=>patch({subtitle:e.target.value})} placeholder="Add subtitle or description…" style={{width:'100%',background:'transparent',border:'none',outline:'none',fontSize:12,color:'rgba(255,255,255,.4)',fontFamily:'inherit',cursor:'text',marginTop:2}}/>
            </div>

            {/* Stat pills */}
            {chartData.length>0&&(
              <div style={{display:'flex',gap:12,marginBottom:12,flexWrap:'wrap',paddingBottom:10,borderBottom:'1px solid rgba(255,255,255,.05)'}}>
                <span style={{fontSize:11,color:'rgba(255,255,255,.35)'}}><span style={{color:C.teal,fontWeight:700}}>{chartData.length}</span> data points</span>
                <span style={{fontSize:11,color:'rgba(255,255,255,.35)'}}>Showing <span style={{color:C.gold,fontWeight:700}}>{CHART_TYPES.find(c=>c.id===cfg.chartType)?.label}</span> chart</span>
                {cfg.filters.filter(f=>f.active&&f.val).length>0&&<span style={{fontSize:11,color:'rgba(255,255,255,.35)'}}><span style={{color:C.amber,fontWeight:700}}>{cfg.filters.filter(f=>f.active&&f.val).length}</span> filter{cfg.filters.filter(f=>f.active&&f.val).length>1?'s':''} active</span>}
                {cfg.yCols.length>0&&<span style={{fontSize:11,color:'rgba(255,255,255,.35)'}}>Agg: <span style={{color:C.gold,fontWeight:700}}>{cfg.aggregation}</span></span>}
                {dsA&&dsB&&<span style={{fontSize:11,color:'rgba(255,255,255,.35)'}}>Source: <span style={{color:C.purple,fontWeight:700}}>{cfg.dataset==='merge'?'Merged':cfg.dataset.toUpperCase()}</span></span>}
              </div>
            )}

            <ChartRenderer cfg={cfg} data={chartData} labels={cfg.colLabels}/>

            {/* Annotation */}
            {cfg.annotations&&<p style={{fontSize:11,color:'rgba(255,255,255,.35)',marginTop:10,fontStyle:'italic',paddingTop:8,borderTop:'1px solid rgba(255,255,255,.05)'}}>{cfg.annotations}</p>}

            {/* Action buttons */}
            <div style={{display:'flex',justifyContent:'space-between',marginTop:14,flexWrap:'wrap',gap:8}}>
              <button onClick={pinToDashboard} disabled={isPinned||!chartData.length}
                style={{display:'flex',alignItems:'center',gap:6,padding:'7px 14px',borderRadius:10,fontSize:12,fontWeight:700,cursor:isPinned?'default':'pointer',background:isPinned?'rgba(46,204,113,.12)':'rgba(212,175,55,.12)',border:`1px solid ${isPinned?'rgba(46,204,113,.3)':'rgba(212,175,55,.3)'}`,color:isPinned?C.green:C.gold,opacity:!chartData.length?.4:1}}>
                {isPinned?<><Check style={{width:13,height:13}}/>Added to Dashboard</>:<><Pin style={{width:13,height:13}}/>Add to Dashboard</>}
              </button>
              <button onClick={exportPNG} style={{display:'flex',alignItems:'center',gap:5,padding:'7px 12px',borderRadius:10,fontSize:11,cursor:'pointer',background:'rgba(255,255,255,.05)',border:'1px solid rgba(255,255,255,.1)',color:'rgba(255,255,255,.5)'}}>
                <Download style={{width:12,height:12}}/> Export PNG
              </button>
            </div>
          </div>

          {/* Data Preview Table */}
          {chartData.length>0&&(
            <div style={{background:'rgba(255,255,255,.02)',border:'1px solid rgba(255,255,255,.07)',borderRadius:14,padding:14,marginBottom:14}}>
              <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',marginBottom:10}}>
                <p style={{fontSize:12,fontWeight:700,color:C.gold,margin:0}}>📋 Data Preview <span style={{fontSize:11,color:'rgba(255,255,255,.3)',fontWeight:400}}>({chartData.length} aggregated rows)</span></p>
                <button
                  onClick={()=>{
                    const headers = Object.keys(chartData[0]).join(',')
                    const rows = chartData.map(r=>Object.values(r).join(',')).join('\n')
                    const blob = new Blob([headers+'\n'+rows],{type:'text/csv'})
                    const a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download='data_export.csv'; a.click()
                  }}
                  style={{display:'flex',alignItems:'center',gap:4,padding:'4px 9px',borderRadius:7,fontSize:10,cursor:'pointer',background:'rgba(255,255,255,.05)',border:'1px solid rgba(255,255,255,.09)',color:'rgba(255,255,255,.5)'}}>
                  <Download style={{width:10,height:10}}/> CSV
                </button>
              </div>
              <div style={{overflowX:'auto'}}>
                <table style={{width:'100%',borderCollapse:'collapse',fontSize:11}}>
                  <thead>
                    <tr>{Object.keys(chartData[0]).map(k=><th key={k} style={{padding:'6px 10px',textAlign:'left',color:'rgba(255,255,255,.4)',borderBottom:'1px solid rgba(255,255,255,.06)',whiteSpace:'nowrap',fontWeight:600}}>
                      {cfg.colLabels[k]||k}
                    </th>)}</tr>
                  </thead>
                  <tbody>
                    {chartData.slice(0,10).map((row,i)=>(
                      <tr key={i} style={{background:i%2===0?'rgba(255,255,255,.01)':'transparent'}}>
                        {Object.entries(row).map(([k,v],j)=>(
                          <td key={j} style={{padding:'6px 10px',color:'rgba(255,255,255,.65)',borderBottom:'1px solid rgba(255,255,255,.04)',whiteSpace:'nowrap'}}>
                            {typeof v==='number'?nf(v,2):String(v)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
                {chartData.length>10&&<p style={{fontSize:10,color:'rgba(255,255,255,.2)',marginTop:6}}>Showing 10 of {chartData.length} rows · Export CSV to see all</p>}
              </div>
            </div>
          )}

          {/* AI Insight */}
          <div style={{background:'rgba(212,175,55,.04)',border:'1px solid rgba(212,175,55,.15)',borderRadius:16,padding:18}}>
            <div style={{display:'flex',alignItems:'center',gap:8,marginBottom:12}}>
              <Sparkles style={{width:15,height:15,color:C.gold}}/>
              <span style={{fontSize:13,fontWeight:700,color:C.gold}}>AI Insight</span>
              <span style={{fontSize:10,padding:'2px 7px',borderRadius:20,background:'rgba(212,175,55,.12)',color:C.gold,border:'1px solid rgba(212,175,55,.2)'}}>Claude</span>
            </div>
            <div style={{display:'flex',gap:7,marginBottom:10}}>
              <input
                value={insightQ} onChange={e=>setInsightQ(e.target.value)}
                onKeyDown={e=>e.key==='Enter'&&askInsight()}
                placeholder="e.g. 'What drives the spike?' · 'Compare top vs bottom performers' · 'Any outliers?'"
                style={{flex:1,padding:'9px 12px',borderRadius:10,fontSize:12,background:'rgba(255,255,255,.06)',border:'1px solid rgba(255,255,255,.1)',color:'rgba(255,255,255,.8)',outline:'none'}}
              />
              <button onClick={askInsight} disabled={insightLoading||!insightQ.trim()||!activeRows.length}
                style={{padding:'9px 14px',borderRadius:10,fontSize:12,fontWeight:700,cursor:'pointer',background:insightLoading?'rgba(212,175,55,.3)':C.gold,border:'none',color:'#000',display:'flex',alignItems:'center',gap:5,opacity:(!insightQ.trim()||!activeRows.length)?0.5:1}}>
                {insightLoading?<RefreshCw style={{width:13,height:13,animation:'spin 1s linear infinite'}}/>:<Play style={{width:13,height:13}}/>}
                {insightLoading?'…':'Ask'}
              </button>
            </div>
            {insightRes&&(
              <div style={{padding:'12px 14px',borderRadius:10,background:'rgba(0,0,0,.3)',border:'1px solid rgba(212,175,55,.12)',fontSize:12,color:'rgba(255,255,255,.8)',lineHeight:1.75}}>
                <Zap style={{width:11,height:11,color:C.gold,marginRight:6,display:'inline'}}/>
                {insightRes}
              </div>
            )}
            {!activeRows.length&&<p style={{fontSize:12,color:'rgba(255,255,255,.3)'}}>Load a dataset to enable AI insights</p>}
          </div>
        </div>
      </div>

      <style>{`
        @keyframes spin { from { transform:rotate(0deg) } to { transform:rotate(360deg) } }
        select option { background: #141420; color: #e0e0e0; }
        ::-webkit-scrollbar { width: 4px; height: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(212,175,55,.2); border-radius: 4px; }
      `}</style>
    </div>
  )
}
