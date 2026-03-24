/**
 * VisualizationsTab — Maximum Coverage Interactive Dashboard
 * ═══════════════════════════════════════════════════════════
 * DATA SOURCES (16 total):
 *   kpis · segments · time_series · growth_rates · distributions
 *   composition · scatter · correlation_matrix · percentage_changes
 *   boxplots · ranking · outlier_detail · cohort · multi_metric
 *   percentile_bands · running_total
 *
 * CHART TYPES PER SECTION:
 *   Segments      → H-Bar / V-Bar / Pie / Donut / Treemap / Funnel / Radar
 *   Trend         → Area / Line / Bar / Composed / Step
 *   Growth        → Composed / Area / Waterfall
 *   Distribution  → Histogram / Box Plot / Area / Violin
 *   Composition   → Donut / Pie / Bar / Treemap
 *   Scatter       → Scatter (quadrant) / Bubble
 *   Correlation   → H-Bar / Intensity / Table
 *   Heatmap       → Pivot bar heatmap
 *   vs Average    → Bar / Bullet / Dot
 *   Top/Bottom    → H-Bar ranked
 *   Radar (multi) → Multi-metric spider
 *   Ranking       → Podium bar / Lollipop / Ranked H-Bar
 *   Outliers      → Severity bar / Scatter strip / Category breakdown
 *   Cohort        → Grouped Bar / Stacked Bar
 *   Multi-Metric  → Grouped Bar / Radar / Normalised Bar
 *   Percentile    → Band chart / Bar / Steps
 *   Pareto        → Composed bar+line (Pareto)
 *
 * RELEVANCE LABELS: Strong / Medium / Weak per tab + per card
 * All hooks unconditional at top level.
 */

import { useState, useMemo, useCallback } from 'react'
import {
  BarChart3, TrendingUp, Activity, Target, GitBranch,
  Layers, PieChart as PieIconLucide, Zap, Award,
  ChevronDown, ArrowUpRight, ArrowDownRight, Minus,
  Pin, Check, Hash, Eye, AlertTriangle, Plus,
  BarChart2, Grid, Trophy, ShieldAlert, Users, Sigma,
  Percent, GitMerge, Flame,
} from 'lucide-react'
import {
  ResponsiveContainer,
  BarChart, Bar,
  LineChart, Line,
  AreaChart, Area,
  ScatterChart, Scatter,
  PieChart, Pie, Cell,
  ComposedChart,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  Treemap,
  FunnelChart, Funnel, LabelList as FunnelLabel,
  CartesianGrid, XAxis, YAxis, ZAxis,
  Tooltip as RTooltip,
  Legend, ReferenceLine, Brush, LabelList,
} from 'recharts'
import { useDashboard } from '../hooks/useDashboard'
import { useCurrency } from '../hooks/useCurrency'

// ─── Types ────────────────────────────────────────────────────────────────────
type Props = { charts?: any[]; analytics: any; jobId: string; jobName: string; previewMode?: boolean }
type RelevanceLevel = 'Strong' | 'Medium' | 'Weak'
interface ChartOpt { id: string; label: string; icon: string }

// ─── Design ───────────────────────────────────────────────────────────────────
const C = {
  gold:'#D4AF37', teal:'#00CED1', coral:'#FF6B6B', purple:'#9B59B6',
  green:'#2ECC71', amber:'#F39C12', blue:'#3498DB', pink:'#E91E63',
  cyan:'#00BCD4', lime:'#8BC34A', orange:'#FF9800', indigo:'#5C6BC0',
  slate:'#607D8B', rose:'#E91E63',
}
const SEQ = [C.gold,C.teal,C.coral,C.purple,C.green,C.amber,C.blue,C.pink,C.cyan,C.lime,C.orange,C.indigo]
const FIN = /price|cost|revenue|sales|profit|amount|salary|budget|fee|income|margin|total/i
const AX  = { stroke:'rgba(255,255,255,0.06)', tick:{fill:'rgba(255,255,255,0.35)',fontSize:10} as any }
const TIER_C: Record<string,string> = { Gold:C.gold, Silver:'#94a3b8', Bronze:'#cd7f32' }
const QUAD_C: Record<string,string> = { 'High-High':C.green,'High-Low':C.amber,'Low-High':C.blue,'Low-Low':C.coral }

const REL: Record<RelevanceLevel,{bg:string;border:string;color:string;dot:string}> = {
  Strong:{ bg:'rgba(46,204,113,.10)', border:'rgba(46,204,113,.30)', color:'#2ECC71', dot:'#2ECC71' },
  Medium:{ bg:'rgba(212,175,55,.10)', border:'rgba(212,175,55,.30)', color:'#D4AF37', dot:'#D4AF37' },
  Weak:  { bg:'rgba(156,163,175,.10)',border:'rgba(156,163,175,.20)',color:'#9ca3af', dot:'#6b7280' },
}

// Chart type catalogs
const T_SEG:  ChartOpt[] = [{id:'hbar',label:'H-Bar',icon:'▬'},{id:'vbar',label:'V-Bar',icon:'▮'},{id:'pie',label:'Pie',icon:'◔'},{id:'donut',label:'Donut',icon:'◎'},{id:'treemap',label:'Treemap',icon:'▦'},{id:'funnel',label:'Funnel',icon:'▽'},{id:'radar',label:'Radar',icon:'⬡'}]
const T_TRD:  ChartOpt[] = [{id:'area',label:'Area',icon:'◿'},{id:'line',label:'Line',icon:'⌇'},{id:'bar',label:'Bar',icon:'▮'},{id:'composed',label:'Composed',icon:'⊞'},{id:'step',label:'Step',icon:'⌐'}]
const T_GRW:  ChartOpt[] = [{id:'composed',label:'Composed',icon:'⊞'},{id:'area',label:'Area',icon:'◿'},{id:'waterfall',label:'Waterfall',icon:'⧗'}]
const T_DST:  ChartOpt[] = [{id:'histogram',label:'Histogram',icon:'▮'},{id:'boxplot',label:'Box Plot',icon:'⊟'},{id:'area',label:'Area',icon:'◿'},{id:'violin',label:'Violin',icon:'◈'}]
const T_CMP:  ChartOpt[] = [{id:'donut',label:'Donut',icon:'◎'},{id:'pie',label:'Pie',icon:'◔'},{id:'bar',label:'Bar',icon:'▮'},{id:'treemap',label:'Treemap',icon:'▦'}]
const T_COR:  ChartOpt[] = [{id:'hbar',label:'Bar',icon:'▬'},{id:'intensity',label:'Intensity',icon:'▦'},{id:'table',label:'Table',icon:'≡'}]
const T_VSA:  ChartOpt[] = [{id:'bar',label:'Bar',icon:'▮'},{id:'bullet',label:'Bullet',icon:'▬'},{id:'dot',label:'Dot',icon:'●'}]
const T_RNK:  ChartOpt[] = [{id:'hbar',label:'H-Bar',icon:'▬'},{id:'lollipop',label:'Lollipop',icon:'◉'},{id:'podium',label:'Podium',icon:'▮'}]
const T_OUT:  ChartOpt[] = [{id:'severity',label:'Severity',icon:'▮'},{id:'strip',label:'Strip',icon:'●'},{id:'category',label:'By Category',icon:'▬'}]
const T_COH:  ChartOpt[] = [{id:'grouped',label:'Grouped',icon:'▮'},{id:'stacked',label:'Stacked',icon:'⊞'},{id:'heatmap',label:'Heatmap',icon:'▦'}]
const T_MMT:  ChartOpt[] = [{id:'grouped',label:'Grouped',icon:'▮'},{id:'radar',label:'Radar',icon:'⬡'},{id:'normalized',label:'Normalised',icon:'◿'}]
const T_PCT:  ChartOpt[] = [{id:'bands',label:'Bands',icon:'◈'},{id:'bar',label:'Bar',icon:'▮'},{id:'steps',label:'Steps',icon:'⌐'}]
const T_PRT:  ChartOpt[] = [{id:'pareto',label:'Pareto',icon:'⊞'},{id:'area',label:'Cumulative Area',icon:'◿'}]

// ─── Helpers ──────────────────────────────────────────────────────────────────
const nf = (v:any,d=1)=>{
  if(v==null||isNaN(+v)) return '–'
  const n=+v,a=Math.abs(n)
  if(a>=1e9) return `${(n/1e9).toFixed(d)}B`
  if(a>=1e6) return `${(n/1e6).toFixed(d)}M`
  if(a>=1e3) return `${(n/1e3).toFixed(d)}K`
  return n.toLocaleString(undefined,{maximumFractionDigits:2})
}
const pf=(v:any)=>v==null?'–':`${(+v).toFixed(1)}%`

function linReg(vals:number[],steps=6){
  const n=vals.length; if(n<4) return {fit:vals,future:[] as number[]}
  const mx=(n-1)/2, my=vals.reduce((s,v)=>s+v,0)/n
  const num=vals.reduce((s,v,i)=>s+(i-mx)*(v-my),0)
  const den=vals.reduce((s,_,i)=>s+(i-mx)**2,0)
  const sl=den?num/den:0, ic=my-sl*mx
  return { fit:vals.map((_,i)=>+(sl*i+ic).toFixed(2)), future:Array.from({length:steps},(_,i)=>+(sl*(n+i)+ic).toFixed(2)) }
}

function rel(type:string,a:any): RelevanceLevel {
  switch(type){
    case 'kpis':          return (a.kpis?.length||0)>=4?'Strong':(a.kpis?.length||0)>=1?'Medium':'Weak'
    case 'segments':      return (a.segments?.length||0)>=2?'Strong':(a.segments?.length||0)>=1?'Medium':'Weak'
    case 'trend':         return (a.time_series?.length||0)>0?'Strong':(a.growth_rates?.length||0)>0?'Medium':'Weak'
    case 'distribution':  return (a.distributions?.length||0)>=3?'Strong':(a.distributions?.length||0)>=1?'Medium':'Weak'
    case 'composition':   return (a.composition?.length||0)>=2?'Strong':(a.composition?.length||0)>=1?'Medium':'Weak'
    case 'scatter':       return (a.scatter?.filter((s:any)=>Math.abs(s.correlation||0)>=.6)?.length||0)>0?'Strong':(a.scatter?.length||0)>0?'Medium':'Weak'
    case 'correlation':   return (a.correlation_matrix?.top_correlations?.filter((c:any)=>c.abs_value>=.7)?.length||0)>0?'Strong':(a.correlation_matrix?.cells?.length||0)>0?'Medium':'Weak'
    case 'heatmap':       return (a.correlation_matrix?.columns?.length||0)>=4?'Strong':(a.correlation_matrix?.columns?.length||0)>=2?'Medium':'Weak'
    case 'vsavg':         return a.percentage_changes?.some((p:any)=>p.type==='vs_average')?'Strong':'Weak'
    case 'topbottom':     return a.percentage_changes?.some((p:any)=>p.type==='top_bottom_5')?'Strong':'Weak'
    case 'radar':         return (a.segments?.[0]?.data?.length||0)>=4?'Medium':'Weak'
    case 'ranking':       return (a.ranking?.length||0)>=1?'Strong':'Weak'
    case 'outliers':      return (a.outlier_detail?.length||0)>=2?'Strong':(a.outlier_detail?.length||0)>=1?'Medium':'Weak'
    case 'cohort':        return (a.cohort?.length||0)>=1?'Strong':'Weak'
    case 'multi_metric':  return (a.multi_metric?.length||0)>=1?'Strong':'Weak'
    case 'percentile':    return (a.percentile_bands?.length||0)>=2?'Strong':(a.percentile_bands?.length||0)>=1?'Medium':'Weak'
    case 'pareto':        return (a.running_total?.length||0)>=1?'Strong':'Weak'
    default:              return 'Medium'
  }
}

// ─── UI Atoms ─────────────────────────────────────────────────────────────────
function Tip({active,payload,label}:any){
  if(!active||!payload?.length) return null
  return(
    <div style={{background:'#10101c',border:'1px solid rgba(212,175,55,.2)',borderRadius:12,padding:'10px 14px',minWidth:160,maxWidth:260,boxShadow:'0 8px 24px rgba(0,0,0,.5)'}}>
      {label!=null&&<p style={{color:'rgba(255,255,255,.35)',fontSize:10,fontWeight:600,marginBottom:6,paddingBottom:6,borderBottom:'1px solid rgba(212,175,55,.08)'}}>{label}</p>}
      {payload.map((p:any,i:number)=>(
        <div key={i} style={{display:'flex',alignItems:'center',justifyContent:'space-between',gap:12,padding:'2px 0'}}>
          <span style={{display:'flex',alignItems:'center',gap:6,color:'rgba(255,255,255,.5)',fontSize:11}}>
            <span style={{width:8,height:8,borderRadius:'50%',background:p.color??p.fill??C.gold,flexShrink:0}}/>
            {p.name}
          </span>
          <span style={{color:'#fff',fontWeight:700,fontSize:11}}>
            {typeof p.value==='number'?nf(p.value):String(p.value??'–')}
          </span>
        </div>
      ))}
    </div>
  )
}

function Empty({msg}:{msg:string}){
  return(
    <div style={{height:120,display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',gap:8}}>
      <BarChart3 style={{width:28,height:28,opacity:.15}}/>
      <span style={{fontSize:12,color:'rgba(255,255,255,.25)'}}>{msg}</span>
    </div>
  )
}

function Insight({icon:Icon=Zap,color=C.gold,text}:{icon?:any;color?:string;text:string}){
  if(!text) return null
  return(
    <div style={{marginTop:10,display:'flex',gap:7,padding:'9px 12px',borderRadius:10,background:`${color}0d`,border:`1px solid ${color}25`,color,fontSize:11,lineHeight:1.6}}>
      <Icon style={{width:12,height:12,flexShrink:0,marginTop:2}}/>{text}
    </div>
  )
}

function Badge({level}:{level:RelevanceLevel}){
  const s=REL[level]
  return(
    <div style={{display:'flex',alignItems:'center',gap:5,padding:'3px 9px',borderRadius:20,background:s.bg,border:`1px solid ${s.border}`,fontSize:10,fontWeight:700,color:s.color}}>
      <span style={{width:6,height:6,borderRadius:'50%',background:s.dot,flexShrink:0}}/>{level}
    </div>
  )
}

function TypePicker({opts,val,onChange}:{opts:ChartOpt[];val:string;onChange:(v:string)=>void}){
  const [open,setOpen]=useState(false)
  const cur=opts.find(o=>o.id===val)||opts[0]
  return(
    <div style={{position:'relative'}}>
      <button onClick={()=>setOpen(v=>!v)} style={{display:'flex',alignItems:'center',gap:5,padding:'5px 10px',borderRadius:8,fontSize:11,cursor:'pointer',background:'rgba(255,255,255,.05)',border:'1px solid rgba(255,255,255,.08)',color:'rgba(255,255,255,.6)'}}>
        <span style={{fontSize:13}}>{cur.icon}</span>{cur.label}<ChevronDown style={{width:10,height:10}}/>
      </button>
      {open&&(<>
        <div style={{position:'fixed',inset:0,zIndex:40}} onClick={()=>setOpen(false)}/>
        <div style={{position:'absolute',right:0,top:'100%',marginTop:4,zIndex:50,minWidth:160,background:'#141420',border:'1px solid rgba(212,175,55,.15)',borderRadius:12,overflow:'hidden',boxShadow:'0 12px 32px rgba(0,0,0,.6)'}}>
          {opts.map(o=>(
            <button key={o.id} onClick={()=>{onChange(o.id);setOpen(false)}} style={{width:'100%',display:'flex',alignItems:'center',gap:8,padding:'9px 12px',fontSize:12,cursor:'pointer',background:val===o.id?'rgba(212,175,55,.1)':'transparent',color:val===o.id?C.gold:'rgba(255,255,255,.55)',border:'none',borderBottom:'1px solid rgba(255,255,255,.04)',textAlign:'left'}}>
              <span style={{fontSize:14,width:20,textAlign:'center'}}>{o.icon}</span>{o.label}
              {val===o.id&&<Check style={{width:10,height:10,marginLeft:'auto',color:C.gold}}/>}
            </button>
          ))}
        </div>
      </>)}
    </div>
  )
}

function Sel({opts,val,onChange}:{opts:string[];val:string;onChange:(v:string)=>void}){
  return(
    <div style={{position:'relative',display:'inline-block'}}>
      <select value={val} onChange={e=>onChange(e.target.value)} style={{padding:'5px 26px 5px 9px',borderRadius:8,fontSize:11,cursor:'pointer',background:'rgba(255,255,255,.05)',border:'1px solid rgba(255,255,255,.08)',color:'rgba(255,255,255,.6)',appearance:'none',outline:'none'}}>
        {opts.map(o=><option key={o} value={o}>{o}</option>)}
      </select>
      <ChevronDown style={{position:'absolute',right:6,top:'50%',transform:'translateY(-50%)',width:11,height:11,color:'rgba(255,255,255,.3)',pointerEvents:'none'}}/>
    </div>
  )
}

function Card({title,sub,icon:Icon,col=C.gold,bar,children,onPin,pinned,relevance}:{
  title:string;sub?:string;icon?:any;col?:string;bar?:React.ReactNode;children:React.ReactNode;
  onPin?:()=>void;pinned?:boolean;relevance?:RelevanceLevel
}){
  return(
    <div style={{background:'rgba(255,255,255,.02)',border:'1px solid rgba(255,255,255,.06)',borderRadius:16,overflow:'hidden',marginBottom:16}}>
      <div style={{padding:'13px 18px',borderBottom:'1px solid rgba(255,255,255,.04)',display:'flex',alignItems:'center',justifyContent:'space-between',gap:12,flexWrap:'wrap'}}>
        <div style={{display:'flex',alignItems:'center',gap:10}}>
          {Icon&&<div style={{width:30,height:30,borderRadius:8,display:'flex',alignItems:'center',justifyContent:'center',background:`${col}18`,flexShrink:0}}><Icon style={{width:15,height:15,color:col}}/></div>}
          <div>
            <p style={{fontSize:13,fontWeight:600,color:'#fff',margin:0}}>{title}</p>
            {sub&&<p style={{fontSize:11,color:'rgba(255,255,255,.35)',margin:'2px 0 0'}}>{sub}</p>}
          </div>
          {relevance&&<Badge level={relevance}/>}
        </div>
        <div style={{display:'flex',alignItems:'center',gap:8,flexWrap:'wrap'}}>
          {bar}
          {onPin&&<button onClick={onPin} style={{display:'flex',alignItems:'center',gap:5,padding:'5px 10px',borderRadius:8,fontSize:11,fontWeight:600,cursor:pinned?'default':'pointer',background:pinned?'rgba(46,204,113,.12)':'rgba(212,175,55,.1)',border:`1px solid ${pinned?'rgba(46,204,113,.3)':'rgba(212,175,55,.3)'}`,color:pinned?C.green:C.gold}}>
            {pinned?<><Check style={{width:11,height:11}}/>Added</>:<><Plus style={{width:11,height:11}}/>Dashboard</>}
          </button>}
        </div>
      </div>
      <div style={{padding:18}}>{children}</div>
    </div>
  )
}

function TreemapNode(props:any){
  const{x,y,width,height,name,value,fill}=props
  if(!width||!height||width<30||height<20) return null
  return(
    <g>
      <rect x={x+1} y={y+1} width={width-2} height={height-2} style={{fill,fillOpacity:.8,stroke:'rgba(0,0,0,.3)',strokeWidth:1}} rx={3}/>
      {width>60&&height>30&&(<>
        <text x={x+width/2} y={y+height/2-6} textAnchor="middle" fill="#fff" fontSize={Math.min(12,width/8)} fontWeight={600} style={{pointerEvents:'none'}}>{String(name||'').slice(0,12)}</text>
        <text x={x+width/2} y={y+height/2+10} textAnchor="middle" fill="rgba(255,255,255,.6)" fontSize={Math.min(10,width/10)} style={{pointerEvents:'none'}}>{nf(value)}</text>
      </>)}
    </g>
  )
}

// ═══════════════════════════════════════════════════════════════════════════════
// MAIN COMPONENT
// ═══════════════════════════════════════════════════════════════════════════════
export function VisualizationsTab({analytics,jobId,jobName,previewMode=false}:Props){
  // ── ALL HOOKS UNCONDITIONAL ──────────────────────────────────────────────
  const {addItem,hasItem}=useDashboard()
  const {format:fmtCur,currency}=useCurrency()

  const [tab,        setTab]        = useState('all')
  const [segDimIdx,  setSegDimIdx]  = useState(0)
  const [segMetIdx,  setSegMetIdx]  = useState(0)
  const [segType,    setSegType]    = useState('hbar')
  const [distIdx,    setDistIdx]    = useState(0)
  const [distType,   setDistType]   = useState('histogram')
  const [compIdx,    setCompIdx]    = useState(0)
  const [compType,   setCompType]   = useState('donut')
  const [scIdx,      setScIdx]      = useState(0)
  const [showQuad,   setShowQuad]   = useState(true)
  const [trendType,  setTrendType]  = useState('area')
  const [showFcast,  setShowFcast]  = useState(false)
  const [grIdx,      setGrIdx]      = useState(0)
  const [grType,     setGrType]     = useState('composed')
  const [corrType,   setCorrType]   = useState('hbar')
  const [vsAvgType,  setVsAvgType]  = useState('bar')
  const [kpiSort,    setKpiSort]    = useState('priority')
  const [hmMetric,   setHmMetric]   = useState(0)
  const [rnkIdx,     setRnkIdx]     = useState(0)
  const [rnkType,    setRnkType]    = useState('hbar')
  const [outIdx,     setOutIdx]     = useState(0)
  const [outType,    setOutType]    = useState('severity')
  const [cohIdx,     setCohIdx]     = useState(0)
  const [cohType,    setCohType]    = useState('grouped')
  const [mmIdx,      setMmIdx]      = useState(0)
  const [mmType,     setMmType]     = useState('grouped')
  const [pctIdx,     setPctIdx]     = useState(0)
  const [pctType,    setPctType]    = useState('bands')
  const [prtIdx,     setPrtIdx]     = useState(0)
  const [prtType,    setPrtType]    = useState('pareto')

  // ── Extra render-function states (must be top-level hooks) ───────────────
  const [varIdx,     setVarIdx]     = useState(0)
  const [msIdx,      setMsIdx]      = useState(0)
  const [cIdx,       setCIdx]       = useState(0)
  const [fIdx,       setFIdx]       = useState(0)
  const [tdIdx,      setTdIdx]      = useState(0)
  const [gIdx,       setGIdx]       = useState(0)
  const [slIdx,      setSlIdx]      = useState(0)
  const [ebIdx,      setEbIdx]      = useState(0)
  const [mmIdx_,     setMmIdx_]     = useState(0)
  const [gnIdx,      setGnIdx]      = useState(0)
  const [skIdx,      setSkIdx]      = useState(0)
  const [dtIdx,      setDtIdx]      = useState(0)
  const [dtSelected, setDtSelected] = useState<string|null>(null)

  // ── Data ─────────────────────────────────────────────────────────────────
  const a   = analytics||{}
  const kpis= useMemo(()=>a.kpis||[],[a])
  const segs= useMemo(()=>a.segments||[],[a])
  const dists=useMemo(()=>a.distributions||[],[a])
  const ts  = useMemo(()=>a.time_series||[],[a])
  const gr  = useMemo(()=>a.growth_rates||[],[a])
  const sct = useMemo(()=>a.scatter||[],[a])
  const comp= useMemo(()=>a.composition||[],[a])
  const pctC= useMemo(()=>a.percentage_changes||[],[a])
  const cm  = useMemo(()=>a.correlation_matrix||{},[a])
  const meta= useMemo(()=>a.meta||{},[a])
  const rnk = useMemo(()=>a.ranking||[],[a])
  const out = useMemo(()=>a.outlier_detail||[],[a])
  const coh = useMemo(()=>a.cohort||[],[a])
  const mm  = useMemo(()=>a.multi_metric||[],[a])
  const pbd = useMemo(()=>a.percentile_bands||[],[a])
  const prt = useMemo(()=>a.running_total||[],[a])

  const corrCells=useMemo(()=>(cm.cells||[]).filter((c:any)=>c.x!==c.y),[cm])
  const corrPairs=useMemo(()=>{
    const seen=new Set<string>()
    return corrCells.reduce((acc:any[],c:any)=>{
      const key=[c.x,c.y].sort().join('|')
      if(!seen.has(key)){seen.add(key);acc.push({...c,label:`${c.x.slice(0,13)} ↔ ${c.y.slice(0,13)}`})}
      return acc
    },[]).sort((a:any,b:any)=>b.abs_value-a.abs_value).slice(0,14)
  },[corrCells])

  const hmCols=useMemo(()=>cm.columns?.slice(0,8)||[],[cm])
  const hmData=useMemo(()=>{
    if(!hmCols.length) return []
    const col=hmCols[hmMetric%hmCols.length]
    return hmCols.map((row:string)=>{
      const cell=corrCells.find((c:any)=>(c.x===row&&c.y===col)||(c.x===col&&c.y===row))
      const v=row===col?1:(cell?.value??0)
      return{name:row.slice(0,12),value:v,abs:Math.abs(v)}
    })
  },[corrCells,hmCols,hmMetric])

  const segDims=useMemo(()=>[...new Set(segs.map((s:any)=>s.display_dimension))] as string[],[segs])
  const segMets=useMemo(()=>segs.filter((s:any)=>s.display_dimension===segDims[segDimIdx]).map((s:any)=>s.display_metric),[segs,segDims,segDimIdx])
  const activeSeg=useMemo(()=>segs.filter((s:any)=>s.display_dimension===segDims[segDimIdx])[segMetIdx]||segs[0],[segs,segDims,segDimIdx,segMetIdx])
  const segData=useMemo(()=>(activeSeg?.data||[]).slice(0,15),[activeSeg])

  const tsItem=ts[0]
  const tsData=useMemo(()=>tsItem?.data||[],[tsItem])
  const tsMets=useMemo(()=>tsItem?.metrics||[],[tsItem])
  const trendData=useMemo(()=>{
    if(!showFcast||!tsData.length||!tsMets.length) return tsData
    const key=tsMets[0]?.key; if(!key) return tsData
    const vals=tsData.map((d:any)=>d[key]).filter((v:any)=>v!=null&&!isNaN(+v))
    if(vals.length<4) return tsData
    const{fit,future}=linReg(vals,6)
    return [...tsData.map((d:any,i:number)=>({...d,_fit:fit[i]})), ...future.map((v,i)=>({period:`▶${i+1}`,_forecast:v}))]
  },[showFcast,tsData,tsMets])

  const grItem=gr[grIdx]||null
  const grData=useMemo(()=>(grItem?.periods||[]).slice(0,40),[grItem])
  const grWF  =useMemo(()=>{let r=0;return grData.map((d:any)=>{r+=(d.growth_rate_pct??0);return{...d,_cum:r,_pos:(d.growth_rate_pct??0)>=0}})},[grData])

  const scItem=sct[scIdx]||null
  const scData=useMemo(()=>scItem?.data||[],[scItem])
  const scCats=useMemo(()=>[...new Set(scData.map((d:any)=>d.category).filter(Boolean))] as string[],[scData])
  const scLabels=useMemo(()=>sct.map((s:any,i:number)=>`${s.display_x?.slice(0,12)} × ${s.display_y?.slice(0,12)}`),[sct])

  const vsAvg=useMemo(()=>pctC.find((x:any)=>x.type==='vs_average'),[pctC])
  const vsAvgD=useMemo(()=>(vsAvg?.data||[]).slice(0,15),[vsAvg])
  const tb=useMemo(()=>pctC.find((x:any)=>x.type==='top_bottom_5'),[pctC])
  const tbData=useMemo(()=>[...(tb?.top_5||[]).map((d:any)=>({...d,_g:'Top'})),...(tb?.bottom_5||[]).slice().reverse().map((d:any)=>({...d,_g:'Bottom'}))]  ,[tb])

  const radarData=useMemo(()=>(segs[0]?.data||[]).slice(0,8).map((d:any)=>({subject:String(d.category||'').slice(0,12),total:d.total??0,mean:d.mean??0})),[segs])

  const rnkItem=rnk[rnkIdx]||null
  const rnkData=useMemo(()=>(rnkItem?.data||[]).slice(0,20),[rnkItem])

  const outItem=out[outIdx]||null
  const cohItem=coh[cohIdx]||null
  const cohLabels=useMemo(()=>cohItem?.col_labels||[],[cohItem])
  const mmItem=mm[mmIdx]||null
  const pctItem=pbd[pctIdx]||null
  const prtItem=prt[prtIdx]||null

  const sortedKpis=useMemo(()=>{
    const l=[...kpis]
    if(kpiSort==='value') return l.sort((a,b)=>(b.value??0)-(a.value??0))
    if(kpiSort==='change') return l.sort((a,b)=>Math.abs(b.pct_change??0)-Math.abs(a.pct_change??0))
    return l
  },[kpis,kpiSort])

  const fmtKpi=useCallback((kpi:any)=>{
    if(FIN.test(kpi.metric||kpi.name||'')&&typeof kpi.value==='number') return fmtCur(kpi.value)
    return kpi.formatted_value??nf(kpi.value)
  },[fmtCur,currency])

  const pin=useCallback((title:string,subtype:string,slice:any,cfg?:any)=>{
    if(hasItem(jobId,title)) return
    addItem({jobId,jobName,type:'recharts',subtype,title,analyticsSlice:slice,chartConfig:cfg})
  },[jobId,jobName,addItem,hasItem])

  const pinKpi=useCallback((kpi:any)=>{
    const t=kpi.display_name||kpi.name
    if(!hasItem(jobId,t)) addItem({jobId,jobName,type:'kpi',subtype:'kpi',title:t,data:kpi})
  },[jobId,jobName,addItem,hasItem])

  // ── Tab definitions ───────────────────────────────────────────────────────
  const TABS=useMemo(()=>[
    {id:'all',         label:'All',           icon:BarChart3,     always:true},
    {id:'kpis',        label:'KPIs',           icon:Target,        show:kpis.length>0},
    {id:'segments',    label:'Segments',       icon:BarChart2,     show:segs.length>0},
    {id:'trend',       label:'Trend',          icon:TrendingUp,    show:ts.length>0||gr.length>0},
    {id:'distribution',label:'Distribution',   icon:Activity,      show:dists.length>0},
    {id:'composition', label:'Composition',    icon:PieIconLucide, show:comp.length>0},
    {id:'scatter',     label:'Scatter',        icon:GitBranch,     show:sct.length>0},
    {id:'correlation', label:'Correlation',    icon:Layers,        show:corrPairs.length>0},
    {id:'heatmap',     label:'Heatmap',        icon:Grid,          show:hmCols.length>=3},
    {id:'vsavg',       label:'vs Average',     icon:Zap,           show:vsAvgD.length>0},
    {id:'topbottom',   label:'Top/Bottom',     icon:Award,         show:tbData.length>0},
    {id:'radar',       label:'Radar',          icon:Eye,           show:radarData.length>=3},
    {id:'ranking',     label:'Ranking',        icon:Trophy,        show:rnk.length>0},
    {id:'outliers',    label:'Outliers',       icon:ShieldAlert,   show:out.length>0},
    {id:'cohort',      label:'Cohort',         icon:Users,         show:coh.length>0},
    {id:'multi_metric',label:'Multi-Metric',   icon:Sigma,         show:mm.length>0},
    {id:'percentile',  label:'Percentiles',    icon:Percent,       show:pbd.length>0},
    {id:'pareto',      label:'Pareto',         icon:GitMerge,      show:prt.length>0},
    {id:'var',         label:'Risk/VaR',        icon:ShieldAlert,   show:(a.value_at_risk||[]).length>0},
    {id:'moving',      label:'Moving Avg',      icon:TrendingUp,    show:(a.moving_statistics||[]).length>0},
    {id:'concentration',label:'Concentration',  icon:GitMerge,      show:(a.concentration||[]).length>0},
    {id:'benchmark',   label:'Benchmarks',      icon:Award,         show:(a.benchmark_comparison||[]).length>0},
    {id:'quality',     label:'Quality',         icon:ShieldAlert,   show:(a.data_quality_detail||[]).length>0},
    {id:'stats_table', label:'Stats Table',     icon:Sigma,         show:(a.summary_stats||[]).length>0},
    {id:'frequency',   label:'Frequency',       icon:BarChart3,     show:(a.frequency_analysis||[]).length>0},
    {id:'decomp',      label:'Decomposition',   icon:TrendingUp,    show:(a.time_decomposition||[]).length>0},
    {id:'gauge',       label:'Gauge/Bullet',    icon:Target,        show:(a.gauge||[]).length>0},
    {id:'slope',       label:'Slope/Dumbbell',  icon:TrendingUp,    show:(a.slope_chart||[]).length>0},
    {id:'errorbars',   label:'Error Bars',      icon:Activity,      show:(a.error_bars||[]).length>0},
    {id:'marimekko',   label:'Marimekko',       icon:Grid,          show:(a.marimekko||[]).length>0},
    {id:'gantt',       label:'Gantt',           icon:TrendingUp,    show:(a.gantt||[]).length>0},
    {id:'sankey',      label:'Flow/Sankey',      icon:GitMerge,      show:(a.sankey||[]).length>0},
    {id:'drill',       label:'Drill-Through',   icon:Eye,           show:(a.drill_through||[]).length>0},
    {id:'meta',        label:'Info',           icon:Hash,          show:!!meta.total_rows},
  ].filter((t:any)=>t.always||t.show),[kpis,segs,ts,gr,dists,comp,sct,corrPairs,hmCols,vsAvgD,tbData,radarData,rnk,out,coh,mm,pbd,prt,meta,a])  // a covers gantt/sankey/drill_through

  // ── Guard ─────────────────────────────────────────────────────────────────
  if(!analytics) return(
    <div style={{padding:48,textAlign:'center'}}>
      <Activity style={{width:40,height:40,opacity:.15,margin:'0 auto 12px'}}/>
      <p style={{color:'rgba(255,255,255,.35)'}}>Interactive charts appear after analysis completes.</p>
    </div>
  )

  // ═══════════════════════════════════════════════════════════════════════════
  // RENDER FUNCTIONS
  // ═══════════════════════════════════════════════════════════════════════════

  // ── KPIs ──────────────────────────────────────────────────────────────────
  function renderKpis(){
    if(!kpis.length) return <Empty msg="No KPIs"/>
    const rv=rel('kpis',a)
    return(
      <Card title="KPI Overview" sub={`${kpis.length} metrics · ${currency}`} icon={Target} col={C.gold} relevance={rv}
        onPin={()=>pin('KPI Overview','kpis',{kpis:sortedKpis.slice(0,9)})} pinned={hasItem(jobId,'KPI Overview')}
        bar={<div style={{display:'flex',gap:3,padding:3,background:'rgba(255,255,255,.04)',borderRadius:8}}>{['priority','value','change'].map(s=>(<button key={s} onClick={()=>setKpiSort(s)} style={{padding:'4px 10px',borderRadius:6,fontSize:11,cursor:'pointer',background:kpiSort===s?'rgba(212,175,55,.15)':'transparent',border:kpiSort===s?'1px solid rgba(212,175,55,.35)':'1px solid transparent',color:kpiSort===s?C.gold:'rgba(255,255,255,.4)'}}>{s}</button>))}</div>}>
        <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fill,minmax(190px,1fr))',gap:12}}>
          {sortedKpis.slice(0,9).map((kpi:any,i:number)=>{
            const col=SEQ[i%SEQ.length],pct=kpi.pct_change,isPos=(pct??0)>0,isFlat=Math.abs(pct??0)<.5,pinned=hasItem(jobId,kpi.display_name||kpi.name),sparks=(kpi.sparkline||[]).map((v:number,si:number)=>({si,v}))
            return(
              <div key={i} style={{padding:14,borderRadius:12,background:'rgba(255,255,255,.02)',border:`1px solid ${col}22`,position:'relative',overflow:'hidden'}}>
                <div style={{position:'absolute',inset:0,background:`radial-gradient(ellipse at 80% 0%,${col}09,transparent 70%)`,pointerEvents:'none'}}/>
                <div style={{display:'flex',justifyContent:'space-between',marginBottom:8}}>
                  <p style={{fontSize:11,color:'rgba(255,255,255,.4)',flex:1,lineHeight:1.3}}>{kpi.display_name||kpi.metric}</p>
                  {pct!=null&&<span style={{fontSize:10,fontWeight:700,padding:'2px 6px',borderRadius:6,display:'flex',alignItems:'center',gap:2,flexShrink:0,color:isFlat?'#9ca3af':isPos?'#34d399':'#f87171',background:isFlat?'rgba(255,255,255,.05)':isPos?'rgba(52,211,153,.1)':'rgba(248,113,113,.1)'}}>{isFlat?<Minus style={{width:10,height:10}}/>:isPos?<ArrowUpRight style={{width:10,height:10}}/>:<ArrowDownRight style={{width:10,height:10}}/>}{Math.abs(pct).toFixed(1)}%</span>}
                </div>
                <p style={{fontSize:22,fontWeight:900,color:col,margin:'2px 0'}}>{fmtKpi(kpi)}</p>
                {sparks.length>2&&<div style={{height:32,margin:'6px -4px'}}><ResponsiveContainer width="100%" height="100%"><AreaChart data={sparks}><defs><linearGradient id={`spk${i}`} x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={col} stopOpacity={.4}/><stop offset="100%" stopColor={col} stopOpacity={0}/></linearGradient></defs><Area type="monotone" dataKey="v" stroke={col} strokeWidth={1.5} fill={`url(#spk${i})`} dot={false}/></AreaChart></ResponsiveContainer></div>}
                <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginTop:4}}>
                  <span style={{fontSize:10,color:'rgba(255,255,255,.2)'}}>Σ {kpi.formatted_total||nf(kpi.total)}</span>
                  <button onClick={()=>pinKpi(kpi)} style={{display:'flex',alignItems:'center',gap:4,padding:'3px 8px',borderRadius:6,fontSize:10,cursor:'pointer',background:pinned?'rgba(46,204,113,.1)':'rgba(212,175,55,.08)',border:`1px solid ${pinned?'rgba(46,204,113,.25)':'rgba(212,175,55,.2)'}`,color:pinned?C.green:C.gold}}>{pinned?<><Check style={{width:9,height:9}}/>Pinned</>:<><Pin style={{width:9,height:9}}/>Pin</>}</button>
                </div>
              </div>
            )
          })}
        </div>
      </Card>
    )
  }

  // ── Segments ──────────────────────────────────────────────────────────────
  function renderSegments(){
    if(!segs.length) return <Empty msg="No segments"/>
    const rv=rel('segments',a)
    const insight=(()=>{if(!segData.length) return '';const s=[...segData].sort((a:any,b:any)=>(b.total??0)-(a.total??0));const top=s[0],bot=s[s.length-1];if(!top||!bot) return '';return `Top: "${top.category}" (${nf(top.total)}) · Bottom: "${bot.category}" (${nf(bot.total)})`})()
    const tmData=segData.map((d:any,i:number)=>({name:d.category,size:Math.abs(d.total||1),value:d.total,fill:d.direction==='above'?C.green:SEQ[i%SEQ.length]}))
    const fnData=[...segData].sort((a:any,b:any)=>(b.total||0)-(a.total||0)).slice(0,8).map((d:any,i:number)=>({name:d.category,value:Math.abs(d.total||0),fill:SEQ[i%SEQ.length]}))
    const rdData=segData.slice(0,7).map((d:any)=>({subject:String(d.category||'').slice(0,10),value:d.mean||0,total:d.total||0}))
    return(
      <Card title="Segment Analysis" sub={`${activeSeg?.display_dimension||'—'} × ${activeSeg?.display_metric||'—'}`} icon={BarChart2} col={C.green} relevance={rv}
        onPin={()=>pin(`Segments: ${activeSeg?.display_dimension}×${activeSeg?.display_metric}`,'segments',{segments:[activeSeg],meta})} pinned={hasItem(jobId,`Segments: ${activeSeg?.display_dimension}×${activeSeg?.display_metric}`)}
        bar={<>{segDims.length>1&&<Sel opts={segDims} val={segDims[segDimIdx]||''} onChange={v=>{setSegDimIdx(segDims.indexOf(v));setSegMetIdx(0)}}/> }{segMets.length>1&&<Sel opts={segMets} val={segMets[segMetIdx]||''} onChange={v=>setSegMetIdx(segMets.indexOf(v))}/>}<TypePicker opts={T_SEG} val={segType} onChange={setSegType}/></>}>
        {segType==='treemap'?(<div style={{height:280}}><ResponsiveContainer width="100%" height="100%"><Treemap data={tmData} dataKey="size" aspectRatio={4/3} content={<TreemapNode/>}><RTooltip content={({active,payload}:any)=>{if(!active||!payload?.[0]) return null;const d=payload[0].payload;return<div style={{background:'#10101c',border:'1px solid rgba(212,175,55,.2)',borderRadius:8,padding:'8px 12px',fontSize:11}}><b style={{color:'#fff'}}>{d.name}</b><br/><span style={{color:C.gold}}>{nf(d.value)}</span></div>}}/></Treemap></ResponsiveContainer></div>)
        :segType==='funnel'?(<div style={{height:280}}><ResponsiveContainer width="100%" height="100%"><FunnelChart><RTooltip content={<Tip/>}/><Funnel dataKey="value" data={fnData} isAnimationActive><FunnelLabel type="trapezoid" position="right" content={({value,name}:any)=><text fill="rgba(255,255,255,.5)" fontSize={10}>{`${String(name).slice(0,12)}: ${nf(value)}`}</text>}/></Funnel></FunnelChart></ResponsiveContainer></div>)
        :segType==='radar'?(<div style={{height:280}}><ResponsiveContainer width="100%" height="100%"><RadarChart data={rdData}><PolarGrid stroke="rgba(255,255,255,.08)"/><PolarAngleAxis dataKey="subject" tick={{fill:'rgba(255,255,255,.4)',fontSize:10}}/><PolarRadiusAxis tick={{fill:'rgba(255,255,255,.2)',fontSize:7}}/><Radar name={activeSeg?.display_metric||'Value'} dataKey="value" stroke={C.gold} fill={C.gold} fillOpacity={.15} strokeWidth={2}/><RTooltip content={<Tip/>}/></RadarChart></ResponsiveContainer></div>)
        :(segType==='pie'||segType==='donut')?(<div style={{display:'flex',gap:16,alignItems:'center'}}><div style={{height:240,flex:'0 0 220px'}}><ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={segData} dataKey="total" nameKey="category" outerRadius={90} innerRadius={segType==='donut'?44:0} paddingAngle={2} startAngle={90} endAngle={-270}>{segData.map((_:any,i:number)=><Cell key={i} fill={SEQ[i%SEQ.length]}/>)}</Pie><RTooltip content={<Tip/>}/><Legend wrapperStyle={{fontSize:10}}/></PieChart></ResponsiveContainer></div><div style={{flex:1,display:'flex',flexDirection:'column',gap:5}}>{segData.slice(0,8).map((d:any,i:number)=>(<div key={i} style={{display:'flex',alignItems:'center',justifyContent:'space-between',fontSize:12}}><span style={{display:'flex',alignItems:'center',gap:6,color:'rgba(255,255,255,.5)'}}><span style={{width:8,height:8,borderRadius:'50%',background:SEQ[i%SEQ.length],flexShrink:0}}/><span style={{overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap',maxWidth:120}}>{d.category}</span></span><span style={{fontWeight:700,color:'#fff',flexShrink:0}}>{pf(d.share_pct)}</span></div>))}</div></div>)
        :segType==='vbar'?(<div style={{height:Math.max(260,segData.length*34)}}><ResponsiveContainer width="100%" height="100%"><BarChart data={segData} margin={{top:5,right:10,bottom:55,left:0}}><CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false}/><XAxis dataKey="category" {...AX} tick={({x,y,payload}:any)=><text x={x} y={y+6} textAnchor="end" fontSize={9} fill="rgba(255,255,255,.3)" transform={`rotate(-30,${x},${y})`}>{String(payload.value).slice(0,14)}</text>} height={55}/><YAxis {...AX} tickFormatter={v=>nf(v,0)}/><RTooltip content={<Tip/>}/>{activeSeg?.overall_mean&&<ReferenceLine y={activeSeg.overall_mean} stroke={`${C.amber}80`} strokeDasharray="4 2"/>}<Bar dataKey="total" name={activeSeg?.display_metric} radius={[4,4,0,0]}>{segData.map((d:any,i:number)=><Cell key={i} fill={d.direction==='above'?C.green:C.coral} opacity={.8}/>)}</Bar></BarChart></ResponsiveContainer></div>)
        :(<div style={{height:Math.max(240,segData.length*34)}}><ResponsiveContainer width="100%" height="100%"><BarChart data={segData} layout="vertical" margin={{left:110,right:60,top:5,bottom:5}}><CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" horizontal={false}/><XAxis type="number" {...AX} tickFormatter={v=>nf(v,0)}/><YAxis type="category" dataKey="category" {...AX} width={105}/><RTooltip content={<Tip/>}/>{activeSeg?.overall_mean&&<ReferenceLine x={activeSeg.overall_mean} stroke={`${C.amber}80`} strokeDasharray="4 2"/>}<Bar dataKey="total" name={activeSeg?.display_metric} radius={[0,4,4,0]} maxBarSize={24}>{segData.map((d:any,i:number)=><Cell key={i} fill={d.direction==='above'?C.green:C.coral} opacity={.8}/>)}<LabelList dataKey="formatted_total" position="right" style={{fontSize:9,fill:'rgba(255,255,255,.3)'}}/></Bar></BarChart></ResponsiveContainer></div>)}
        <Insight text={insight}/>
      </Card>
    )
  }

  // ── Trend ─────────────────────────────────────────────────────────────────
  function renderTrend(){
    const hasTrend=ts.length>0&&tsData.length>0, hasGrowth=gr.length>0&&grData.length>0
    if(!hasTrend&&!hasGrowth) return <Empty msg="No time series — need date column"/>
    const rv=rel('trend',a)
    return(<>
      {hasTrend&&(
        <Card title="Trend Analysis" sub={`${tsItem?.period||''} · ${tsData.length} periods`} icon={TrendingUp} col={C.teal} relevance={rv}
          onPin={()=>pin('Trend Analysis','trend',{time_series:ts,meta})} pinned={hasItem(jobId,'Trend Analysis')}
          bar={<><TypePicker opts={T_TRD} val={trendType} onChange={setTrendType}/>{tsData.length>=4&&<button onClick={()=>setShowFcast(!showFcast)} style={{padding:'5px 10px',borderRadius:8,fontSize:11,cursor:'pointer',background:showFcast?'rgba(52,152,219,.15)':'rgba(255,255,255,.05)',border:`1px solid ${showFcast?C.blue+'40':'rgba(255,255,255,.08)'}`,color:showFcast?C.blue:'rgba(255,255,255,.4)'}}>{showFcast?'✓ Forecast':'+ Forecast'}</button>}</>}>
          <div style={{height:300}}>
            <ResponsiveContainer width="100%" height="100%">
              {trendType==='bar'?(<BarChart data={trendData} margin={{top:5,right:10,bottom:5,left:0}}><CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false}/><XAxis dataKey="period" {...AX}/><YAxis {...AX} tickFormatter={v=>nf(v,0)}/><RTooltip content={<Tip/>}/><Legend wrapperStyle={{fontSize:11}}/><Brush dataKey="period" height={14} stroke="rgba(255,255,255,.06)" fill="#0f0f1a" travellerWidth={4}/>{tsMets.map((m:any,j:number)=><Bar key={m.key} dataKey={m.key} name={m.display_name} fill={SEQ[j%SEQ.length]} radius={[3,3,0,0]} maxBarSize={32}/>)}{showFcast&&<Bar dataKey="_forecast" name="Forecast" fill={`${C.blue}50`} radius={[3,3,0,0]} maxBarSize={32}/>}</BarChart>)
              :trendType==='step'?(<LineChart data={trendData} margin={{top:5,right:10,bottom:5,left:0}}><CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false}/><XAxis dataKey="period" {...AX}/><YAxis {...AX} tickFormatter={v=>nf(v,0)}/><RTooltip content={<Tip/>}/><Legend wrapperStyle={{fontSize:11}}/><Brush dataKey="period" height={14} stroke="rgba(255,255,255,.06)" fill="#0f0f1a" travellerWidth={4}/>{tsMets.map((m:any,j:number)=><Line key={m.key} type="stepAfter" dataKey={m.key} name={m.display_name} stroke={SEQ[j%SEQ.length]} strokeWidth={2.5} dot={false}/>)}</LineChart>)
              :trendType==='composed'?(<ComposedChart data={trendData} margin={{top:5,right:20,bottom:5,left:0}}><CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false}/><XAxis dataKey="period" {...AX}/><YAxis {...AX} tickFormatter={v=>nf(v,0)}/><RTooltip content={<Tip/>}/><Legend wrapperStyle={{fontSize:11}}/><Brush dataKey="period" height={14} stroke="rgba(255,255,255,.06)" fill="#0f0f1a" travellerWidth={4}/>{tsMets.slice(0,1).map((m:any)=><Bar key={m.key} dataKey={m.key} name={m.display_name} fill={`${C.blue}50`} radius={[3,3,0,0]} maxBarSize={28}/>)}{tsMets.slice(1).map((m:any,j:number)=><Line key={m.key} type="monotone" dataKey={m.key} name={m.display_name} stroke={SEQ[j+1]} strokeWidth={2.5} dot={false}/>)}</ComposedChart>)
              :trendType==='line'?(<LineChart data={trendData} margin={{top:5,right:10,bottom:5,left:0}}><CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false}/><XAxis dataKey="period" {...AX}/><YAxis {...AX} tickFormatter={v=>nf(v,0)}/><RTooltip content={<Tip/>}/><Legend wrapperStyle={{fontSize:11}}/><Brush dataKey="period" height={14} stroke="rgba(255,255,255,.06)" fill="#0f0f1a" travellerWidth={4}/>{tsMets.map((m:any,j:number)=><Line key={m.key} type="monotone" dataKey={m.key} name={m.display_name} stroke={SEQ[j%SEQ.length]} strokeWidth={2.5} dot={{r:2}} activeDot={{r:4}}/>)}{showFcast&&<Line type="monotone" dataKey="_forecast" name="Forecast" stroke={C.blue} strokeWidth={2} strokeDasharray="6 3" dot={{r:4}}/>}{showFcast&&<Line type="monotone" dataKey="_fit" name="Trend" stroke={C.amber} strokeWidth={1} dot={false} strokeDasharray="4 4"/>}</LineChart>)
              :(<AreaChart data={trendData} margin={{top:5,right:10,bottom:5,left:0}}><defs>{tsMets.map((_:any,j:number)=><linearGradient key={j} id={`tga${j}`} x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={SEQ[j%SEQ.length]} stopOpacity={.4}/><stop offset="100%" stopColor={SEQ[j%SEQ.length]} stopOpacity={.02}/></linearGradient>)}</defs><CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false}/><XAxis dataKey="period" {...AX}/><YAxis {...AX} tickFormatter={v=>nf(v,0)}/><RTooltip content={<Tip/>}/><Legend wrapperStyle={{fontSize:11}}/><Brush dataKey="period" height={14} stroke="rgba(255,255,255,.06)" fill="#0f0f1a" travellerWidth={4}/>{tsMets.map((m:any,j:number)=><Area key={m.key} type="monotone" dataKey={m.key} name={m.display_name} stroke={SEQ[j%SEQ.length]} strokeWidth={2.5} fill={`url(#tga${j})`} dot={false} activeDot={{r:4}}/>)}{showFcast&&<Area type="monotone" dataKey="_forecast" name="Forecast" stroke={C.blue} strokeWidth={2} strokeDasharray="6 3" fill="none" dot={{r:4}}/>}</AreaChart>)}
            </ResponsiveContainer>
          </div>
        </Card>
      )}
      {hasGrowth&&(
        <Card title="Growth Rate" sub={grItem?.display_name||''} icon={TrendingUp} col={C.green} relevance={rv}
          onPin={()=>pin('Growth Rate','growth',{growth_rates:gr,meta})} pinned={hasItem(jobId,'Growth Rate')}
          bar={<>{gr.length>1&&<Sel opts={gr.map((g:any)=>g.display_name)} val={grItem?.display_name||''} onChange={v=>setGrIdx(gr.findIndex((g:any)=>g.display_name===v))}/> }<TypePicker opts={T_GRW} val={grType} onChange={setGrType}/></>}>
          <div style={{height:260}}>
            <ResponsiveContainer width="100%" height="100%">
              {grType==='waterfall'?(<BarChart data={grWF} margin={{top:5,right:10,bottom:5,left:0}}><CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false}/><XAxis dataKey="period" {...AX}/><YAxis {...AX} tickFormatter={v=>`${(+v).toFixed(0)}%`}/><RTooltip content={<Tip/>}/><ReferenceLine y={0} stroke="rgba(255,255,255,.2)" strokeWidth={1.5}/><Bar dataKey="growth_rate_pct" name="Period Growth %" radius={[3,3,0,0]} maxBarSize={28}>{grWF.map((d:any,i:number)=><Cell key={i} fill={d._pos?C.green:C.coral} opacity={.85}/>)}<LabelList dataKey="growth_rate_pct" position="top" formatter={(v:any)=>`${(+v).toFixed(1)}%`} style={{fontSize:8,fill:'rgba(255,255,255,.35)'}}/></Bar></BarChart>)
              :grType==='area'?(<AreaChart data={grData} margin={{top:5,right:10,bottom:5,left:0}}><defs><linearGradient id="grFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={C.green} stopOpacity={.3}/><stop offset="100%" stopColor={C.green} stopOpacity={.02}/></linearGradient></defs><CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false}/><XAxis dataKey="period" {...AX}/><YAxis {...AX} tickFormatter={v=>nf(v,0)}/><RTooltip content={<Tip/>}/><Legend wrapperStyle={{fontSize:11}}/><Brush dataKey="period" height={14} stroke="rgba(255,255,255,.06)" fill="#0f0f1a" travellerWidth={4}/><Area type="monotone" dataKey="value" name="Value" stroke={C.green} fill="url(#grFill)" strokeWidth={2.5} dot={false}/><Area type="monotone" dataKey="cumulative_growth_pct" name="Cumulative %" stroke={C.coral} fill="none" strokeWidth={1.5} dot={false} strokeDasharray="4 2"/></AreaChart>)
              :(<ComposedChart data={grData} margin={{top:5,right:20,bottom:5,left:0}}><CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false}/><XAxis dataKey="period" {...AX}/><YAxis yAxisId="l" {...AX} tickFormatter={v=>nf(v,0)}/><YAxis yAxisId="r" orientation="right" {...AX} tickFormatter={v=>`${(+v).toFixed(0)}%`}/><RTooltip content={<Tip/>}/><Legend wrapperStyle={{fontSize:11}}/><Brush dataKey="period" height={14} stroke="rgba(255,255,255,.06)" fill="#0f0f1a" travellerWidth={4}/><Bar yAxisId="l" dataKey="value" name="Value" fill={`${C.blue}40`} radius={[3,3,0,0]} maxBarSize={28}/><Line yAxisId="r" type="monotone" dataKey="growth_rate_pct" name="Growth %" stroke={C.gold} strokeWidth={2.5} dot={{r:3}}/><Line yAxisId="r" type="monotone" dataKey="cumulative_growth_pct" name="Cumulative %" stroke={C.coral} strokeWidth={1.5} dot={false} strokeDasharray="4 2"/><ReferenceLine yAxisId="r" y={0} stroke="rgba(255,255,255,.15)"/></ComposedChart>)}
            </ResponsiveContainer>
          </div>
        </Card>
      )}
    </>)
  }

  // ── Distribution ──────────────────────────────────────────────────────────
  function renderDistribution(){
    if(!dists.length) return <Empty msg="No distributions"/>
    const rv=rel('distribution',a), dist=dists[distIdx]
    if(!dist) return <Empty msg="Select column"/>
    const hist=dist.histogram||[], s=dist.stats||{}
    const areaData=hist.map((h:any)=>({x:h.label,y:h.count}))
    const insight=s.skewness!=null?(()=>{const sk=s.skewness,shape=Math.abs(sk)<.5?'Symmetric':sk>0?'Right-skewed':'Left-skewed',cv=s.std&&s.mean?((s.std/Math.abs(s.mean))*100).toFixed(0):'–';return `${shape} · CV=${cv}% · Outliers=${s.outlier_pct}%`})():''
    return(
      <Card title="Value Distribution" sub={dist.display_name} icon={Activity} col={C.purple} relevance={rv}
        onPin={()=>pin(`Distribution: ${dist.display_name}`,'distribution',{distributions:dists,meta})} pinned={hasItem(jobId,`Distribution: ${dist.display_name}`)}
        bar={<>{dists.length>1&&<Sel opts={dists.map((d:any)=>d.display_name)} val={dist.display_name} onChange={v=>setDistIdx(dists.findIndex((d:any)=>d.display_name===v))}/> }<TypePicker opts={T_DST} val={distType} onChange={setDistType}/></>}>
        {distType==='area'?(<><div style={{height:240}}><ResponsiveContainer width="100%" height="100%"><AreaChart data={areaData} margin={{top:5,right:5,bottom:5,left:0}}><defs><linearGradient id="dA" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={C.purple} stopOpacity={.5}/><stop offset="100%" stopColor={C.purple} stopOpacity={.02}/></linearGradient></defs><CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false}/><XAxis dataKey="x" {...AX} interval="preserveStartEnd"/><YAxis {...AX}/><RTooltip content={<Tip/>}/><Area type="monotone" dataKey="y" name="Count" stroke={C.purple} fill="url(#dA)" strokeWidth={2}/>{s.mean!=null&&<ReferenceLine x={s.mean?.toFixed(1)} stroke={C.coral} strokeDasharray="4 2"/>}</AreaChart></ResponsiveContainer></div><Insight text={insight}/></>)
        :distType==='violin'?(<><div style={{height:240}}><ResponsiveContainer width="100%" height="100%"><BarChart data={hist} layout="vertical" margin={{left:5,right:5,top:5,bottom:5}}><CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" horizontal={false}/><XAxis type="number" {...AX}/><YAxis type="category" dataKey="label" {...AX} width={50} interval="preserveStartEnd"/><RTooltip content={<Tip/>}/><Bar dataKey="count" name="Count" radius={[0,3,3,0]}>{hist.map((_:any,i:number)=><Cell key={i} fill={`hsl(${270+i*(60/hist.length)},70%,${35+i*(25/hist.length)}%)`}/>)}</Bar></BarChart></ResponsiveContainer></div><Insight text={insight}/></>)
        :distType==='boxplot'?(<div>{dists.slice(0,8).filter((d:any)=>d.stats).map((d:any,i:number)=>{const ss=d.stats,range=(ss.max??0)-(ss.min??0);if(!range) return null;const toX=(v:number)=>`${((v-ss.min)/range)*100}%`,col=SEQ[i%SEQ.length];return(<div key={i} style={{marginBottom:16}}><div style={{display:'flex',justifyContent:'space-between',marginBottom:4}}><span style={{fontSize:11,color:'rgba(255,255,255,.45)'}}>{d.display_name}</span><span style={{fontSize:10,color:'rgba(255,255,255,.25)',fontFamily:'monospace'}}>μ={nf(ss.mean)} · σ={nf(ss.std)}</span></div><div style={{position:'relative',height:20,display:'flex',alignItems:'center'}}><div style={{position:'absolute',inset:'50% 0',height:1,background:'rgba(255,255,255,.06)'}}/><div style={{position:'absolute',height:8,borderLeft:'1px solid rgba(255,255,255,.15)',borderRight:'1px solid rgba(255,255,255,.15)',left:toX(ss.min),right:`${100-((ss.max-ss.min)/range)*100}%`}}/><div style={{position:'absolute',height:14,borderRadius:2,background:`${col}28`,border:`1px solid ${col}55`,left:toX(ss.q1??ss.mean-ss.std),right:`${100-(((ss.q3??ss.mean+ss.std)-ss.min)/range)*100}%`}}/><div style={{position:'absolute',width:2,height:18,borderRadius:1,background:col,left:toX(ss.median??ss.mean)}}/><div style={{position:'absolute',width:8,height:8,borderRadius:'50%',background:C.coral,left:`calc(${toX(ss.mean)} - 4px)`}}/></div><div style={{display:'flex',justifyContent:'space-between',marginTop:2,fontSize:9,color:'rgba(255,255,255,.2)',fontFamily:'monospace'}}><span>{nf(ss.min)}</span><span>Q1:{nf(ss.q1)}</span><span>Median:{nf(ss.median)}</span><span>Q3:{nf(ss.q3)}</span><span>{nf(ss.max)}</span></div></div>)})}<div style={{display:'flex',gap:16,marginTop:8,fontSize:10,color:'rgba(255,255,255,.25)'}}><span>— Min/Max</span><span>□ IQR</span><span>| Median</span><span style={{color:C.coral}}>● Mean</span></div></div>)
        :(<><div style={{height:240}}><ResponsiveContainer width="100%" height="100%"><BarChart data={hist} margin={{top:5,right:5,bottom:5,left:0}}><CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false}/><XAxis dataKey="label" {...AX} interval="preserveStartEnd"/><YAxis {...AX}/><RTooltip content={<Tip/>}/><Bar dataKey="count" name="Count" radius={[3,3,0,0]}>{hist.map((_:any,i:number)=><Cell key={i} fill={`${C.purple}${Math.round(50+(i/hist.length)*180).toString(16).padStart(2,'0')}`}/>)}</Bar>{s.mean!=null&&<ReferenceLine x={s.mean?.toFixed(1)} stroke={C.coral} strokeDasharray="4 2" label={{value:'Mean',position:'top',fill:C.coral,fontSize:9}}/>}{s.median!=null&&<ReferenceLine x={s.median?.toFixed(1)} stroke={C.teal} strokeDasharray="4 2" label={{value:'Median',position:'top',fill:C.teal,fontSize:9}}/>}</BarChart></ResponsiveContainer></div>{s.mean!=null&&<div style={{display:'grid',gridTemplateColumns:'repeat(5,1fr)',gap:8,marginTop:12}}>{[['Mean',nf(s.mean)],['Median',nf(s.median)],['Std',nf(s.std)],['Skew',s.skewness?.toFixed(2)],['Outliers',`${s.outlier_pct}%`]].map(([l,v])=>(<div key={l} style={{padding:'8px 4px',textAlign:'center',borderRadius:8,background:'rgba(212,175,55,.04)',border:'1px solid rgba(212,175,55,.08)'}}><p style={{fontSize:9,color:'rgba(255,255,255,.25)'}}>{l}</p><p style={{fontSize:13,fontWeight:700,color:C.gold,marginTop:2}}>{v}</p></div>))}</div>}<Insight text={insight}/></>)}
      </Card>
    )
  }

  // ── Composition ───────────────────────────────────────────────────────────
  function renderComposition(){
    if(!comp.length) return <Empty msg="No composition data"/>
    const rv=rel('composition',a), item=comp[compIdx]; if(!item) return <Empty msg="No data"/>
    const data=item.data||[], insight=(()=>{if(!data.length) return '';const top2=[...data].sort((a:any,b:any)=>(b.pct??0)-(a.pct??0)).slice(0,2);return `Top 2 = ${top2.reduce((s:number,x:any)=>s+(x.pct??0),0).toFixed(0)}%`})()
    const tmData=data.map((d:any,i:number)=>({name:d.name,size:d.value||1,value:d.value,fill:SEQ[i%SEQ.length]}))
    return(
      <Card title="Composition" sub={item.display_name} icon={PieIconLucide} col={C.amber} relevance={rv}
        onPin={()=>pin(`Composition: ${item.display_name}`,'composition',{composition:comp,meta})} pinned={hasItem(jobId,`Composition: ${item.display_name}`)}
        bar={<>{comp.length>1&&<Sel opts={comp.map((c:any)=>c.display_name)} val={item.display_name} onChange={v=>setCompIdx(comp.findIndex((c:any)=>c.display_name===v))}/> }<TypePicker opts={T_CMP} val={compType} onChange={setCompType}/></>}>
        {compType==='treemap'?(<div style={{height:260}}><ResponsiveContainer width="100%" height="100%"><Treemap data={tmData} dataKey="size" aspectRatio={4/3} content={<TreemapNode/>}><RTooltip content={({active,payload}:any)=>{if(!active||!payload?.[0]) return null;const d=payload[0].payload;return<div style={{background:'#10101c',border:'1px solid rgba(212,175,55,.2)',borderRadius:8,padding:'8px 12px',fontSize:11}}><b style={{color:'#fff'}}>{d.name}</b><br/><span style={{color:C.gold}}>{nf(d.value)}</span></div>}}/></Treemap></ResponsiveContainer></div>)
        :compType==='bar'?(<div style={{height:260}}><ResponsiveContainer width="100%" height="100%"><BarChart data={data} margin={{top:5,right:5,bottom:50,left:0}}><CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false}/><XAxis dataKey="name" {...AX} tick={({x,y,payload}:any)=><text x={x} y={y+6} textAnchor="end" fontSize={9} fill="rgba(255,255,255,.3)" transform={`rotate(-30,${x},${y})`}>{String(payload.value).slice(0,14)}</text>} height={50}/><YAxis {...AX} tickFormatter={v=>`${(+v).toFixed(0)}%`}/><RTooltip content={<Tip/>}/><Bar dataKey="pct" name="Share %" radius={[4,4,0,0]}>{data.map((_:any,i:number)=><Cell key={i} fill={SEQ[i%SEQ.length]} opacity={.85}/>)}<LabelList dataKey="pct" position="top" formatter={(v:number)=>`${v?.toFixed(0)}%`} style={{fontSize:9,fill:'rgba(255,255,255,.3)'}}/></Bar></BarChart></ResponsiveContainer></div>)
        :(<div style={{display:'flex',gap:16,alignItems:'center'}}><div style={{height:220,flex:'0 0 200px'}}><ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={data} dataKey="value" nameKey="name" outerRadius={88} innerRadius={compType==='donut'?44:0} paddingAngle={2} startAngle={90} endAngle={-270}>{data.map((_:any,i:number)=><Cell key={i} fill={SEQ[i%SEQ.length]}/>)}</Pie><RTooltip content={<Tip/>}/></PieChart></ResponsiveContainer></div><div style={{flex:1,display:'flex',flexDirection:'column',gap:5}}>{data.slice(0,7).map((d:any,i:number)=>(<div key={i} style={{display:'flex',alignItems:'center',justifyContent:'space-between',fontSize:12}}><span style={{display:'flex',alignItems:'center',gap:6,color:'rgba(255,255,255,.5)',minWidth:0}}><span style={{width:8,height:8,borderRadius:'50%',background:SEQ[i%SEQ.length],flexShrink:0}}/><span style={{overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{d.name}</span></span><span style={{fontWeight:700,color:'#fff',flexShrink:0}}>{pf(d.pct)}</span></div>))}</div></div>)}
        <Insight text={insight}/>
      </Card>
    )
  }

  // ── Scatter ───────────────────────────────────────────────────────────────
  function renderScatter(){
    if(!sct.length) return <Empty msg="Need 2+ correlated numeric columns"/>
    const rv=rel('scatter',a), nPts=scData.length
    const quadCounts=scData.reduce((acc:any,d:any)=>{if(d.quadrant) acc[d.quadrant]=(acc[d.quadrant]||0)+1;return acc},{})
    const insight=scItem?(()=>{const r=scItem.correlation??0,str=Math.abs(r)>.7?'Strong':Math.abs(r)>.4?'Moderate':'Weak',dir=r>0?'positive':'negative';return `${str} ${dir} (r=${r.toFixed(2)}) · ${nPts} aggregated points`})():''
    return(
      <Card title="Relationship Analysis" sub={scItem?`${scItem.display_x} vs ${scItem.display_y}`:''} icon={GitBranch} col={C.gold} relevance={rv}
        onPin={()=>pin(`Scatter: ${scItem?.display_x}×${scItem?.display_y}`,'scatter',{scatter:sct,meta})} pinned={hasItem(jobId,`Scatter: ${scItem?.display_x}×${scItem?.display_y}`)}
        bar={<>{sct.length>1&&<Sel opts={scLabels} val={scLabels[scIdx]||''} onChange={v=>setScIdx(scLabels.indexOf(v))}/> }<button onClick={()=>setShowQuad(!showQuad)} style={{padding:'5px 10px',borderRadius:8,fontSize:11,cursor:'pointer',background:showQuad?'rgba(212,175,55,.12)':'rgba(255,255,255,.05)',border:`1px solid ${showQuad?'rgba(212,175,55,.3)':'rgba(255,255,255,.08)'}`,color:showQuad?C.gold:'rgba(255,255,255,.4)'}}>{showQuad?'✓ Quadrants':'Quadrants'}</button></>}>
        <div style={{height:340}}>
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart margin={{top:10,right:20,bottom:40,left:10}}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.06)"/>
              {showQuad&&scItem?.x_median!=null&&<ReferenceLine x={scItem.x_median} stroke="rgba(255,255,255,.15)" strokeDasharray="5 3"/>}
              {showQuad&&scItem?.y_median!=null&&<ReferenceLine y={scItem.y_median} stroke="rgba(255,255,255,.15)" strokeDasharray="5 3"/>}
              <XAxis type="number" dataKey="x" name={scItem?.display_x} {...AX} tickFormatter={v=>nf(v,0)} label={{value:scItem?.display_x||'X',position:'insideBottom',offset:-10,fill:'rgba(255,255,255,.25)',fontSize:10}}/>
              <YAxis type="number" dataKey="y" name={scItem?.display_y} {...AX} tickFormatter={v=>nf(v,0)} label={{value:scItem?.display_y||'Y',angle:-90,position:'insideLeft',fill:'rgba(255,255,255,.25)',fontSize:10}}/>
              <ZAxis range={[60,200]}/>
              <RTooltip content={({active,payload}:any)=>{if(!active||!payload?.[0]) return null;const d=payload[0].payload;return<div style={{background:'#10101c',border:'1px solid rgba(212,175,55,.2)',borderRadius:12,padding:'10px 14px',minWidth:180}}>{d.category&&<p style={{color:C.gold,fontWeight:700,fontSize:12,marginBottom:6}}>{d.category}</p>}<p style={{fontSize:11,color:'rgba(255,255,255,.5)'}}>{scItem?.display_x}: <b style={{color:'#fff'}}>{nf(d.x)}</b></p><p style={{fontSize:11,color:'rgba(255,255,255,.5)'}}>{scItem?.display_y}: <b style={{color:'#fff'}}>{nf(d.y)}</b></p>{d.quadrant&&<p style={{fontSize:10,marginTop:6,color:QUAD_C[d.quadrant]||C.gold,fontWeight:600}}>◆ {d.quadrant}</p>}</div>}}/>
              {scCats.length>1?(<>{scCats.map((cat:string,ci:number)=><Scatter key={cat} name={cat} data={scData.filter((d:any)=>d.category===cat)} fill={SEQ[ci%SEQ.length]} opacity={.85}/>)}<Legend wrapperStyle={{fontSize:11}}/></>)
              :<Scatter data={scData} fill={C.gold} opacity={.8} shape={(props:any)=>{const{cx,cy,payload}=props;if(cx==null||cy==null)return<g/>;const fill=showQuad?(QUAD_C[payload?.quadrant||'']||C.gold):C.gold;return<circle cx={cx} cy={cy} r={9} fill={fill} fillOpacity={.75} stroke="rgba(0,0,0,.2)"/>}}/>}
            </ScatterChart>
          </ResponsiveContainer>
        </div>
        {showQuad&&<div style={{display:'flex',gap:10,marginTop:12,flexWrap:'wrap'}}>{Object.entries(QUAD_C).map(([q,c])=><div key={q} style={{display:'flex',alignItems:'center',gap:5,fontSize:11}}><span style={{width:12,height:12,borderRadius:3,background:c,opacity:.8}}/><span style={{color:'rgba(255,255,255,.4)'}}>{q}</span>{quadCounts[q]&&<span style={{color:c,fontWeight:700}}>({quadCounts[q]})</span>}</div>)}</div>}
        <Insight text={insight}/>
      </Card>
    )
  }

  // ── Correlation ───────────────────────────────────────────────────────────
  function renderCorrelation(){
    if(!corrPairs.length) return <Empty msg="Need 2+ numeric columns"/>
    const rv=rel('correlation',a)
    return(
      <Card title="Metric Correlations" sub={`${corrPairs.length} pairs`} icon={Layers} col={C.teal} relevance={rv}
        onPin={()=>pin('Metric Correlations','correlation',{correlation_matrix:cm,meta})} pinned={hasItem(jobId,'Metric Correlations')}
        bar={<TypePicker opts={T_COR} val={corrType} onChange={setCorrType}/>}>
        {corrType==='table'?(<div style={{overflowX:'auto'}}><table style={{width:'100%',borderCollapse:'collapse',fontSize:11}}><thead><tr>{['Pair','r','Strength','Direction'].map(h=><th key={h} style={{padding:'8px 10px',textAlign:'left',color:'rgba(255,255,255,.4)',borderBottom:'1px solid rgba(255,255,255,.06)',fontWeight:600}}>{h}</th>)}</tr></thead><tbody>{corrPairs.map((c:any,i:number)=><tr key={i} style={{background:i%2===0?'rgba(255,255,255,.01)':'transparent'}}><td style={{padding:'8px 10px',color:'rgba(255,255,255,.55)'}}>{c.label}</td><td style={{padding:'8px 10px',fontWeight:700,color:c.value>=0?C.teal:C.coral}}>{c.value?.toFixed(3)}</td><td style={{padding:'8px 10px',color:'rgba(255,255,255,.4)'}}>{c.strength}</td><td style={{padding:'8px 10px',color:c.value>=0?C.green:C.coral}}>{c.value>=0?'↑ Positive':'↓ Negative'}</td></tr>)}</tbody></table></div>)
        :corrType==='intensity'?(<div style={{height:Math.max(200,corrPairs.length*28+40)}}><ResponsiveContainer width="100%" height="100%"><BarChart data={corrPairs} layout="vertical" margin={{left:155,right:55,top:5,bottom:5}}><CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" horizontal={false}/><XAxis type="number" domain={[-1,1]} {...AX}/><YAxis type="category" dataKey="label" {...AX} width={150}/><RTooltip content={<Tip/>}/><ReferenceLine x={0} stroke="rgba(255,255,255,.15)"/><ReferenceLine x={.7} stroke={`${C.green}40`} strokeDasharray="3 2"/><ReferenceLine x={-.7} stroke={`${C.coral}40`} strokeDasharray="3 2"/><Bar dataKey="value" name="r" radius={[0,3,3,0]} maxBarSize={18}>{corrPairs.map((d:any,i:number)=><Cell key={i} fill={d.value>=0?`rgba(0,206,209,${.3+d.abs_value*.7})`:`rgba(255,107,107,${.3+d.abs_value*.7})`}/>)}<LabelList dataKey="value" position="right" formatter={(v:number)=>v?.toFixed(2)} style={{fontSize:9,fill:'rgba(255,255,255,.3)'}}/></Bar></BarChart></ResponsiveContainer></div>)
        :(<div style={{height:Math.max(200,corrPairs.length*28+40)}}><ResponsiveContainer width="100%" height="100%"><BarChart data={corrPairs} layout="vertical" margin={{left:155,right:55,top:5,bottom:5}}><CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" horizontal={false}/><XAxis type="number" domain={[-1,1]} {...AX}/><YAxis type="category" dataKey="label" {...AX} width={150}/><RTooltip content={<Tip/>}/><ReferenceLine x={0} stroke="rgba(255,255,255,.15)"/><ReferenceLine x={.7} stroke={`${C.green}40`} strokeDasharray="3 2" label={{value:'Strong',position:'top',fill:C.green,fontSize:8}}/><ReferenceLine x={-.7} stroke={`${C.coral}40`} strokeDasharray="3 2"/><Bar dataKey="value" name="r" radius={[0,3,3,0]} maxBarSize={18}>{corrPairs.map((d:any,i:number)=><Cell key={i} fill={d.value>=0?C.teal:C.coral} opacity={.4+d.abs_value*.6}/>)}<LabelList dataKey="value" position="right" formatter={(v:number)=>v?.toFixed(2)} style={{fontSize:9,fill:'rgba(255,255,255,.3)'}}/></Bar></BarChart></ResponsiveContainer></div>)}
        <Insight text={corrPairs[0]?`Strongest: ${corrPairs[0].label} (r=${corrPairs[0].value?.toFixed(2)}) — ${corrPairs[0].value>0?'move together':'inverse'}`:''} />
      </Card>
    )
  }

  // ── Heatmap ───────────────────────────────────────────────────────────────
  function renderHeatmap(){
    if(hmCols.length<3) return <Empty msg="Need 3+ numeric columns"/>
    const rv=rel('heatmap',a), pivotCol=hmCols[hmMetric%hmCols.length]
    return(
      <Card title="Correlation Heatmap" sub={`Pivot: ${pivotCol?.slice(0,20)}`} icon={Grid} col={C.indigo} relevance={rv}
        bar={<Sel opts={hmCols} val={pivotCol} onChange={v=>setHmMetric(hmCols.indexOf(v))}/>}>
        <div style={{height:280}}><ResponsiveContainer width="100%" height="100%"><BarChart data={hmData} margin={{top:5,right:10,bottom:55,left:0}}><CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false}/><XAxis dataKey="name" {...AX} tick={({x,y,payload}:any)=><text x={x} y={y+6} textAnchor="end" fontSize={9} fill="rgba(255,255,255,.35)" transform={`rotate(-35,${x},${y})`}>{payload.value}</text>} height={55}/><YAxis domain={[-1,1]} {...AX} tickFormatter={v=>v.toFixed(1)}/><RTooltip content={<Tip/>}/><ReferenceLine y={0} stroke="rgba(255,255,255,.15)"/><ReferenceLine y={.7} stroke={`${C.green}40`} strokeDasharray="3 2"/><ReferenceLine y={-.7} stroke={`${C.coral}40`} strokeDasharray="3 2"/><Bar dataKey="value" name={`r vs ${pivotCol?.slice(0,12)}`} radius={[3,3,0,0]} maxBarSize={40}>{hmData.map((d:any,i:number)=><Cell key={i} fill={d.value>=0?`rgba(0,206,209,${.2+Math.abs(d.value)*.8})`:`rgba(255,107,107,${.2+Math.abs(d.value)*.8})`}/>)}<LabelList dataKey="value" position="top" formatter={(v:number)=>v?.toFixed(2)} style={{fontSize:8,fill:'rgba(255,255,255,.3)'}}/></Bar></BarChart></ResponsiveContainer></div>
        <Insight text={`Teal = positive correlation, Red = negative. Taller = stronger. Pivot: "${pivotCol?.slice(0,20)}"`}/>
      </Card>
    )
  }

  // ── vs Average ────────────────────────────────────────────────────────────
  function renderVsAvg(){
    if(!vsAvgD.length) return <Empty msg="No vs-average data"/>
    const rv=rel('vsavg',a), above=vsAvgD.filter((d:any)=>d.direction==='above').length
    return(
      <Card title="Performance vs Average" sub={`${above} above · ${vsAvgD.length-above} below`} icon={Zap} col={C.green} relevance={rv}
        onPin={()=>pin('Performance vs Average','vsavg',{percentage_changes:pctC,meta})} pinned={hasItem(jobId,'Performance vs Average')}
        bar={<TypePicker opts={T_VSA} val={vsAvgType} onChange={setVsAvgType}/>}>
        {vsAvgType==='bullet'?(
          <div>{vsAvgD.slice(0,10).map((d:any,i:number)=>{const pct=d.pct_vs_average??0,isPos=pct>=0,bw=Math.min(100,Math.abs(pct));return(<div key={i} style={{marginBottom:14}}><div style={{display:'flex',justifyContent:'space-between',marginBottom:4,fontSize:11}}><span style={{color:'rgba(255,255,255,.5)'}}>{d.category?.slice(0,20)}</span><span style={{fontWeight:700,color:isPos?C.green:C.coral}}>{isPos?'+':''}{pct?.toFixed(1)}%</span></div><div style={{height:10,borderRadius:5,background:'rgba(255,255,255,.05)',position:'relative',overflow:'hidden'}}><div style={{position:'absolute',[isPos?'left':'right']:'50%',width:`${bw/2}%`,height:'100%',background:isPos?C.green:C.coral,opacity:.8,borderRadius:5}}/><div style={{position:'absolute',left:'50%',top:0,width:1,height:'100%',background:'rgba(255,255,255,.2)'}}/></div></div>)})}</div>
        ):vsAvgType==='dot'?(
          <div style={{height:280}}><ResponsiveContainer width="100%" height="100%"><ScatterChart margin={{top:5,right:20,bottom:55,left:0}}><CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.06)"/><XAxis dataKey="category" type="category" {...AX} tick={({x,y,payload}:any)=><text x={x} y={y+6} textAnchor="end" fontSize={8} fill="rgba(255,255,255,.3)" transform={`rotate(-35,${x},${y})`}>{String(payload.value).slice(0,14)}</text>} height={55}/><YAxis dataKey="pct_vs_average" {...AX} tickFormatter={v=>`${(+v).toFixed(0)}%`}/><RTooltip content={<Tip/>}/><ReferenceLine y={0} stroke="rgba(255,255,255,.2)" strokeWidth={2}/><Scatter data={vsAvgD} shape={(props:any)=>{const{cx,cy,payload}=props;return<circle cx={cx} cy={cy} r={7} fill={payload.direction==='above'?C.green:C.coral} fillOpacity={.8} stroke="rgba(0,0,0,.2)"/>}}/></ScatterChart></ResponsiveContainer></div>
        ):(
          <div style={{height:280}}><ResponsiveContainer width="100%" height="100%"><BarChart data={vsAvgD} margin={{top:5,right:5,bottom:55,left:0}}><CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false}/><XAxis dataKey="category" {...AX} tick={({x,y,payload}:any)=><text x={x} y={y+6} textAnchor="end" fontSize={8} fill="rgba(255,255,255,.3)" transform={`rotate(-35,${x},${y})`}>{String(payload.value).slice(0,14)}</text>} height={55}/><YAxis {...AX} tickFormatter={v=>`${(+v).toFixed(0)}%`}/><RTooltip content={<Tip/>}/><ReferenceLine y={0} stroke="rgba(255,255,255,.2)" strokeWidth={1.5}/><Bar dataKey="pct_vs_average" name="vs Avg %" radius={[3,3,0,0]} maxBarSize={30}>{vsAvgD.map((d:any,i:number)=><Cell key={i} fill={d.direction==='above'?C.green:C.coral} opacity={.8}/>)}<LabelList dataKey="pct_vs_average" position="top" formatter={(v:any)=>`${(+v).toFixed(0)}%`} style={{fontSize:8,fill:'rgba(255,255,255,.3)'}}/></Bar></BarChart></ResponsiveContainer></div>
        )}
        <Insight text={`${above}/${vsAvgD.length} segments above average.`}/>
      </Card>
    )
  }

  // ── Top/Bottom ────────────────────────────────────────────────────────────
  function renderTopBottom(){
    if(!tbData.length) return <Empty msg="Need 5+ categories"/>
    const rv=rel('topbottom',a)
    return(
      <Card title="Top vs Bottom Performers" sub={tb?.display_metric||''} icon={Award} col={C.coral} relevance={rv}
        onPin={()=>pin('Top vs Bottom Performers','topbottom',{percentage_changes:pctC,meta})} pinned={hasItem(jobId,'Top vs Bottom Performers')}>
        <div style={{height:Math.max(260,tbData.length*28)}}><ResponsiveContainer width="100%" height="100%"><BarChart data={tbData} layout="vertical" margin={{left:95,right:70,top:5,bottom:5}}><CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" horizontal={false}/><XAxis type="number" {...AX} tickFormatter={v=>nf(v,0)}/><YAxis type="category" dataKey="category" {...AX} width={90}/><RTooltip content={<Tip/>}/><Bar dataKey="value" name="Value" radius={[0,4,4,0]} maxBarSize={22}>{tbData.map((d:any,i:number)=><Cell key={i} fill={d._g==='Top'?C.green:C.coral} opacity={.8}/>)}<LabelList dataKey="formatted" position="right" style={{fontSize:9,fill:'rgba(255,255,255,.3)'}}/></Bar></BarChart></ResponsiveContainer></div>
        {tb?.pct_gap!=null&&<Insight icon={Award} color={C.amber} text={`Top performers ${Math.abs(tb.pct_gap).toFixed(0)}% ${tb.pct_gap>0?'higher':'lower'} than bottom.`}/>}
      </Card>
    )
  }

  // ── Radar ─────────────────────────────────────────────────────────────────
  function renderRadar(){
    if(radarData.length<3) return <Empty msg="Need 3+ segments"/>
    return(
      <Card title="Segment Radar" sub="Multi-metric overview" icon={Eye} col={C.pink} relevance={rel('radar',a)}>
        <div style={{height:320}}><ResponsiveContainer width="100%" height="100%"><RadarChart data={radarData}><PolarGrid stroke="rgba(255,255,255,.08)"/><PolarAngleAxis dataKey="subject" tick={{fill:'rgba(255,255,255,.4)',fontSize:10}}/><PolarRadiusAxis tick={{fill:'rgba(255,255,255,.2)',fontSize:7}}/><Radar name="Total" dataKey="total" stroke={C.gold} fill={C.gold} fillOpacity={.15} strokeWidth={2}/><Radar name="Mean" dataKey="mean" stroke={C.teal} fill={C.teal} fillOpacity={.08} strokeWidth={1.5}/><Legend wrapperStyle={{fontSize:11}}/><RTooltip content={<Tip/>}/></RadarChart></ResponsiveContainer></div>
      </Card>
    )
  }

  // ── Ranking ───────────────────────────────────────────────────────────────
  function renderRanking(){
    if(!rnk.length) return <Empty msg="No ranking data"/>
    const rv=rel('ranking',a)
    if(!rnkItem) return <Empty msg="No item"/>
    const lollipopData=[...rnkData].reverse()
    return(
      <Card title="Category Ranking" sub={`${rnkItem.display_dimension} by ${rnkItem.display_metric} · ${rnkItem.total_categories} categories`} icon={Trophy} col={C.gold} relevance={rv}
        bar={<>{rnk.length>1&&<Sel opts={rnk.map((_:any,i:number)=>`${rnk[i].display_dimension} × ${rnk[i].display_metric}`)} val={`${rnkItem.display_dimension} × ${rnkItem.display_metric}`} onChange={v=>setRnkIdx(rnk.findIndex((_:any,i:number)=>`${rnk[i].display_dimension} × ${rnk[i].display_metric}`===v))}/> }<TypePicker opts={T_RNK} val={rnkType} onChange={setRnkType}/></>}>
        {rnkType==='lollipop'?(
          <div style={{height:Math.max(280,lollipopData.length*30)}}>
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={lollipopData} layout="vertical" margin={{left:110,right:80,top:5,bottom:5}}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" horizontal={false}/>
                <XAxis type="number" {...AX} tickFormatter={v=>nf(v,0)} domain={[0,'auto']}/>
                <YAxis type="category" dataKey="category" {...AX} width={105}/>
                <RTooltip content={<Tip/>}/>
                <Bar dataKey="value" name={rnkItem.display_metric} barSize={2}>{lollipopData.map((d:any,i:number)=><Cell key={i} fill={TIER_C[d.tier]||C.gold} opacity={.6}/>)}</Bar>
                <Scatter dataKey="value" name="Value" shape={(props:any)=>{const{cx,cy,payload}=props;return<circle cx={cx} cy={cy} r={6} fill={TIER_C[payload?.tier]||C.gold} stroke="rgba(0,0,0,.3)" strokeWidth={1}/>}}/>
                <LabelList dataKey="formatted_value" position="right" style={{fontSize:9,fill:'rgba(255,255,255,.35)'}}/>
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        ):rnkType==='podium'?(
          <><div style={{height:Math.max(260,rnkData.length*32)}}><ResponsiveContainer width="100%" height="100%"><BarChart data={rnkData} margin={{top:5,right:10,bottom:55,left:0}}><CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false}/><XAxis dataKey="category" {...AX} tick={({x,y,payload}:any)=><text x={x} y={y+6} textAnchor="end" fontSize={9} fill="rgba(255,255,255,.3)" transform={`rotate(-30,${x},${y})`}>{String(payload.value).slice(0,14)}</text>} height={55}/><YAxis {...AX} tickFormatter={v=>nf(v,0)}/><RTooltip content={<Tip/>}/><Bar dataKey="value" name={rnkItem.display_metric} radius={[4,4,0,0]}>{rnkData.map((d:any,i:number)=><Cell key={i} fill={TIER_C[d.tier]||C.gold} opacity={.8+.2*(i===0?1:0)}/>)}</Bar></BarChart></ResponsiveContainer></div>
          <div style={{display:'flex',gap:10,marginTop:10,flexWrap:'wrap'}}>{Object.entries(TIER_C).map(([t,c])=><div key={t} style={{display:'flex',alignItems:'center',gap:5,fontSize:11}}><span style={{width:12,height:12,borderRadius:3,background:c}}/><span style={{color:'rgba(255,255,255,.4)'}}>{t}</span></div>)}</div></>
        ):(
          <div style={{height:Math.max(240,rnkData.length*32)}}><ResponsiveContainer width="100%" height="100%"><BarChart data={rnkData} layout="vertical" margin={{left:110,right:80,top:5,bottom:5}}><CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" horizontal={false}/><XAxis type="number" {...AX} tickFormatter={v=>nf(v,0)}/><YAxis type="category" dataKey="category" {...AX} width={105}/><RTooltip content={<Tip/>}/><Bar dataKey="value" name={rnkItem.display_metric} radius={[0,4,4,0]} maxBarSize={24}>{rnkData.map((d:any,i:number)=><Cell key={i} fill={TIER_C[d.tier]||C.gold} opacity={.85}/>)}<LabelList dataKey="formatted_value" position="right" style={{fontSize:9,fill:'rgba(255,255,255,.3)'}}/></Bar></BarChart></ResponsiveContainer></div>
        )}
        {rnkItem.winner&&<Insight icon={Trophy} color={C.gold} text={`Winner: "${rnkItem.winner}" (${rnkItem.winner_value}) · Spread: ${rnkItem.spread_pct?.toFixed(0)}% gap top vs bottom`}/>}
      </Card>
    )
  }

  // ── Outliers ──────────────────────────────────────────────────────────────
  function renderOutliers(){
    if(!out.length) return <Empty msg="No outliers detected"/>
    const rv=rel('outliers',a)
    if(!outItem) return <Empty msg="No data"/>
    const stripData=outItem.samples||[]
    return(
      <Card title="Outlier Analysis" sub={`${outItem.display_name} · ${outItem.total_outliers} outliers (${outItem.outlier_pct}%)`} icon={ShieldAlert} col={C.coral} relevance={rv}
        bar={<>{out.length>1&&<Sel opts={out.map((o:any)=>o.display_name)} val={outItem.display_name} onChange={v=>setOutIdx(out.findIndex((o:any)=>o.display_name===v))}/> }<TypePicker opts={T_OUT} val={outType} onChange={setOutType}/></>}>
        {outType==='category'&&outItem.by_category?.length>0?(
          <div style={{height:240}}><ResponsiveContainer width="100%" height="100%"><BarChart data={outItem.by_category.slice(0,12)} layout="vertical" margin={{left:90,right:60,top:5,bottom:5}}><CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" horizontal={false}/><XAxis type="number" {...AX}/><YAxis type="category" dataKey="category" {...AX} width={85}/><RTooltip content={<Tip/>}/><Bar dataKey="outlier_count" name="Outlier Count" radius={[0,4,4,0]} fill={C.coral} opacity={.8}><LabelList dataKey="outlier_pct" position="right" formatter={(v:any)=>`${v}%`} style={{fontSize:9,fill:'rgba(255,255,255,.3)'}}/></Bar></BarChart></ResponsiveContainer></div>
        ):outType==='strip'?(
          <div style={{height:260}}>
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{top:10,right:20,bottom:20,left:10}}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.06)" vertical={false}/>
                <XAxis type="number" dataKey="value" name="Value" {...AX} tickFormatter={v=>nf(v,0)}/>
                <YAxis type="number" dataKey="zscore" name="Z-Score" {...AX}/>
                <RTooltip content={({active,payload}:any)=>{if(!active||!payload?.[0]) return null;const d=payload[0].payload;return<div style={{background:'#10101c',border:'1px solid rgba(212,175,55,.2)',borderRadius:8,padding:'8px 12px',fontSize:11}}><p style={{color:'#fff',fontWeight:700}}>{d.formatted}</p><p style={{color:'rgba(255,255,255,.5)'}}>Z-Score: {d.zscore?.toFixed(2)}</p><p style={{color:d.severity==='extreme'?C.coral:C.amber,fontWeight:600}}>{d.severity} {d.direction}</p></div>}}/>
                <ReferenceLine y={3} stroke={`${C.coral}60`} strokeDasharray="4 2" label={{value:'z=3 extreme',position:'right',fill:C.coral,fontSize:9}}/>
                <ReferenceLine y={-3} stroke={`${C.coral}60`} strokeDasharray="4 2"/>
                <ReferenceLine y={1.5} stroke={`${C.amber}40`} strokeDasharray="3 3"/>
                <ReferenceLine y={-1.5} stroke={`${C.amber}40`} strokeDasharray="3 3"/>
                <Scatter data={stripData} shape={(props:any)=>{const{cx,cy,payload}=props;return<circle cx={cx} cy={cy} r={7} fill={payload.severity==='extreme'?C.coral:C.amber} fillOpacity={.8} stroke="rgba(0,0,0,.2)"/>}}/>
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        ):(
          <><div style={{height:200}}><ResponsiveContainer width="100%" height="100%"><BarChart data={outItem.severity_data||[]} margin={{top:5,right:10,bottom:5,left:0}}><CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false}/><XAxis dataKey="label" {...AX}/><YAxis {...AX}/><RTooltip content={<Tip/>}/><Bar dataKey="count" name="Count" radius={[4,4,0,0]}>{(outItem.severity_data||[]).map((d:any,i:number)=><Cell key={i} fill={d.fill||C.coral} opacity={.85}/>)}<LabelList dataKey="count" position="top" style={{fontSize:10,fill:'rgba(255,255,255,.4)'}}/></Bar></BarChart></ResponsiveContainer></div>
          <div style={{display:'grid',gridTemplateColumns:'repeat(4,1fr)',gap:8,marginTop:12}}>{[['Extreme',outItem.extreme_count,C.coral],['Mild',outItem.mild_count,C.amber],['High',outItem.high_count,C.orange],['Low',outItem.low_count,C.blue]].map(([l,v,c])=>(<div key={l as string} style={{padding:'8px 4px',textAlign:'center',borderRadius:8,background:`${c}0a`,border:`1px solid ${c}20`}}><p style={{fontSize:9,color:'rgba(255,255,255,.3)'}}>{l}</p><p style={{fontSize:16,fontWeight:700,color:c as string}}>{v}</p></div>))}</div></>
        )}
        <Insight icon={AlertTriangle} color={C.coral} text={`${outItem.extreme_count} extreme outliers (|z|>3). Fence: [${nf(outItem.fence_low)}, ${nf(outItem.fence_high)}]. Mean=${nf(outItem.mean)} vs Median=${nf(outItem.median)}.`}/>
      </Card>
    )
  }

  // ── Cohort ────────────────────────────────────────────────────────────────
  function renderCohort(){
    if(!coh.length) return <Empty msg="Need 2+ categorical columns"/>
    const rv=rel('cohort',a)
    if(!cohItem) return <Empty msg="No data"/>
    const stackColors=cohLabels.map((_:any,i:number)=>SEQ[i%SEQ.length])
    return(
      <Card title="Cohort Analysis" sub={`${cohItem.display_row} × ${cohItem.display_col} · ${cohItem.display_metric}`} icon={Users} col={C.cyan} relevance={rv}
        bar={<>{coh.length>1&&<Sel opts={coh.map((_:any,i:number)=>`${coh[i].display_row}×${coh[i].display_col}`)} val={`${cohItem.display_row}×${cohItem.display_col}`} onChange={v=>setCohIdx(coh.findIndex((_:any,i:number)=>`${coh[i].display_row}×${coh[i].display_col}`===v))}/> }<TypePicker opts={T_COH} val={cohType} onChange={setCohType}/></>}>
        <div style={{height:Math.max(260,cohItem.data?.length*40||260)}}>
          <ResponsiveContainer width="100%" height="100%">
            {cohType==='heatmap'?(
              <BarChart data={cohItem.data||[]} margin={{top:5,right:10,bottom:55,left:90}}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false}/>
                <XAxis dataKey="category" {...AX} tick={({x,y,payload}:any)=><text x={x} y={y+6} textAnchor="end" fontSize={9} fill="rgba(255,255,255,.3)" transform={`rotate(-30,${x},${y})`}>{String(payload.value).slice(0,14)}</text>} height={55}/>
                <YAxis {...AX} tickFormatter={v=>nf(v,0)}/>
                <RTooltip content={<Tip/>}/>
                <Legend wrapperStyle={{fontSize:11}}/>
                {cohLabels.map((label:string,i:number)=><Bar key={label} dataKey={label} name={label} fill={stackColors[i]} radius={[3,3,0,0]} maxBarSize={28} opacity={.85}/>)}
              </BarChart>
            ):cohType==='stacked'?(
              <BarChart data={cohItem.data||[]} margin={{top:5,right:10,bottom:55,left:0}}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false}/>
                <XAxis dataKey="category" {...AX} tick={({x,y,payload}:any)=><text x={x} y={y+6} textAnchor="end" fontSize={9} fill="rgba(255,255,255,.3)" transform={`rotate(-30,${x},${y})`}>{String(payload.value).slice(0,14)}</text>} height={55}/>
                <YAxis {...AX} tickFormatter={v=>nf(v,0)}/>
                <RTooltip content={<Tip/>}/>
                <Legend wrapperStyle={{fontSize:11}}/>
                {cohLabels.map((label:string,i:number)=><Bar key={label} dataKey={label} name={label} stackId="a" fill={stackColors[i]} opacity={.85}/>)}
              </BarChart>
            ):(
              <BarChart data={cohItem.data||[]} layout="vertical" margin={{left:90,right:10,top:5,bottom:5}}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" horizontal={false}/>
                <XAxis type="number" {...AX} tickFormatter={v=>nf(v,0)}/>
                <YAxis type="category" dataKey="category" {...AX} width={85}/>
                <RTooltip content={<Tip/>}/>
                <Legend wrapperStyle={{fontSize:11}}/>
                {cohLabels.map((label:string,i:number)=><Bar key={label} dataKey={label} name={label} fill={stackColors[i]} radius={[0,3,3,0]} maxBarSize={22} opacity={.85}/>)}
              </BarChart>
            )}
          </ResponsiveContainer>
        </div>
        <Insight text={`Cross-tabulation of ${cohItem.display_row} vs ${cohItem.display_col}. Each bar group = one ${cohItem.display_row} value.`}/>
      </Card>
    )
  }

  // ── Multi-Metric ──────────────────────────────────────────────────────────
  function renderMultiMetric(){
    if(!mm.length) return <Empty msg="Need 3+ numeric columns + categorical"/>
    const rv=rel('multi_metric',a)
    if(!mmItem) return <Empty msg="No data"/>
    const cats=mmItem.categories||[], metrics=mmItem.metrics||[], dmets=mmItem.display_metrics||[]
    const normKey=(cat:string,m:string)=>`${cat}_norm`
    return(
      <Card title="Multi-Metric Comparison" sub={`${mmItem.display_dimension} · ${metrics.length} metrics`} icon={Sigma} col={C.orange} relevance={rv}
        bar={<>{mm.length>1&&<Sel opts={mm.map((m:any)=>m.display_dimension)} val={mmItem.display_dimension} onChange={v=>setMmIdx(mm.findIndex((m:any)=>m.display_dimension===v))}/> }<TypePicker opts={T_MMT} val={mmType} onChange={setMmType}/></>}>
        {mmType==='radar'?(
          <div style={{height:320}}><ResponsiveContainer width="100%" height="100%"><RadarChart data={mmItem.radar_data||[]}><PolarGrid stroke="rgba(255,255,255,.08)"/><PolarAngleAxis dataKey="category" tick={{fill:'rgba(255,255,255,.4)',fontSize:9}}/><PolarRadiusAxis tick={{fill:'rgba(255,255,255,.2)',fontSize:7}}/>{metrics.slice(0,4).map((m:string,j:number)=><Radar key={m} name={dmets[j]||m} dataKey={`${m}_norm`} stroke={SEQ[j]} fill={SEQ[j]} fillOpacity={.1} strokeWidth={2}/>)}<Legend wrapperStyle={{fontSize:11}}/><RTooltip content={<Tip/>}/></RadarChart></ResponsiveContainer></div>
        ):mmType==='normalized'?(
          <div style={{height:Math.max(260,cats.length*40)}}><ResponsiveContainer width="100%" height="100%"><BarChart data={mmItem.radar_data||[]} layout="vertical" margin={{left:80,right:10,top:5,bottom:5}}><CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" horizontal={false}/><XAxis type="number" domain={[0,1]} {...AX} tickFormatter={v=>`${(v*100).toFixed(0)}%`}/><YAxis type="category" dataKey="category" {...AX} width={75}/><RTooltip content={<Tip/>}/><Legend wrapperStyle={{fontSize:11}}/>{metrics.map((m:string,j:number)=><Bar key={m} dataKey={`${m}_norm`} name={dmets[j]||m} fill={SEQ[j]} radius={[0,3,3,0]} maxBarSize={14} opacity={.85}/>)}</BarChart></ResponsiveContainer></div>
        ):(
          <div style={{height:Math.max(260,mmItem.grouped_data?.length*50||260)}}><ResponsiveContainer width="100%" height="100%"><BarChart data={mmItem.grouped_data||[]} margin={{top:5,right:10,bottom:55,left:0}}><CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false}/><XAxis dataKey="metric" {...AX} tick={({x,y,payload}:any)=><text x={x} y={y+6} textAnchor="end" fontSize={9} fill="rgba(255,255,255,.3)" transform={`rotate(-30,${x},${y})`}>{String(payload.value).slice(0,14)}</text>} height={55}/><YAxis {...AX} tickFormatter={v=>nf(v,0)}/><RTooltip content={<Tip/>}/><Legend wrapperStyle={{fontSize:11}}/>{cats.slice(0,6).map((cat:string,j:number)=><Bar key={cat} dataKey={cat} name={cat} fill={SEQ[j]} radius={[3,3,0,0]} maxBarSize={28} opacity={.85}/>)}</BarChart></ResponsiveContainer></div>
        )}
        <Insight text={`Comparing ${metrics.length} metrics across ${cats.length} categories of ${mmItem.display_dimension}.`}/>
      </Card>
    )
  }

  // ── Percentiles ───────────────────────────────────────────────────────────
  function renderPercentile(){
    if(!pbd.length) return <Empty msg="No percentile data"/>
    const rv=rel('percentile',a)
    if(!pctItem) return <Empty msg="No item"/>
    return(
      <Card title="Percentile Distribution" sub={pctItem.display_name} icon={Percent} col={C.blue} relevance={rv}
        bar={<>{pbd.length>1&&<Sel opts={pbd.map((p:any)=>p.display_name)} val={pctItem.display_name} onChange={v=>setPctIdx(pbd.findIndex((p:any)=>p.display_name===v))}/> }<TypePicker opts={T_PCT} val={pctType} onChange={setPctType}/></>}>
        {pctType==='steps'?(
          <div style={{height:260}}><ResponsiveContainer width="100%" height="100%"><AreaChart data={pctItem.steps||[]} margin={{top:5,right:10,bottom:5,left:0}}><defs><linearGradient id="pctFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={C.blue} stopOpacity={.4}/><stop offset="100%" stopColor={C.blue} stopOpacity={.02}/></linearGradient></defs><CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false}/><XAxis dataKey="label" {...AX}/><YAxis {...AX} tickFormatter={v=>nf(v,0)}/><RTooltip content={<Tip/>}/><Area type="stepAfter" dataKey="band_high" name="P band high" stroke="transparent" fill={`${C.blue}20`}/><Area type="stepAfter" dataKey="value" name="Percentile" stroke={C.blue} fill="url(#pctFill)" strokeWidth={2.5}/><ReferenceLine y={pctItem.mean} stroke={C.gold} strokeDasharray="4 2" label={{value:'Mean',position:'right',fill:C.gold,fontSize:9}}/></AreaChart></ResponsiveContainer></div>
        ):pctType==='bar'?(
          <div style={{height:240}}><ResponsiveContainer width="100%" height="100%"><BarChart data={pctItem.bands||[]} margin={{top:5,right:10,bottom:5,left:0}}><CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false}/><XAxis dataKey="label" {...AX}/><YAxis {...AX} tickFormatter={v=>nf(v,0)}/><RTooltip content={<Tip/>}/><ReferenceLine y={pctItem.mean} stroke={C.gold} strokeDasharray="4 2" label={{value:'Mean',position:'right',fill:C.gold,fontSize:9}}/><Bar dataKey="value" name="Value" radius={[4,4,0,0]}>{(pctItem.bands||[]).map((b:any,i:number)=><Cell key={i} fill={b.fill||SEQ[i]}/>)}<LabelList dataKey="value" position="top" formatter={(v:any)=>nf(v)} style={{fontSize:9,fill:'rgba(255,255,255,.3)'}}/></Bar></BarChart></ResponsiveContainer></div>
        ):(
          // bands — visual band chart
          <div>
            <div style={{marginBottom:12,padding:'12px 16px',borderRadius:10,background:'rgba(255,255,255,.03)',border:'1px solid rgba(255,255,255,.06)'}}>
              <div style={{display:'flex',justifyContent:'space-between',marginBottom:8,fontSize:11,color:'rgba(255,255,255,.4)'}}>
                <span>P10: {nf(pctItem.p10)}</span><span>P25: {nf(pctItem.p25)}</span><span>Median: {nf(pctItem.p50)}</span><span>P75: {nf(pctItem.p75)}</span><span>P90: {nf(pctItem.p90)}</span>
              </div>
              {[{lo:pctItem.p10,hi:pctItem.p25,label:'P10–P25',col:'#5C6BC0'},{lo:pctItem.p25,hi:pctItem.p50,label:'P25–P50',col:'#3498DB'},{lo:pctItem.p50,hi:pctItem.p75,label:'P50–P75',col:'#2ECC71'},{lo:pctItem.p75,hi:pctItem.p90,label:'P75–P90',col:'#F39C12'}].map((band,i)=>{
                const range=(pctItem.p90||0)-(pctItem.p10||0)||1, start=((band.lo||0)-(pctItem.p10||0))/range*100, width=((band.hi||0)-(band.lo||0))/range*100
                return(<div key={i} style={{marginBottom:6}}><div style={{display:'flex',justifyContent:'space-between',fontSize:10,color:'rgba(255,255,255,.3)',marginBottom:3}}><span>{band.label}</span><span>{nf(band.lo)} → {nf(band.hi)}</span></div><div style={{position:'relative',height:14,background:'rgba(255,255,255,.05)',borderRadius:7,overflow:'hidden'}}><div style={{position:'absolute',left:`${start}%`,width:`${width}%`,height:'100%',background:band.col,opacity:.75,borderRadius:7}}/></div></div>)
              })}
              <div style={{display:'flex',gap:4,marginTop:8}}><div style={{flex:1,height:3,borderRadius:2,background:`${C.gold}80`}}/></div>
              <p style={{fontSize:10,color:'rgba(255,255,255,.3)',marginTop:4}}>Mean: {nf(pctItem.mean)} · Std: {nf(pctItem.std)}</p>
            </div>
          </div>
        )}
        <Insight text={`P25–P75 (IQR) spans ${nf(pctItem.p25)} to ${nf(pctItem.p75)}. ${(pctItem.mean||0)>(pctItem.p50||0)?'Mean > Median — right-skewed distribution.':'Mean ≈ Median — approximately symmetric.'}`}/>
      </Card>
    )
  }

  // ── Pareto ────────────────────────────────────────────────────────────────
  function renderPareto(){
    if(!prt.length) return <Empty msg="No Pareto data"/>
    const rv=rel('pareto',a)
    if(!prtItem) return <Empty msg="No item"/>
    const data=prtItem.data||[]
    return(
      <Card title="Pareto Analysis (80/20)" sub={`${prtItem.display_dimension} by ${prtItem.display_metric} · Vital few: ${prtItem.vital_few_count}`} icon={GitMerge} col={C.lime} relevance={rv}
        bar={<>{prt.length>1&&<Sel opts={prt.map((p:any)=>`${p.display_dimension}×${p.display_metric}`)} val={`${prtItem.display_dimension}×${prtItem.display_metric}`} onChange={v=>setPrtIdx(prt.findIndex((p:any)=>`${p.display_dimension}×${p.display_metric}`===v))}/> }<TypePicker opts={T_PRT} val={prtType} onChange={setPrtType}/></>}>
        <div style={{height:300}}>
          <ResponsiveContainer width="100%" height="100%">
            {prtType==='area'?(
              <AreaChart data={data} margin={{top:5,right:30,bottom:55,left:0}}>
                <defs><linearGradient id="rtFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={C.lime} stopOpacity={.3}/><stop offset="100%" stopColor={C.lime} stopOpacity={.02}/></linearGradient></defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false}/>
                <XAxis dataKey="category" {...AX} tick={({x,y,payload}:any)=><text x={x} y={y+6} textAnchor="end" fontSize={9} fill="rgba(255,255,255,.3)" transform={`rotate(-30,${x},${y})`}>{String(payload.value).slice(0,14)}</text>} height={55}/>
                <YAxis {...AX} tickFormatter={v=>nf(v,0)}/>
                <RTooltip content={<Tip/>}/>
                <Area type="monotone" dataKey="running_total" name="Running Total" stroke={C.lime} fill="url(#rtFill)" strokeWidth={2.5}/>
              </AreaChart>
            ):(
              <ComposedChart data={data} margin={{top:5,right:30,bottom:55,left:0}}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false}/>
                <XAxis dataKey="category" {...AX} tick={({x,y,payload}:any)=><text x={x} y={y+6} textAnchor="end" fontSize={9} fill="rgba(255,255,255,.3)" transform={`rotate(-30,${x},${y})`}>{String(payload.value).slice(0,14)}</text>} height={55}/>
                <YAxis yAxisId="l" {...AX} tickFormatter={v=>nf(v,0)}/>
                <YAxis yAxisId="r" orientation="right" {...AX} tickFormatter={v=>`${(+v).toFixed(0)}%`}/>
                <RTooltip content={<Tip/>}/>
                <Bar yAxisId="l" dataKey="value" name={prtItem.display_metric} radius={[3,3,0,0]} maxBarSize={32}>
                  {data.map((d:any,i:number)=><Cell key={i} fill={d.is_vital_few?C.gold:`${C.gold}40`} opacity={.85}/>)}
                </Bar>
                <Line yAxisId="r" type="monotone" dataKey="cumulative_pct" name="Cumulative %" stroke={C.coral} strokeWidth={2.5} dot={{r:3}} activeDot={{r:5}}/>
                <ReferenceLine yAxisId="r" y={80} stroke={`${C.teal}80`} strokeDasharray="6 3" label={{value:'80%',position:'right',fill:C.teal,fontSize:10}}/>
              </ComposedChart>
            )}
          </ResponsiveContainer>
        </div>
        <Insight icon={Flame} color={C.lime} text={`Pareto rule: ${prtItem.vital_few_count} categories (${prtItem.vital_few_pct?.toFixed(0)}% of total) drive 80% of ${prtItem.display_metric}. Gold bars = vital few.`}/>
      </Card>
    )
  }

  // ── Value at Risk ─────────────────────────────────────────────────────────
  function renderVaR(){
    const var_ = a.value_at_risk||[]; if(!var_.length) return <Empty msg="Need numeric columns with variance"/>
    const rv=rel('value_at_risk',a)
    const item=var_[varIdx]||var_[0]; if(!item) return <Empty msg="No data"/>
    const hist=item.histogram||[]
    return(
      <Card title="Statistical Risk Analysis" sub={`${item.display_name} · Risk Tier: ${item.risk_tier}`} icon={ShieldAlert} col={item.risk_tier==='High'?C.coral:item.risk_tier==='Medium'?C.amber:C.green} relevance={rv}
        bar={var_.length>1?<Sel opts={var_.map((v:any)=>v.display_name)} val={item.display_name} onChange={v=>setVarIdx(var_.findIndex((x:any)=>x.display_name===v))}/>:undefined}>
        <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16}}>
          <div>
            <div style={{height:200}}><ResponsiveContainer width="100%" height="100%"><BarChart data={hist} margin={{top:5,right:5,bottom:5,left:0}}><CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false}/><XAxis dataKey="bin" {...AX} interval="preserveStartEnd"/><YAxis {...AX}/><RTooltip content={<Tip/>}/><Bar dataKey="count" name="Count" radius={[3,3,0,0]}>{hist.map((d:any,i:number)=><Cell key={i} fill={d.is_risk?C.coral:C.blue} opacity={.8}/>)}</Bar><ReferenceLine x={item.var_95} stroke={C.amber} strokeDasharray="4 2" label={{value:'VaR95',position:'top',fill:C.amber,fontSize:9}}/></BarChart></ResponsiveContainer></div>
            <p style={{fontSize:10,color:'rgba(255,255,255,.3)',marginTop:6,textAlign:'center'}}>Red = below VaR 95% threshold</p>
          </div>
          <div style={{display:'flex',flexDirection:'column',gap:8}}>
            {[['VaR 95%',item.var_95,C.amber,'Worst 5% scenario'],['VaR 99%',item.var_99,C.coral,'Worst 1% scenario'],['CVaR 95%',item.cvar_95,C.pink,'Expected loss below VaR'],['Mean',item.mean,C.gold,'Expected value'],['Best 5%',item.best_case,C.green,'Best 5% scenario'],['CV %',`${item.cv_pct?.toFixed(1)}%`,item.risk_tier==='High'?C.coral:item.risk_tier==='Medium'?C.amber:C.green,'Volatility measure']].map(([l,v,c,desc])=>(
              <div key={l as string} style={{padding:'10px 12px',borderRadius:10,background:`${c}0a`,border:`1px solid ${c}20`}}>
                <div style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}>
                  <div><p style={{fontSize:10,color:'rgba(255,255,255,.35)'}}>{l}</p><p style={{fontSize:9,color:'rgba(255,255,255,.2)'}}>{desc}</p></div>
                  <span style={{fontWeight:700,fontSize:14,color:c as string}}>{typeof v==='number'?nf(v):v}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
        <Insight icon={AlertTriangle} color={item.risk_tier==='High'?C.coral:C.amber} text={`Risk tier: ${item.risk_tier}. CV=${item.cv_pct?.toFixed(1)}% — ${item.risk_tier==='High'?'High volatility, significant uncertainty in predictions.':item.risk_tier==='Medium'?'Moderate variation — manageable risk.':'Low volatility — stable and predictable.'}`}/>
      </Card>
    )
  }

  // ── Moving Statistics ─────────────────────────────────────────────────────
  function renderMovingStats(){
    const ms=a.moving_statistics||[]; if(!ms.length) return <Empty msg="Need 15+ data points"/>
    const rv=rel('moving_stats',a)
    const item=ms[msIdx]||ms[0]; if(!item) return <Empty msg="No data"/>
    const windows=item.windows||[3]
    return(
      <Card title="Moving Average Analysis" sub={`${item.display_name} · Window: ${windows.join('/')} periods`} icon={TrendingUp} col={C.cyan} relevance={rel('trend',a)}
        bar={ms.length>1?<Sel opts={ms.map((m:any)=>m.display_name)} val={item.display_name} onChange={v=>setMsIdx(ms.findIndex((x:any)=>x.display_name===v))}/>:undefined}>
        <div style={{height:280}}><ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={(item.data||[]).slice(-60)} margin={{top:5,right:10,bottom:5,left:0}}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false}/>
            <XAxis dataKey="index" {...AX} tickFormatter={v=>`T${v+1}`}/><YAxis {...AX} tickFormatter={v=>nf(v,0)}/>
            <RTooltip content={<Tip/>}/><Legend wrapperStyle={{fontSize:11}}/>
            <Brush dataKey="index" height={14} stroke="rgba(255,255,255,.06)" fill="#0f0f1a" travellerWidth={4}/>
            <Bar dataKey="value" name="Actual" fill={`${C.blue}30`} radius={[2,2,0,0]} maxBarSize={20}/>
            {windows.includes(3)&&<Line type="monotone" dataKey="ma3" name="MA3" stroke={C.gold} strokeWidth={2.5} dot={false}/>}
            {windows.includes(7)&&<Line type="monotone" dataKey="ma7" name="MA7" stroke={C.teal} strokeWidth={2} dot={false} strokeDasharray="5 3"/>}
            {windows.includes(3)&&<Area type="monotone" dataKey="upper3" name="Upper Band" stroke="transparent" fill={`${C.gold}08`} activeDot={false}/>}
            {windows.includes(3)&&<Area type="monotone" dataKey="lower3" name="Lower Band" stroke="transparent" fill="transparent" activeDot={false}/>}
            <ReferenceLine y={item.overall_mean} stroke="rgba(255,255,255,.2)" strokeDasharray="4 4" label={{value:'Avg',position:'right',fill:'rgba(255,255,255,.3)',fontSize:9}}/>
          </ComposedChart>
        </ResponsiveContainer></div>
        <Insight text={`Overall mean: ${nf(item.overall_mean)} · Std dev: ${nf(item.overall_std)}. MA smooths noise to reveal underlying trend.`}/>
      </Card>
    )
  }

  // ── Concentration (Lorenz / Gini / HHI) ──────────────────────────────────
  function renderConcentration(){
    const conc=a.concentration||[]; if(!conc.length) return <Empty msg="Need categorical + numeric columns"/>
    const rv=rel('concentration',a)
    const item=conc[cIdx]||conc[0]; if(!item) return <Empty msg="No data"/>
    const lorenz=item.lorenz_data||[]
    return(
      <Card title="Market Concentration" sub={`${item.display_dimension} · Gini=${item.gini_pct}% · ${item.concentration_level}`} icon={GitMerge} col={C.indigo} relevance={rv}
        bar={conc.length>1?<Sel opts={conc.map((_:any,i:number)=>`${conc[i].display_dimension}×${conc[i].display_metric}`)} val={`${item.display_dimension}×${item.display_metric}`} onChange={v=>setCIdx(conc.findIndex((_:any,i:number)=>`${conc[i].display_dimension}×${conc[i].display_metric}`===v))}/>:undefined}>
        <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16}}>
          <div>
            <p style={{fontSize:11,color:'rgba(255,255,255,.4)',marginBottom:8}}>Lorenz Curve</p>
            <div style={{height:220}}><ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={lorenz} margin={{top:5,right:5,bottom:5,left:0}}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)"/>
                <XAxis dataKey="x" {...AX} tickFormatter={v=>`${(v*100).toFixed(0)}%`}/><YAxis {...AX} tickFormatter={v=>`${(v*100).toFixed(0)}%`}/>
                <RTooltip content={<Tip/>}/>
                <Line type="monotone" dataKey="equality" name="Equal Distribution" stroke="rgba(255,255,255,.2)" strokeWidth={1} dot={false} strokeDasharray="4 4"/>
                <Area type="monotone" dataKey="y" name="Lorenz Curve" stroke={C.gold} fill={`${C.gold}15`} strokeWidth={2.5} dot={false}/>
              </ComposedChart>
            </ResponsiveContainer></div>
          </div>
          <div style={{display:'flex',flexDirection:'column',gap:8}}>
            {[['Gini Index',`${item.gini_pct}%`,C.gold,'0%=perfect equality, 100%=monopoly'],['HHI Score',`${item.hhi_pct?.toFixed(1)}%`,item.hhi>0.25?C.coral:item.hhi>0.10?C.amber:C.green,'<10%=competitive, >25%=concentrated'],['Top 1 Share',`${item.top1_share}%`,C.coral,'Share of largest player'],['Top 3 Share',`${item.top3_share?.toFixed(0)}%`,C.amber,'Combined top 3 share'],['Level',item.concentration_level,item.hhi>0.25?C.coral:item.hhi>0.10?C.amber:C.green,'Market structure']].map(([l,v,c,desc])=>(
              <div key={l as string} style={{padding:'10px 12px',borderRadius:10,background:`${c}0a`,border:`1px solid ${c}20`}}>
                <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-start'}}>
                  <div><p style={{fontSize:10,color:'rgba(255,255,255,.35)'}}>{l}</p><p style={{fontSize:9,color:'rgba(255,255,255,.2)'}}>{desc}</p></div>
                  <span style={{fontWeight:700,fontSize:13,color:c as string,marginLeft:8}}>{v}</span>
                </div>
              </div>
            ))}
            <div style={{marginTop:4,padding:'10px 12px',borderRadius:10,background:'rgba(255,255,255,.03)',border:'1px solid rgba(255,255,255,.06)'}}>
              <p style={{fontSize:10,color:'rgba(255,255,255,.35)',marginBottom:6}}>Category Shares</p>
              {(item.share_data||[]).slice(0,5).map((d:any,i:number)=>(
                <div key={i} style={{display:'flex',alignItems:'center',gap:8,marginBottom:4}}>
                  <span style={{fontSize:10,color:'rgba(255,255,255,.4)',minWidth:80,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{d.category}</span>
                  <div style={{flex:1,height:5,background:'rgba(255,255,255,.06)',borderRadius:3,overflow:'hidden'}}><div style={{width:`${d.share_pct}%`,height:'100%',background:SEQ[i%SEQ.length]}}/></div>
                  <span style={{fontSize:10,color:'rgba(255,255,255,.5)',minWidth:35,textAlign:'right'}}>{d.share_pct}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </Card>
    )
  }

  // ── Benchmark Comparison ──────────────────────────────────────────────────
  function renderBenchmark(){
    const bm=a.benchmark_comparison||[]; if(!bm.length) return <Empty msg="No industry benchmarks available for this domain"/>
    return(
      <Card title="Industry Benchmark Comparison" sub={`${bm.length} metrics vs benchmarks`} icon={Award} col={C.green} relevance={'Strong'}>
        <div style={{height:Math.max(200,bm.length*60)}}><ResponsiveContainer width="100%" height="100%">
          <BarChart data={bm} layout="vertical" margin={{left:100,right:80,top:5,bottom:5}}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" horizontal={false}/>
            <XAxis type="number" {...AX} tickFormatter={v=>nf(v,0)}/>
            <YAxis type="category" dataKey="display_name" {...AX} width={95}/>
            <RTooltip content={({active,payload}:any)=>{
              if(!active||!payload?.[0]) return null; const d=payload[0].payload
              return(<div style={{background:'#10101c',border:'1px solid rgba(212,175,55,.2)',borderRadius:8,padding:'10px 14px',minWidth:200}}>
                <p style={{fontWeight:700,color:'#fff',marginBottom:6}}>{d.display_name}</p>
                <p style={{fontSize:11,color:'rgba(255,255,255,.5)'}}>Actual: <b style={{color:d.status==='above'?C.green:C.coral}}>{d.formatted_actual}</b></p>
                <p style={{fontSize:11,color:'rgba(255,255,255,.5)'}}>Benchmark: <b style={{color:'rgba(255,255,255,.7)'}}>{d.formatted_benchmark}</b></p>
                <p style={{fontSize:11,color:d.status==='above'?C.green:C.coral,marginTop:4}}>{d.status==='above'?'▲':'▼'} {Math.abs(d.diff_pct||0).toFixed(1)}% vs benchmark</p>
              </div>)
            }}/>
            <Legend wrapperStyle={{fontSize:11}}/>
            <ReferenceLine x={0} stroke="rgba(255,255,255,.1)"/>
            <Bar dataKey="actual" name="Actual" radius={[0,4,4,0]} maxBarSize={28}>{bm.map((d:any,i:number)=><Cell key={i} fill={d.status==='above'?C.green:C.coral} opacity={.85}/>)}<LabelList dataKey="formatted_actual" position="right" style={{fontSize:9,fill:'rgba(255,255,255,.4)'}}/></Bar>
            <Bar dataKey="benchmark" name="Benchmark" fill={`${C.blue}50`} radius={[0,4,4,0]} maxBarSize={14}/>
          </BarChart>
        </ResponsiveContainer></div>
        <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fill,minmax(160px,1fr))',gap:10,marginTop:12}}>
          {bm.map((d:any,i:number)=>(
            <div key={i} style={{padding:'10px 12px',borderRadius:10,background:d.status==='above'?'rgba(46,204,113,.06)':'rgba(255,107,107,.06)',border:`1px solid ${d.status==='above'?'rgba(46,204,113,.2)':'rgba(255,107,107,.2)'}`}}>
              <p style={{fontSize:10,color:'rgba(255,255,255,.4)',marginBottom:4}}>{d.display_name}</p>
              <div style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}>
                <span style={{fontWeight:700,fontSize:14,color:d.status==='above'?C.green:C.coral}}>{d.formatted_actual}</span>
                <span style={{fontSize:10,color:'rgba(255,255,255,.3)'}}>vs {d.formatted_benchmark}</span>
              </div>
              <span style={{fontSize:9,padding:'2px 6px',borderRadius:20,background:d.status==='above'?'rgba(46,204,113,.1)':'rgba(255,107,107,.1)',color:d.status==='above'?C.green:C.coral,fontWeight:700}}>{d.rating?.replace('_',' ')}</span>
            </div>
          ))}
        </div>
      </Card>
    )
  }

  // ── Data Quality Detail ───────────────────────────────────────────────────
  function renderQualityDetail(){
    const dq=a.data_quality_detail||[]; if(!dq.length) return <Empty msg="No quality data"/>
    const avgScore=dq.length?dq.reduce((s:number,d:any)=>s+d.quality_score,0)/dq.length:0
    return(
      <Card title="Column Quality Report" sub={`${dq.length} columns · Avg score: ${avgScore.toFixed(0)}%`} icon={ShieldAlert} col={C.green} relevance={'Strong'}>
        <div style={{height:Math.max(200,dq.length*28)}}><ResponsiveContainer width="100%" height="100%">
          <BarChart data={dq} layout="vertical" margin={{left:120,right:60,top:5,bottom:5}}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" horizontal={false}/>
            <XAxis type="number" domain={[0,100]} {...AX} tickFormatter={v=>`${v}%`}/>
            <YAxis type="category" dataKey="display_name" {...AX} width={115}/>
            <RTooltip content={({active,payload}:any)=>{
              if(!active||!payload?.[0]) return null; const d=payload[0].payload
              return(<div style={{background:'#10101c',border:'1px solid rgba(212,175,55,.2)',borderRadius:8,padding:'10px 14px',minWidth:200}}>
                <p style={{fontWeight:700,color:'#fff',marginBottom:6}}>{d.display_name}</p>
                <p style={{fontSize:11,color:'rgba(255,255,255,.5)'}}>Type: <b style={{color:'rgba(255,255,255,.7)'}}>{d.col_type}</b></p>
                <p style={{fontSize:11,color:'rgba(255,255,255,.5)'}}>Nulls: <b style={{color:d.null_pct>10?C.coral:C.green}}>{d.null_pct}%</b></p>
                <p style={{fontSize:11,color:'rgba(255,255,255,.5)'}}>Unique: <b style={{color:'rgba(255,255,255,.7)'}}>{d.unique_pct}%</b></p>
                {d.issues?.length>0&&<p style={{fontSize:10,color:C.amber,marginTop:4}}>{d.issues.join(', ')}</p>}
              </div>)
            }}/>
            <ReferenceLine x={80} stroke={`${C.green}60`} strokeDasharray="4 2" label={{value:'Good',position:'top',fill:C.green,fontSize:8}}/>
            <ReferenceLine x={50} stroke={`${C.amber}60`} strokeDasharray="4 2" label={{value:'Warn',position:'top',fill:C.amber,fontSize:8}}/>
            <Bar dataKey="quality_score" name="Quality Score" radius={[0,4,4,0]} maxBarSize={20}>{dq.map((d:any,i:number)=><Cell key={i} fill={d.fill||C.green} opacity={.85}/>)}<LabelList dataKey="quality_score" position="right" formatter={(v:any)=>`${v}%`} style={{fontSize:9,fill:'rgba(255,255,255,.4)'}}/></Bar>
          </BarChart>
        </ResponsiveContainer></div>
        <div style={{display:'flex',gap:12,marginTop:10,flexWrap:'wrap'}}>
          {['good','warning','critical'].map(s=>{
            const count=dq.filter((d:any)=>d.status===s).length; const col=s==='good'?C.green:s==='warning'?C.amber:C.coral
            return(<div key={s} style={{display:'flex',alignItems:'center',gap:6,padding:'5px 10px',borderRadius:8,background:`${col}0d`,border:`1px solid ${col}25`}}><span style={{width:8,height:8,borderRadius:'50%',background:col}}/><span style={{fontSize:11,color:col,fontWeight:600}}>{s}: {count}</span></div>)
          })}
        </div>
      </Card>
    )
  }

  // ── Summary Stats Table ───────────────────────────────────────────────────
  function renderSummaryStats(){
    const ss=a.summary_stats||[]; if(!ss.length) return <Empty msg="No numeric columns"/>
    const cols=['display_name','count','mean','median','std','min','max','skewness','cv_pct','null_count']
    const labels={display_name:'Column',count:'Count',mean:'Mean',median:'Median',std:'Std Dev',min:'Min',max:'Max',skewness:'Skewness',cv_pct:'CV %',null_count:'Nulls'}
    return(
      <Card title="Descriptive Statistics" sub={`${ss.length} numeric columns · full breakdown`} icon={Sigma} col={C.purple} relevance={'Strong'}>
        <div style={{overflowX:'auto'}}>
          <table style={{width:'100%',borderCollapse:'collapse',fontSize:11,minWidth:700}}>
            <thead><tr>{cols.map(c=><th key={c} style={{padding:'8px 10px',textAlign:c==='display_name'?'left':'right',color:'rgba(212,175,55,.7)',borderBottom:'1px solid rgba(212,175,55,.12)',fontWeight:600,whiteSpace:'nowrap'}}>{(labels as any)[c]}</th>)}</tr></thead>
            <tbody>
              {ss.map((row:any,i:number)=>(
                <tr key={i} style={{background:i%2===0?'rgba(255,255,255,.01)':'transparent'}}>
                  {cols.map(c=>(
                    <td key={c} style={{padding:'8px 10px',textAlign:c==='display_name'?'left':'right',color:'rgba(255,255,255,.6)',borderBottom:'1px solid rgba(255,255,255,.04)',whiteSpace:'nowrap'}}>
                      {c==='display_name'?<span style={{fontWeight:600,color:'rgba(255,255,255,.8)'}}>{row[c]}</span>
                      :c==='null_count'?<span style={{color:row[c]>0?C.amber:'rgba(255,255,255,.35)'}}>{row[c]}</span>
                      :c==='skewness'?<span style={{color:Math.abs(row[c])>1?C.amber:'rgba(255,255,255,.6)'}}>{(row[c]||0).toFixed(2)}</span>
                      :c==='cv_pct'?<span style={{color:(row[c]||0)>50?C.coral:(row[c]||0)>20?C.amber:C.green}}>{(row[c]||0).toFixed(1)}%</span>
                      :c==='mean'?<span style={{fontWeight:600,color:C.gold}}>{row.formatted_mean||nf(row[c])}</span>
                      :nf(row[c])}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    )
  }

  // ── Frequency Analysis ────────────────────────────────────────────────────
  function renderFrequency(){
    const fa=a.frequency_analysis||[]; if(!fa.length) return <Empty msg="No categorical columns"/>
    const item=fa[fIdx]||fa[0]; if(!item) return <Empty msg="No data"/>
    const topData=(item.data||[]).slice(0,15)
    return(
      <Card title="Frequency Analysis" sub={`${item.display_name} · ${item.unique} unique values · Entropy: ${item.entropy}`} icon={BarChart3} col={C.slate} relevance={rel('distribution',a)}
        bar={fa.length>1?<Sel opts={fa.map((f:any)=>f.display_name)} val={item.display_name} onChange={v=>setFIdx(fa.findIndex((x:any)=>x.display_name===v))}/>:undefined}>
        <div style={{height:Math.max(240,topData.length*28)}}><ResponsiveContainer width="100%" height="100%">
          <BarChart data={topData} layout="vertical" margin={{left:120,right:80,top:5,bottom:5}}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" horizontal={false}/>
            <XAxis type="number" {...AX} tickFormatter={v=>`${v}%`}/>
            <YAxis type="category" dataKey="category" {...AX} width={115}/>
            <RTooltip content={({active,payload}:any)=>{
              if(!active||!payload?.[0]) return null; const d=payload[0].payload
              return(<div style={{background:'#10101c',border:'1px solid rgba(212,175,55,.2)',borderRadius:8,padding:'8px 12px',fontSize:11}}>
                <b style={{color:'#fff'}}>{d.category}</b>
                <p style={{color:'rgba(255,255,255,.5)',marginTop:4}}>Count: <b style={{color:'#fff'}}>{d.count.toLocaleString()}</b></p>
                <p style={{color:'rgba(255,255,255,.5)'}}>Share: <b style={{color:C.gold}}>{d.pct}%</b></p>
                <p style={{color:'rgba(255,255,255,.5)'}}>Cumulative: <b style={{color:'rgba(255,255,255,.7)'}}>{d.cumulative_pct}%</b></p>
              </div>)
            }}/>
            <Bar dataKey="pct" name="Share %" radius={[0,4,4,0]} maxBarSize={22}>{topData.map((d:any,i:number)=><Cell key={i} fill={d.fill||SEQ[i%SEQ.length]} opacity={.85}/>)}<LabelList dataKey="pct" position="right" formatter={(v:any)=>`${v}%`} style={{fontSize:9,fill:'rgba(255,255,255,.3)'}}/></Bar>
          </BarChart>
        </ResponsiveContainer></div>
        <Insight text={`Top category: "${item.top_category}" (${item.top_pct}%). Entropy=${item.entropy} — ${item.entropy>3?'highly diverse':'low diversity, concentrated distribution'}.`}/>
      </Card>
    )
  }

  // ── Time Decomposition ────────────────────────────────────────────────────
  function renderTimeDecomp(){
    const td=a.time_decomposition||[]; if(!td.length) return <Empty msg="Need datetime column for decomposition"/>
    const item=td[tdIdx]||td[0]; if(!item) return <Empty msg="No data"/>
    const rv=rel('trend',a)
    return(
      <Card title="Trend Decomposition" sub={`${item.display_name} · Trend: ${item.trend_direction} (${item.trend_strength})`} icon={TrendingUp} col={item.trend_direction==='upward'?C.green:C.coral} relevance={rv}
        bar={td.length>1?<Sel opts={td.map((t:any)=>t.display_name)} val={item.display_name} onChange={v=>setTdIdx(td.findIndex((x:any)=>x.display_name===v))}/>:undefined}>
        <div style={{display:'flex',flexDirection:'column',gap:16}}>
          <div>
            <p style={{fontSize:11,color:'rgba(255,255,255,.4)',marginBottom:6}}>Actual + Trend Line</p>
            <div style={{height:200}}><ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={item.data||[]} margin={{top:5,right:10,bottom:5,left:0}}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false}/>
                <XAxis dataKey="period" {...AX}/><YAxis {...AX} tickFormatter={v=>nf(v,0)}/>
                <RTooltip content={<Tip/>}/><Legend wrapperStyle={{fontSize:11}}/>
                <Brush dataKey="period" height={14} stroke="rgba(255,255,255,.06)" fill="#0f0f1a" travellerWidth={4}/>
                <Area type="monotone" dataKey="actual" name="Actual" stroke={C.blue} fill={`${C.blue}20`} strokeWidth={2} dot={false}/>
                <Line type="monotone" dataKey="trend" name="Trend" stroke={item.trend_direction==='upward'?C.green:C.coral} strokeWidth={2.5} dot={false} strokeDasharray="6 3"/>
                <Line type="monotone" dataKey="moving_avg" name="Moving Avg" stroke={C.gold} strokeWidth={1.5} dot={false}/>
              </ComposedChart>
            </ResponsiveContainer></div>
          </div>
          <div>
            <p style={{fontSize:11,color:'rgba(255,255,255,.4)',marginBottom:6}}>Residuals (Actual − Trend)</p>
            <div style={{height:120}}><ResponsiveContainer width="100%" height="100%">
              <BarChart data={item.data||[]} margin={{top:5,right:10,bottom:5,left:0}}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false}/>
                <XAxis dataKey="period" {...AX}/><YAxis {...AX} tickFormatter={v=>nf(v,1)}/>
                <RTooltip content={<Tip/>}/>
                <ReferenceLine y={0} stroke="rgba(255,255,255,.2)" strokeWidth={1.5}/>
                <Bar dataKey="residual" name="Residual" radius={[2,2,0,0]} maxBarSize={20}>{(item.data||[]).map((d:any,i:number)=><Cell key={i} fill={(d.residual||0)>=0?C.green:C.coral} opacity={.7}/>)}</Bar>
              </BarChart>
            </ResponsiveContainer></div>
          </div>
        </div>
        <Insight icon={TrendingUp} color={item.trend_direction==='upward'?C.green:C.coral} text={`${item.trend_direction==='upward'?'📈':'📉'} ${item.trend_strength.charAt(0).toUpperCase()+item.trend_strength.slice(1)} ${item.trend_direction} trend (slope=${item.slope?.toFixed(4)} per period). Residuals show noise around trend.`}/>
      </Card>
    )
  }

  // ── Gauge / KPI vs Target ─────────────────────────────────────────────────
  function renderGauge(){
    const gd=a.gauge||[]; if(!gd.length) return <Empty msg="Need numeric columns"/>
    const item=gd[gIdx]||gd[0]; if(!item) return <Empty msg="No data"/>
    // Gauge rendered as a radial-style bar using a 180° arc approximation via BarChart radial
    const gaugeAngle=Math.round((item.gauge_pct||0)/100*180)
    const statusColor=item.status==='excellent'?C.green:item.status==='good'?C.teal:item.status==='warning'?C.amber:C.coral
    const allGaugeData=gd.map((g:any)=>({name:g.display_name,value:g.gauge_pct||0,pct_target:g.pct_of_target||0,status:g.status,fill:g.status==='excellent'?C.green:g.status==='good'?C.teal:g.status==='warning'?C.amber:C.coral}))
    return(
      <Card title="Gauge / KPI vs Target" sub={`${gd.length} metrics · ${item.display_name}: ${item.formatted_actual} vs target ${item.formatted_target}`} icon={Target} col={statusColor} relevance={'Strong'}
        bar={gd.length>1?<Sel opts={gd.map((g:any)=>g.display_name)} val={item.display_name} onChange={v=>setGIdx(gd.findIndex((g:any)=>g.display_name===v))}/>:undefined}>
        <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:20}}>
          {/* Single gauge */}
          <div style={{textAlign:'center'}}>
            <div style={{position:'relative',width:200,height:110,margin:'0 auto'}}>
              {/* Background arc */}
              <svg viewBox="0 0 200 110" style={{position:'absolute',inset:0}}>
                <path d="M 10 100 A 90 90 0 0 1 190 100" fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="16" strokeLinecap="round"/>
                {/* Colored fill arc */}
                <path d={`M 10 100 A 90 90 0 ${gaugeAngle>90?1:0} 1 ${10+180*Math.cos((180-gaugeAngle)*Math.PI/180)} ${100-90*Math.sin((180-gaugeAngle)*Math.PI/180)}`} fill="none" stroke={statusColor} strokeWidth="16" strokeLinecap="round"/>
                {/* Needle */}
                <line x1="100" y1="100" x2={100+80*Math.cos((180-gaugeAngle)*Math.PI/180)} y2={100-80*Math.sin((180-gaugeAngle)*Math.PI/180)} stroke={statusColor} strokeWidth="3" strokeLinecap="round"/>
                <circle cx="100" cy="100" r="6" fill={statusColor}/>
              </svg>
              <div style={{position:'absolute',bottom:0,width:'100%',textAlign:'center'}}>
                <p style={{fontSize:22,fontWeight:900,color:statusColor}}>{item.pct_of_target?.toFixed(0)}%</p>
                <p style={{fontSize:10,color:'rgba(255,255,255,.3)'}}>of target</p>
              </div>
            </div>
            <div style={{marginTop:12,display:'flex',justifyContent:'center',gap:16}}>
              {[['Actual',item.formatted_actual,statusColor],['Target',item.formatted_target,'rgba(255,255,255,.4)']].map(([l,v,c])=>(
                <div key={l as string} style={{textAlign:'center'}}><p style={{fontSize:10,color:'rgba(255,255,255,.3)'}}>{l}</p><p style={{fontSize:14,fontWeight:700,color:c as string}}>{v}</p></div>
              ))}
            </div>
            <span style={{fontSize:10,padding:'3px 10px',borderRadius:20,background:`${statusColor}18`,color:statusColor,fontWeight:700,border:`1px solid ${statusColor}30`,marginTop:8,display:'inline-block'}}>{item.status?.replace('_',' ').toUpperCase()}</span>
          </div>
          {/* All metrics overview */}
          <div style={{height:200}}><ResponsiveContainer width="100%" height="100%">
            <BarChart data={allGaugeData} layout="vertical" margin={{left:80,right:60,top:5,bottom:5}}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" horizontal={false}/>
              <XAxis type="number" domain={[0,100]} {...AX} tickFormatter={v=>`${v}%`}/>
              <YAxis type="category" dataKey="name" {...AX} width={75}/>
              <RTooltip content={<Tip/>}/>
              <ReferenceLine x={100} stroke="rgba(255,255,255,.25)" strokeDasharray="4 2" label={{value:'Target',position:'top',fill:'rgba(255,255,255,.3)',fontSize:9}}/>
              <Bar dataKey="value" name="% of Target" radius={[0,4,4,0]} maxBarSize={20}>{allGaugeData.map((d:any,i:number)=><Cell key={i} fill={d.fill} opacity={.85}/>)}<LabelList dataKey="pct_target" position="right" formatter={(v:any)=>`${v}%`} style={{fontSize:9,fill:'rgba(255,255,255,.35)'}}/></Bar>
            </BarChart>
          </ResponsiveContainer></div>
        </div>
      </Card>
    )
  }

  // ── Slope / Dumbbell Chart ────────────────────────────────────────────────
  function renderSlope(){
    const sl=a.slope_chart||[]; if(!sl.length) return <Empty msg="Need categorical + numeric columns"/>
    const item=sl[slIdx]||sl[0]; if(!item) return <Empty msg="No data"/>
    const data=item.data||[]
    return(
      <Card title="Slope / Before–After" sub={`${item.display_dimension} · ${item.period_a} vs ${item.period_b} · ${item.improvers}↗ ${item.decliners}↘`} icon={TrendingUp} col={C.teal} relevance={'Strong'}
        bar={sl.length>1?<Sel opts={sl.map((_:any,i:number)=>`${sl[i].display_dimension}×${sl[i].display_metric}`)} val={`${item.display_dimension}×${item.display_metric}`} onChange={v=>setSlIdx(sl.findIndex((_:any,i:number)=>`${sl[i].display_dimension}×${sl[i].display_metric}`===v))}/>:undefined}>
        <div style={{height:Math.max(300,data.length*40)}}><ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} layout="vertical" margin={{left:90,right:90,top:10,bottom:10}}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" horizontal={false}/>
            <XAxis type="number" {...AX} tickFormatter={v=>nf(v,0)}/>
            <YAxis type="category" dataKey="category" {...AX} width={85}/>
            <RTooltip content={({active,payload}:any)=>{
              if(!active||!payload?.[0]) return null; const d=payload[0].payload
              return(<div style={{background:'#10101c',border:'1px solid rgba(212,175,55,.2)',borderRadius:8,padding:'8px 12px',fontSize:11}}>
                <b style={{color:'#fff'}}>{d.category}</b>
                <p style={{color:'rgba(255,255,255,.5)',marginTop:4}}>{item.period_a}: <b style={{color:'rgba(255,255,255,.7)'}}>{d.formatted_a}</b></p>
                <p style={{color:'rgba(255,255,255,.5)'}}>{item.period_b}: <b style={{color:d.direction==='up'?C.green:C.coral}}>{d.formatted_b}</b></p>
                {d.change_pct!=null&&<p style={{color:d.direction==='up'?C.green:C.coral,marginTop:4,fontWeight:700}}>{d.direction==='up'?'▲':'▼'} {Math.abs(d.change_pct).toFixed(1)}%</p>}
              </div>)
            }}/>
            <Bar dataKey="period_a" name={item.period_a} fill={`${C.blue}40`} radius={[0,3,3,0]} maxBarSize={4}/>
            <Bar dataKey="period_b" name={item.period_b} fill="transparent" maxBarSize={4}/>
            {/* Dumbbell dots */}
            <Scatter dataKey="period_b" name={item.period_b} shape={(props:any)=>{
              const{cx,cy,payload}=props
              return(<g><line x1={props.cx-20} y1={props.cy} x2={props.cx+20} y2={props.cy} stroke={payload.direction==='up'?C.green:C.coral} strokeWidth={1.5} opacity={.5}/><circle cx={cx} cy={cy} r={7} fill={payload.direction==='up'?C.green:C.coral} stroke="rgba(0,0,0,.3)"/></g>)
            }}/>
          </ComposedChart>
        </ResponsiveContainer></div>
        <div style={{display:'flex',gap:16,marginTop:10,flexWrap:'wrap'}}>
          {[['Improvers ↗',item.improvers,C.green],['Decliners ↘',item.decliners,C.coral]].map(([l,v,c])=>(
            <div key={l as string} style={{display:'flex',alignItems:'center',gap:6,padding:'5px 10px',borderRadius:8,background:`${c}0d`,border:`1px solid ${c}25`}}><span style={{width:8,height:8,borderRadius:'50%',background:c}}/><span style={{fontSize:11,color:c as string,fontWeight:600}}>{l}: {v}</span></div>
          ))}
        </div>
      </Card>
    )
  }

  // ── Error Bars / Confidence Intervals ─────────────────────────────────────
  function renderErrorBars(){
    const eb=a.error_bars||[]; if(!eb.length) return <Empty msg="Need categorical + numeric columns"/>
    const item=eb[ebIdx]||eb[0]; if(!item) return <Empty msg="No data"/>
    const data=item.data||[]
    return(
      <Card title="Confidence Intervals (95% CI)" sub={`${item.display_dimension} · ${item.display_metric} · Mean ± 1.96×SEM`} icon={Activity} col={C.purple} relevance={'Strong'}
        bar={eb.length>1?<Sel opts={eb.map((_:any,i:number)=>`${eb[i].display_dimension}×${eb[i].display_metric}`)} val={`${item.display_dimension}×${item.display_metric}`} onChange={v=>setEbIdx(eb.findIndex((_:any,i:number)=>`${eb[i].display_dimension}×${eb[i].display_metric}`===v))}/>:undefined}>
        <div style={{height:Math.max(260,data.length*36)}}><ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} layout="vertical" margin={{left:100,right:40,top:10,bottom:10}}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" horizontal={false}/>
            <XAxis type="number" {...AX} tickFormatter={v=>nf(v,0)}/>
            <YAxis type="category" dataKey="category" {...AX} width={95}/>
            <RTooltip content={({active,payload}:any)=>{
              if(!active||!payload?.[0]) return null; const d=payload[0].payload
              return(<div style={{background:'#10101c',border:'1px solid rgba(212,175,55,.2)',borderRadius:8,padding:'8px 12px',fontSize:11}}>
                <b style={{color:'#fff'}}>{d.category}</b>
                <p style={{color:'rgba(255,255,255,.5)',marginTop:4}}>Mean: <b style={{color:C.gold}}>{d.formatted_mean}</b></p>
                <p style={{color:'rgba(255,255,255,.5)'}}>95% CI: [{nf(d.ci_lower)}, {nf(d.ci_upper)}]</p>
                <p style={{color:'rgba(255,255,255,.5)'}}>Std Dev: ±{nf(d.std)}</p>
                <p style={{color:'rgba(255,255,255,.35)'}}>n = {d.count}</p>
              </div>)
            }}/>
            <ReferenceLine x={item.overall_mean} stroke={`${C.amber}80`} strokeDasharray="4 2" label={{value:'Overall Avg',position:'top',fill:C.amber,fontSize:9}}/>
            {/* CI range bars */}
            <Bar dataKey="ci_lower" name="CI Lower" fill="transparent" maxBarSize={0}/>
            <Bar dataKey="ci_upper" name="CI Upper" fill="transparent" maxBarSize={0}/>
            {/* Mean dots with error bars */}
            <Scatter data={data} shape={(props:any)=>{
              const{cx,cy,payload}=props
              const xScale=props.xAxis?.scale
              if(!xScale) return<g/>
              const x1=xScale(payload.ci_lower||0), x2=xScale(payload.ci_upper||0)
              const xs1=xScale(payload.std_lower||0), xs2=xScale(payload.std_upper||0)
              return(<g>
                <rect x={xs1} y={cy-4} width={xs2-xs1} height={8} fill={`${C.purple}20`} rx={2}/>
                <rect x={x1} y={cy-7} width={x2-x1} height={14} fill={`${C.purple}12`} rx={3}/>
                <line x1={x1} y1={cy} x2={x2} y2={cy} stroke={C.purple} strokeWidth={1.5}/>
                <line x1={x1} y1={cy-5} x2={x1} y2={cy+5} stroke={C.purple} strokeWidth={1.5}/>
                <line x1={x2} y1={cy-5} x2={x2} y2={cy+5} stroke={C.purple} strokeWidth={1.5}/>
                <circle cx={cx} cy={cy} r={5} fill={C.gold} stroke="rgba(0,0,0,.3)"/>
              </g>)
            }}/>
          </ComposedChart>
        </ResponsiveContainer></div>
        <div style={{display:'flex',gap:16,marginTop:10,fontSize:11,color:'rgba(255,255,255,.3)',flexWrap:'wrap'}}>
          <span style={{display:'flex',alignItems:'center',gap:5}}><span style={{width:14,height:3,background:C.purple,opacity:.8}}/> 95% CI</span>
          <span style={{display:'flex',alignItems:'center',gap:5}}><span style={{width:14,height:7,background:`${C.purple}20`,borderRadius:2}}/> Std Dev Band</span>
          <span style={{display:'flex',alignItems:'center',gap:5}}><span style={{width:10,height:10,borderRadius:'50%',background:C.gold}}/> Mean</span>
        </div>
        <Insight text={`Shorter CI = more reliable estimate. Wide CI = small sample size. ${data[0]?.category} has highest mean (n=${data[0]?.count}).`}/>
      </Card>
    )
  }

  // ── Gantt / Timeline ──────────────────────────────────────────────────────
  function renderGantt(){
    const gn=a.gantt||[]; if(!gn.length) return <Empty msg="Need 2 date columns (start + end)"/>
    const item=gn[gnIdx]||gn[0]; if(!item) return <Empty msg="No data"/>
    const data=item.data||[]

    // Build color map for statuses
    const statusColors:Record<string,string>={}
    ;(item.statuses||[]).forEach((s:string,i:number)=>{ statusColors[s]=SEQ[i%SEQ.length] })
    statusColors['default']=C.teal

    // Compute bar widths as % of total span
    const totalDays=item.date_span_days||1

    return(
      <Card title="Gantt / Timeline" sub={`${item.display_start} → ${item.display_end} · ${item.total_tasks} tasks · avg ${item.avg_duration_days}d`} icon={TrendingUp} col={C.cyan} relevance={'Strong'}
        bar={gn.length>1?<Sel opts={gn.map((_:any,i:number)=>`${gn[i].display_start} → ${gn[i].display_end}`)} val={`${item.display_start} → ${item.display_end}`} onChange={v=>setGnIdx(gn.findIndex((_:any,i:number)=>`${gn[i].display_start} → ${gn[i].display_end}`===v))}/>:undefined}>
        {/* Timeline header */}
        <div style={{overflowX:'auto'}}>
          <div style={{minWidth:600}}>
            {/* Date axis */}
            <div style={{display:'flex',marginBottom:8,paddingLeft:160}}>
              {[0,25,50,75,100].map(pct=>(
                <div key={pct} style={{flex:'none',width:'25%',fontSize:9,color:'rgba(255,255,255,.3)',textAlign:'left'}}>
                  {pct===0?item.global_start:''}
                </div>
              ))}
            </div>
            {/* Rows */}
            <div style={{display:'flex',flexDirection:'column',gap:4}}>
              {data.map((row:any,i:number)=>{
                const col=statusColors[row.status]||C.teal
                const startPct=(row.start_day/totalDays)*100
                const widthPct=Math.max(.5,(row.duration/totalDays)*100)
                return(
                  <div key={i} style={{display:'flex',alignItems:'center',gap:8}}>
                    {/* Task label */}
                    <div style={{width:155,flexShrink:0,fontSize:11,color:'rgba(255,255,255,.55)',overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap',textAlign:'right'}} title={row.task}>{row.task}</div>
                    {/* Bar track */}
                    <div style={{flex:1,height:20,background:'rgba(255,255,255,.04)',borderRadius:4,position:'relative',overflow:'hidden'}}>
                      <div style={{
                        position:'absolute',left:`${startPct}%`,width:`${widthPct}%`,height:'100%',
                        background:col,opacity:.8,borderRadius:3,minWidth:4,
                        boxShadow:`inset 0 0 0 1px ${col}88`,
                        transition:'all .15s'
                      }}/>
                    </div>
                    {/* Duration label */}
                    <div style={{width:40,flexShrink:0,fontSize:10,color:'rgba(255,255,255,.3)',textAlign:'right'}}>{row.duration}d</div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
        {/* Legend */}
        {item.statuses?.length>0&&(
          <div style={{display:'flex',gap:12,marginTop:12,flexWrap:'wrap'}}>
            {item.statuses.map((s:string)=>(
              <div key={s} style={{display:'flex',alignItems:'center',gap:5,fontSize:11}}>
                <span style={{width:12,height:12,borderRadius:3,background:statusColors[s]||C.teal}}/>
                <span style={{color:'rgba(255,255,255,.5)'}}>{s}</span>
              </div>
            ))}
          </div>
        )}
        <Insight text={`${item.total_tasks} tasks · avg ${item.avg_duration_days} days · total span ${item.date_span_days} days`}/>
      </Card>
    )
  }

  // ── Sankey / Flow diagram ─────────────────────────────────────────────────
  function renderSankey(){
    const sk=a.sankey||[]; if(!sk.length) return <Empty msg="Need 2 categorical columns for flow"/>
    const item=sk[skIdx]||sk[0]; if(!item) return <Empty msg="No data"/>
    const nodes:any[]=item.nodes||[]
    const links:any[]=item.links||[]
    if(!nodes.length||!links.length) return <Empty msg="No flow data"/>

    // Pure SVG Sankey — layout computed in React
    const W=580, H=Math.max(280, nodes.length*30)
    const PAD=20
    const NODE_W=16, NODE_GAP=10
    const INNER_W=W-PAD*2-NODE_W*2

    // Separate sources vs targets
    const srcNodeIds=new Set(links.map((l:any)=>l.source))
    const tgtNodeIds=new Set(links.map((l:any)=>l.target))
    const srcNodes=nodes.filter((n:any)=>srcNodeIds.has(n.id))
    const tgtNodes=nodes.filter((n:any)=>tgtNodeIds.has(n.id))

    // Assign vertical positions
    const maxTotal=Math.max(...nodes.map((n:any)=>n.total||1))
    const assignY=(nodeList:any[],x:number)=>{
      let y=PAD
      return nodeList.map((n:any)=>{
        const h=Math.max(12,(n.total/maxTotal)*(H-PAD*2))
        const rect={x,y,w:NODE_W,h,col:SEQ[n.id%SEQ.length],...n}
        y+=h+NODE_GAP
        return rect
      })
    }
    const leftRects=assignY(srcNodes,PAD)
    const rightRects=assignY(tgtNodes,W-PAD-NODE_W)
    const allRects=[...leftRects,...rightRects]
    const rectById:Record<number,any>={}
    allRects.forEach(r=>rectById[r.id]=r)

    // Compute link paths (cubic bezier)
    const linkPaths=links.map((lnk:any)=>{
      const s=rectById[lnk.source], t=rectById[lnk.target]
      if(!s||!t) return null
      const thick=Math.max(2,(lnk.value/maxTotal)*(H/4))
      const sy=s.y+s.h/2, ty=t.y+t.h/2
      const mx=(s.x+s.w+t.x)/2
      return{...lnk,thick,path:`M${s.x+s.w},${sy} C${mx},${sy} ${mx},${ty} ${t.x},${ty}`,col:SEQ[lnk.source%SEQ.length]}
    }).filter(Boolean)

    return(
      <Card title="Flow / Sankey Diagram" sub={`${item.display_source} → ${item.display_target} · ${item.display_metric}`} icon={GitMerge} col={C.purple} relevance={'Strong'}
        bar={sk.length>1?<Sel opts={sk.map((_:any,i:number)=>`${sk[i].display_source}→${sk[i].display_target}`)} val={`${item.display_source}→${item.display_target}`} onChange={v=>setSkIdx(sk.findIndex((_:any,i:number)=>`${sk[i].display_source}→${sk[i].display_target}`===v))}/>:undefined}>
        <div style={{overflowX:'auto'}}>
          <svg viewBox={`0 0 ${W} ${H}`} style={{width:'100%',maxWidth:W,display:'block'}}>
            {/* Link paths */}
            {linkPaths.map((lnk:any,i:number)=>(
              <path key={i} d={lnk.path} fill="none" stroke={lnk.col} strokeWidth={lnk.thick} strokeOpacity={.35}/>
            ))}
            {/* Node rects */}
            {allRects.map((r:any)=>(
              <g key={r.id}>
                <rect x={r.x} y={r.y} width={r.w} height={r.h} rx={3} fill={r.col} opacity={.85}/>
                <text
                  x={r.x<W/2?r.x+r.w+5:r.x-5}
                  y={r.y+r.h/2+4}
                  fontSize={10} fill="rgba(255,255,255,.65)"
                  textAnchor={r.x<W/2?'start':'end'}
                >{r.name.slice(0,18)}</text>
              </g>
            ))}
          </svg>
        </div>
        <Insight text={`${item.n_sources} sources → ${item.n_targets} destinations · Total flow: ${item.total_flow!=null?item.total_flow.toLocaleString():''} ${item.display_metric}`}/>
      </Card>
    )
  }

  // ── Drill-through panel ───────────────────────────────────────────────────
  function renderDrillThrough(){
    const dt=a.drill_through||[]; if(!dt.length) return <Empty msg="Need categorical + numeric columns"/>
    const item=dt[dtIdx]||dt[0]; if(!item) return <Empty msg="No data"/>
    const detail=dtSelected&&item.detail?.[dtSelected]?item.detail[dtSelected]:null

    return(
      <Card title="Drill-Through Explorer" sub={`${item.display_dimension} · click a category to drill down`} icon={Eye} col={C.gold} relevance={'Strong'}
        bar={dt.length>1?<Sel opts={dt.map((d:any)=>d.display_dimension)} val={item.display_dimension} onChange={v=>{setDtIdx(dt.findIndex((d:any)=>d.display_dimension===v));setDtSelected(null)}}/>:undefined}>
        {/* Category pills */}
        <div style={{display:'flex',gap:6,flexWrap:'wrap',marginBottom:16}}>
          {item.categories.map((cat:string,i:number)=>(
            <button key={cat} onClick={()=>setDtSelected(dtSelected===cat?null:cat)}
              style={{padding:'5px 12px',borderRadius:20,fontSize:11,cursor:'pointer',fontWeight:dtSelected===cat?700:400,
                background:dtSelected===cat?`${SEQ[i%SEQ.length]}20`:'rgba(255,255,255,.04)',
                border:`1px solid ${dtSelected===cat?SEQ[i%SEQ.length]+'55':'rgba(255,255,255,.08)'}`,
                color:dtSelected===cat?SEQ[i%SEQ.length]:'rgba(255,255,255,.45)',transition:'all .15s'}}>
              {cat.slice(0,22)}
            </button>
          ))}
        </div>

        {!detail&&(
          <div style={{padding:'24px 0',textAlign:'center',color:'rgba(255,255,255,.25)',fontSize:12}}>
            ↑ Click a category above to see details
          </div>
        )}

        {detail&&(
          <div style={{display:'flex',flexDirection:'column',gap:12,animation:'fadeIn .2s'}}>
            {/* Header */}
            <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',padding:'10px 14px',borderRadius:10,background:'rgba(212,175,55,.06)',border:'1px solid rgba(212,175,55,.15)'}}>
              <span style={{color:C.gold,fontWeight:700,fontSize:14}}>📂 {detail.category_value}</span>
              <span style={{color:'rgba(255,255,255,.4)',fontSize:11}}>{detail.row_count.toLocaleString()} records</span>
            </div>

            {/* Metrics grid */}
            <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fill,minmax(160px,1fr))',gap:8}}>
              {(detail.metrics||[]).map((m:any,i:number)=>(
                <div key={i} style={{padding:'10px 12px',borderRadius:10,background:'rgba(255,255,255,.02)',border:`1px solid ${SEQ[i%SEQ.length]}22`}}>
                  <p style={{fontSize:10,color:'rgba(255,255,255,.3)',marginBottom:4}}>{m.display_metric}</p>
                  <p style={{fontSize:16,fontWeight:700,color:SEQ[i%SEQ.length]}}>{m.formatted_mean}</p>
                  <p style={{fontSize:10,color:'rgba(255,255,255,.25)',marginTop:2}}>total: {m.formatted_total}</p>
                </div>
              ))}
            </div>

            {/* Mini histogram */}
            {detail.histogram?.length>0&&(
              <div>
                <p style={{fontSize:11,color:'rgba(255,255,255,.3)',marginBottom:6}}>{item.display_metric} distribution</p>
                <div style={{height:60,display:'flex',alignItems:'flex-end',gap:2}}>
                  {detail.histogram.map((v:number,i:number)=>{
                    const max=Math.max(...detail.histogram)
                    const pct=max>0?(v/max)*100:0
                    return<div key={i} style={{flex:1,height:`${pct}%`,background:C.gold,opacity:.7,borderRadius:'2px 2px 0 0',minHeight:2}}/>
                  })}
                </div>
              </div>
            )}

            {/* Sub-breakdown */}
            {detail.sub_breakdown?.length>0&&(
              <div>
                <p style={{fontSize:11,color:'rgba(255,255,255,.3)',marginBottom:6}}>Breakdown by {detail.sub_display}</p>
                <div style={{display:'flex',flexDirection:'column',gap:4}}>
                  {detail.sub_breakdown.map((sb:any,i:number)=>{
                    const maxSb=Math.max(...detail.sub_breakdown.map((x:any)=>x.value||0))
                    const pct=maxSb>0?((sb.value||0)/maxSb)*100:0
                    return(
                      <div key={i} style={{display:'flex',alignItems:'center',gap:8,fontSize:11}}>
                        <span style={{width:100,color:'rgba(255,255,255,.45)',overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap',flexShrink:0}}>{sb.label}</span>
                        <div style={{flex:1,height:10,background:'rgba(255,255,255,.05)',borderRadius:5,overflow:'hidden'}}>
                          <div style={{width:`${pct}%`,height:'100%',background:SEQ[i%SEQ.length],opacity:.8,borderRadius:5}}/>
                        </div>
                        <span style={{width:60,color:'rgba(255,255,255,.5)',textAlign:'right',flexShrink:0}}>{sb.display_value}</span>
                      </div>
                    )
                  })}
                </div>
              </div>
            )}
          </div>
        )}
      </Card>
    )
  }

  // ── Marimekko / Mosaic ────────────────────────────────────────────────────
  function renderMarimekko(){
    const mm_=a.marimekko||[]; if(!mm_.length) return <Empty msg="Need 2+ categorical columns"/>
    const item=mm_[mmIdx_]||mm_[0]; if(!item) return <Empty msg="No data"/>
    const blocks=item.blocks||[]
    const dim2Cats=item.dim2_categories||[]
    // Build recharts-compatible stacked bar data per dim1
    const dim1Cats=item.dim1_categories||[]
    const chartData=dim1Cats.map((d1:string)=>{
      const d1Blocks=blocks.filter((b:any)=>b.dim1===d1)
      const entry:any={category:d1,_width:d1Blocks[0]?.width||0}
      dim2Cats.forEach((d2:string,i:number)=>{
        const b=d1Blocks.find((b:any)=>b.dim2===d2)
        entry[d2]=b?.height||0
        entry[`${d2}_value`]=b?.value||0
      })
      return entry
    })
    return(
      <Card title="Marimekko / Mosaic Chart" sub={`${item.display_dim1} × ${item.display_dim2} · ${item.display_metric}`} icon={Grid} col={C.slate} relevance={'Strong'}
        bar={mm_.length>1?<Sel opts={mm_.map((_:any,i:number)=>`${mm_[i].display_dim1}×${mm_[i].display_dim2}`)} val={`${item.display_dim1}×${item.display_dim2}`} onChange={v=>setMmIdx_(mm_.findIndex((_:any,i:number)=>`${mm_[i].display_dim1}×${mm_[i].display_dim2}`===v))}/>:undefined}>
        <div style={{height:300}}><ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{top:5,right:10,bottom:55,left:0}}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false}/>
            <XAxis dataKey="category" {...AX} tick={({x,y,payload}:any)=><text x={x} y={y+6} textAnchor="end" fontSize={9} fill="rgba(255,255,255,.35)" transform={`rotate(-30,${x},${y})`}>{String(payload.value).slice(0,14)}</text>} height={55}/>
            <YAxis {...AX} tickFormatter={v=>`${v.toFixed(0)}%`}/>
            <RTooltip content={<Tip/>}/>
            <Legend wrapperStyle={{fontSize:11}}/>
            {dim2Cats.map((d2:string,i:number)=>(
              <Bar key={d2} dataKey={d2} name={d2} stackId="a" fill={SEQ[i%SEQ.length]} opacity={.85}/>
            ))}
          </BarChart>
        </ResponsiveContainer></div>
        <Insight text={`Marimekko: X-axis bar width = share of ${item.display_dim1}. Y-axis stacking = ${item.display_dim2} composition within each ${item.display_dim1} group.`}/>
      </Card>
    )
  }

  // ── Meta ──────────────────────────────────────────────────────────────────
  function renderMeta(){
    return(
      <Card title="Dataset Intelligence" sub={`${meta.domain||'General'} · ${(meta.total_rows||0).toLocaleString()} records`} icon={Hash} col={C.blue}>
        <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fill,minmax(110px,1fr))',gap:10}}>
          {[['Rows',(meta.total_rows||0).toLocaleString(),C.gold],['Columns',String(meta.total_cols??'–'),C.teal],['Numeric',String(meta.numeric_cols?.length??'–'),C.purple],['Categorical',String(meta.categorical_cols?.length??'–'),C.amber],['Time-Aware',meta.has_datetime?'Yes ✓':'No',meta.has_datetime?C.green:'rgba(255,255,255,.3)'],['Domain',meta.domain||'General',C.blue],['Quality',meta.quality_score!=null?`${meta.quality_score}%`:'–',C.green],['Complete',meta.completeness!=null?`${meta.completeness}%`:'–',C.teal]].map(([l,v,c])=>(
            <div key={l as string} style={{padding:'10px 6px',textAlign:'center',borderRadius:10,background:'rgba(212,175,55,.04)',border:'1px solid rgba(212,175,55,.08)'}}><p style={{fontSize:9,color:'rgba(255,255,255,.25)',marginBottom:4}}>{l}</p><p style={{fontSize:14,fontWeight:700,color:c as string}}>{v}</p></div>
          ))}
        </div>
      </Card>
    )
  }

  // ── All ───────────────────────────────────────────────────────────────────
  function renderAll(){
    return(<div>
      {kpis.length>0            && renderKpis()}
      {segs.length>0            && renderSegments()}
      {(ts.length>0||gr.length>0)&&renderTrend()}
      {dists.length>0           && renderDistribution()}
      {comp.length>0            && renderComposition()}
      {sct.length>0             && renderScatter()}
      {corrPairs.length>0       && renderCorrelation()}
      {hmCols.length>=3         && renderHeatmap()}
      {vsAvgD.length>0          && renderVsAvg()}
      {tbData.length>0          && renderTopBottom()}
      {radarData.length>=3      && renderRadar()}
      {rnk.length>0             && renderRanking()}
      {out.length>0             && renderOutliers()}
      {coh.length>0             && renderCohort()}
      {mm.length>0              && renderMultiMetric()}
      {pbd.length>0             && renderPercentile()}
      {prt.length>0             && renderPareto()}
      {(a.value_at_risk||[]).length>0     && renderVaR()}
      {(a.moving_statistics||[]).length>0  && renderMovingStats()}
      {(a.concentration||[]).length>0     && renderConcentration()}
      {(a.benchmark_comparison||[]).length>0 && renderBenchmark()}
      {(a.data_quality_detail||[]).length>0  && renderQualityDetail()}
      {(a.summary_stats||[]).length>0     && renderSummaryStats()}
      {(a.frequency_analysis||[]).length>0 && renderFrequency()}
      {(a.time_decomposition||[]).length>0 && renderTimeDecomp()}
      {(a.gauge||[]).length>0              && renderGauge()}
      {(a.slope_chart||[]).length>0        && renderSlope()}
      {(a.error_bars||[]).length>0         && renderErrorBars()}
      {(a.marimekko||[]).length>0          && renderMarimekko()}
      {(a.gantt||[]).length>0               && renderGantt()}
      {(a.sankey||[]).length>0              && renderSankey()}
      {(a.drill_through||[]).length>0       && renderDrillThrough()}
      {!!meta.total_rows         && renderMeta()}
    </div>)
  }

  const R: Record<string,()=>React.ReactNode>={
    all:renderAll, kpis:renderKpis, segments:renderSegments, trend:renderTrend,
    distribution:renderDistribution, composition:renderComposition,
    scatter:renderScatter, correlation:renderCorrelation, heatmap:renderHeatmap,
    vsavg:renderVsAvg, topbottom:renderTopBottom, radar:renderRadar,
    ranking:renderRanking, outliers:renderOutliers, cohort:renderCohort,
    multi_metric:renderMultiMetric, percentile:renderPercentile, pareto:renderPareto,
    var:renderVaR, moving:renderMovingStats, concentration:renderConcentration,
    benchmark:renderBenchmark, quality:renderQualityDetail, stats_table:renderSummaryStats,
    frequency:renderFrequency, decomp:renderTimeDecomp,
    gauge:renderGauge, slope:renderSlope, errorbars:renderErrorBars, marimekko:renderMarimekko,
    gantt:renderGantt, sankey:renderSankey, drill:renderDrillThrough,
    meta:renderMeta,
  }

  // ── Render ────────────────────────────────────────────────────────────────
  return(
    <div style={{display:'flex',flexDirection:'column',gap:12}}>
      {/* Tab bar */}
      <div style={{display:'flex',gap:3,padding:4,borderRadius:12,background:'rgba(255,255,255,.03)',border:'1px solid rgba(255,255,255,.06)',overflowX:'auto'}}>
        {TABS.map((t:any)=>{
          const active=tab===t.id, rv=t.id!=='all'&&t.id!=='meta'?rel(t.id,a):undefined
          return(
            <button key={t.id} onClick={()=>setTab(t.id)} style={{display:'flex',alignItems:'center',gap:5,padding:'8px 13px',borderRadius:8,fontSize:12,fontWeight:500,whiteSpace:'nowrap',flexShrink:0,cursor:'pointer',background:active?'rgba(212,175,55,.1)':'transparent',border:active?'1px solid rgba(212,175,55,.25)':'1px solid transparent',color:active?C.gold:'rgba(255,255,255,.4)',transition:'all .15s'}}>
              <t.icon style={{width:13,height:13}}/>{t.label}
              {rv&&<span style={{fontSize:9,fontWeight:700,padding:'1px 5px',borderRadius:10,background:REL[rv as RelevanceLevel].bg,color:REL[rv as RelevanceLevel].color,border:`1px solid ${REL[rv as RelevanceLevel].border}`}}>{rv}</span>}
            </button>
          )
        })}
      </div>
      <div>{(R[tab]||renderAll)()}</div>
    </div>
  )
}
