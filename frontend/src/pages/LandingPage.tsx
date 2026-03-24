import { Link } from "react-router-dom";
import {
  Sparkles,
  BarChart3,
  TrendingUp,
  Zap,
  Shield,
  Brain,
  ArrowRight,
  CheckCircle,
  Upload,
  Activity,
  PieChart,
  LineChart,
  Database,
  Star,
  ChevronRight,
  Play,
} from "lucide-react";

const FEATURES = [
  {
    icon: Brain,
    title: "AI-Powered Analysis",
    description:
      "Automatically understands your data context, detects business domain, and generates meaningful insights without manual configuration.",
    color: "#D4AF37",
  },
  {
    icon: BarChart3,
    title: "Smart Chart Selection",
    description:
      "Intelligently picks the most impactful visualization for each dataset — bar, line, scatter, heatmap, pie, and more. No repetition, just signal.",
    color: "#00CED1",
  },
  {
    icon: TrendingUp,
    title: "Trend & Correlation Detection",
    description:
      "Discovers hidden relationships between metrics, identifies year-over-year patterns, and highlights what actually moves the needle.",
    color: "#9B59B6",
  },
  {
    icon: Zap,
    title: "Auto Summary & Labels",
    description:
      "Every chart comes with a plain-English summary, auto-generated title, axis labels, and a business insight — ready to present.",
    color: "#2ECC71",
  },
  {
    icon: Activity,
    title: "Dynamic Filtering",
    description:
      "Filter by category, time period, segment, or metric in real time. Drill down from executive overview to granular segment analysis.",
    color: "#FF6B6B",
  },
  {
    icon: Shield,
    title: "Decision-Ready Reports",
    description:
      "Generates a full HTML report with KPIs, insights, and charts — exportable for presentations and stakeholder meetings.",
    color: "#F39C12",
  },
];

const CHART_TYPES = [
  { label: "Time Series", icon: LineChart, color: "#D4AF37" },
  { label: "Segment Bar", icon: BarChart3, color: "#00CED1" },
  { label: "Distribution", icon: Activity, color: "#9B59B6" },
  { label: "Correlation Heatmap", icon: TrendingUp, color: "#2ECC71" },
  { label: "Composition Pie", icon: PieChart, color: "#FF6B6B" },
  { label: "Scatter Matrix", icon: Database, color: "#F39C12" },
  { label: "KPI Sparkline", icon: Zap, color: "#00CED1" },
  { label: "Waterfall Chart", icon: BarChart3, color: "#9B59B6" },
  { label: "Box Plot", icon: Activity, color: "#D4AF37" },
];

const STEPS = [
  {
    n: "01",
    title: "Upload CSV",
    desc: "Drop any CSV file — sales, HR, operations, marketing, finance. DataFlow handles the rest.",
    icon: Upload,
  },
  {
    n: "02",
    title: "AI Profiling",
    desc: "The engine detects domain, column types, key metrics, relationships, and data quality automatically.",
    icon: Brain,
  },
  {
    n: "03",
    title: "Visualize & Explore",
    desc: "Get animated interactive charts with auto-labels, summaries, and business insights. Filter by category or segment.",
    icon: BarChart3,
  },
];

const TESTIMONIALS = [
  {
    name: "Sarah K.",
    role: "Head of Analytics",
    quote:
      "DataFlow turned 3 days of BI work into 30 seconds. The charts are actually presentation-ready.",
  },
  {
    name: "Marcus T.",
    role: "VP Sales",
    quote:
      "I dropped in our CRM export and it immediately surfaced the pipeline segment I was missing. Incredible.",
  },
  {
    name: "Priya M.",
    role: "Data Scientist",
    quote:
      "Finally a tool that understands business context. The correlation detection alone saved us weeks of EDA.",
  },
];

function StatCounter({ value, label }: { value: string; label: string }) {
  return (
    <div className="text-center">
      <div className="text-4xl font-bold gradient-text mb-1">{value}</div>
      <div className="text-gray-400 text-sm">{label}</div>
    </div>
  );
}

export function LandingPage() {
  return (
    <div className="relative min-h-screen overflow-x-hidden">
      {/* Animated background orbs */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute top-[-20%] left-[-10%] w-[600px] h-[600px] rounded-full bg-[#D4AF37]/4 blur-[120px] animate-float-slow" />
        <div className="absolute top-[30%] right-[-15%] w-[500px] h-[500px] rounded-full bg-[#00CED1]/4 blur-[120px] animate-float-medium" />
        <div className="absolute bottom-[-10%] left-[20%] w-[400px] h-[400px] rounded-full bg-[#9B59B6]/3 blur-[100px] animate-float-fast" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_50%_0%,rgba(212,175,55,0.03)_0%,transparent_70%)]" />
      </div>

      {/* NAV */}
      <nav className="relative z-50 px-6 py-5 flex justify-between items-center max-w-7xl mx-auto">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#D4AF37] to-[#996515] flex items-center justify-center shadow-lg shadow-yellow-900/30">
            <Sparkles className="w-5 h-5 text-black" />
          </div>
          <span className="text-xl font-bold gradient-text">DataFlow</span>
        </div>
        <div className="flex items-center gap-4">
          <Link to="/login" className="nav-link">
            Sign In
          </Link>
          <Link
            to="/login"
            className="btn-gold text-sm px-5 py-2.5 inline-flex items-center gap-2"
          >
            Get Started <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </nav>

      {/* HERO */}
      <section className="relative z-10 max-w-7xl mx-auto px-6 pt-20 pb-28 text-center fade-in">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#D4AF37]/10 border border-[#D4AF37]/20 text-[#D4AF37] text-sm font-medium mb-8">
          <Star className="w-3.5 h-3.5 fill-[#D4AF37]" />
          AI-Powered Data Intelligence Platform
        </div>

        <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight tracking-tight">
          Turn Raw Data into
          <br />
          <span className="gradient-text">Actionable Insights</span>
        </h1>

        <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed">
          Upload any CSV. DataFlow automatically profiles your data, detects
          patterns, generates beautiful animated charts, and delivers
          decision-ready insights in seconds.
        </p>

        <div className="flex items-center justify-center gap-4 flex-wrap">
          <Link
            to="/login"
            className="btn-gold text-base px-8 py-4 inline-flex items-center gap-2 shadow-lg shadow-yellow-900/20"
          >
            <Play className="w-4 h-4" />
            Start Analyzing Free
          </Link>
          <a
            href="#features"
            className="btn-outline text-base px-8 py-4 inline-flex items-center gap-2"
          >
            See How It Works <ChevronRight className="w-4 h-4" />
          </a>
        </div>

        {/* Hero visual card */}
        <div className="mt-16 relative max-w-5xl mx-auto">
          <div className="glass p-6 rounded-2xl border border-white/10 shadow-2xl">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-[#D4AF37]/20 flex items-center justify-center">
                  <BarChart3 className="w-4 h-4 text-[#D4AF37]" />
                </div>
                <div className="text-left">
                  <div className="text-white font-semibold text-sm">
                    Monthly Revenue by Segment
                  </div>
                  <div className="text-gray-500 text-xs">
                    Auto-generated · 12 data points · Animated
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="badge badge-green text-xs py-1 px-2">
                  <CheckCircle className="w-3 h-3" /> AI Summary
                </span>
                <span className="badge badge-gold text-xs py-1 px-2">
                  <Sparkles className="w-3 h-3" /> Auto-labeled
                </span>
              </div>
            </div>
            {/* Mock bars animation */}
            <div className="flex items-end gap-2 h-36 px-2 pb-0">
              {[65, 88, 45, 92, 70, 55, 78, 95, 62, 80, 50, 73].map((h, i) => (
                <div
                  key={i}
                  className="flex-1 rounded-t-md relative"
                  style={{
                    height: `${h}%`,
                    background:
                      i === 7
                        ? "linear-gradient(180deg, #D4AF37 0%, #996515 100%)"
                        : i % 3 === 0
                          ? "rgba(0,206,209,0.25)"
                          : "rgba(212,175,55,0.15)",
                    border:
                      i === 7
                        ? "1px solid rgba(212,175,55,0.6)"
                        : "1px solid rgba(255,255,255,0.05)",
                    animation: `barRise 0.6s ease-out ${i * 0.06}s both`,
                    transition: "height 0.3s ease",
                  }}
                >
                  {i === 7 && (
                    <div className="absolute -top-7 left-1/2 -translate-x-1/2 text-[10px] text-[#D4AF37] font-bold whitespace-nowrap bg-[#D4AF37]/10 px-1.5 py-0.5 rounded">
                      ↑ Peak
                    </div>
                  )}
                </div>
              ))}
            </div>
            <div className="flex justify-between mt-2 px-2 text-[10px] text-gray-600">
              {[
                "Jan",
                "Feb",
                "Mar",
                "Apr",
                "May",
                "Jun",
                "Jul",
                "Aug",
                "Sep",
                "Oct",
                "Nov",
                "Dec",
              ].map((m) => (
                <span key={m}>{m}</span>
              ))}
            </div>
            {/* Auto summary box */}
            <div className="mt-4 p-3 bg-[#D4AF37]/8 border border-[#D4AF37]/15 rounded-xl text-left">
              <div className="flex items-center gap-2 mb-1">
                <Sparkles className="w-3 h-3 text-[#D4AF37]" />
                <span className="text-xs text-[#D4AF37] font-semibold">
                  AI-Generated Summary
                </span>
              </div>
              <p className="text-xs text-gray-400 leading-relaxed">
                August achieved peak revenue at 95% of target — up 22% YoY. Q3
                shows strong momentum with consistent growth. The February dip
                warrants further segment investigation.
              </p>
            </div>
          </div>
          <div className="absolute -bottom-4 left-1/2 -translate-x-1/2 w-[85%] h-8 bg-[#D4AF37]/8 blur-2xl rounded-full" />
        </div>
      </section>

      {/* STATS BAR */}
      <section className="relative z-10 border-y border-white/5 bg-white/1 py-12">
        <div className="max-w-5xl mx-auto px-6 grid grid-cols-2 md:grid-cols-4 gap-8">
          <StatCounter value="12+" label="Chart Types" />
          <StatCounter value="<30s" label="Analysis Time" />
          <StatCounter value="15+" label="Business Domains" />
          <StatCounter value="100%" label="Automated" />
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section
        id="features"
        className="relative z-10 max-w-7xl mx-auto px-6 py-24"
      >
        <div className="text-center mb-16">
          <div className="text-[#D4AF37] text-sm font-semibold uppercase tracking-widest mb-4">
            Process
          </div>
          <h2 className="text-4xl font-bold text-white mb-4">
            From CSV to Insights in 3 Steps
          </h2>
          <p className="text-gray-400 max-w-xl mx-auto">
            No SQL. No dashboarding skills. No configuration. Just upload and
            discover.
          </p>
        </div>
        <div className="grid md:grid-cols-3 gap-6">
          {STEPS.map((step) => (
            <div key={step.n} className="glass p-8 relative group card-hover">
              <div className="text-7xl font-bold text-white/4 absolute top-5 right-5 font-mono select-none">
                {step.n}
              </div>
              <div className="w-12 h-12 rounded-xl bg-[#D4AF37]/10 border border-[#D4AF37]/20 flex items-center justify-center mb-5 group-hover:bg-[#D4AF37]/20 group-hover:border-[#D4AF37]/40 transition-all duration-300">
                <step.icon className="w-6 h-6 text-[#D4AF37]" />
              </div>
              <h3 className="text-lg font-bold text-white mb-3">
                {step.title}
              </h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                {step.desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* FEATURES GRID */}
      <section className="relative z-10 max-w-7xl mx-auto px-6 pb-24">
        <div className="text-center mb-16">
          <div className="text-[#D4AF37] text-sm font-semibold uppercase tracking-widest mb-4">
            Capabilities
          </div>
          <h2 className="text-4xl font-bold text-white mb-4">
            Everything You Need for Data Intelligence
          </h2>
          <p className="text-gray-400 max-w-xl mx-auto">
            Built for analysts, designed for everyone. Every chart is
            meaningful, every insight actionable.
          </p>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
          {FEATURES.map((f) => (
            <div key={f.title} className="glass p-6 card-hover group">
              <div
                className="w-10 h-10 rounded-xl flex items-center justify-center mb-4 transition-all duration-300 group-hover:scale-110"
                style={{
                  background: `${f.color}15`,
                  border: `1px solid ${f.color}25`,
                }}
              >
                <f.icon className="w-5 h-5" style={{ color: f.color }} />
              </div>
              <h3 className="font-semibold text-white mb-2">{f.title}</h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                {f.description}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* CHART TYPES */}
      <section className="relative z-10 border-y border-white/5 bg-white/1 py-16">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-10">
            <h2 className="text-3xl font-bold text-white mb-3">
              Comprehensive Chart Library
            </h2>
            <p className="text-gray-400 max-w-lg mx-auto">
              Auto-selects the most relevant visualization for your data — never
              repetitive, always impactful.
            </p>
          </div>
          <div className="flex flex-wrap justify-center gap-3">
            {CHART_TYPES.map((ct) => (
              <div
                key={ct.label}
                className="flex items-center gap-2.5 px-4 py-2.5 rounded-xl cursor-default transition-all duration-200 hover:bg-[#D4AF37]/5"
                style={{
                  background: "rgba(255,255,255,0.02)",
                  border: "1px solid rgba(212,175,55,0.1)",
                }}
              >
                <ct.icon className="w-4 h-4" style={{ color: ct.color }} />
                <span className="text-sm text-gray-300">{ct.label}</span>
              </div>
            ))}
            <div
              className="flex items-center gap-2.5 px-4 py-2.5 rounded-xl"
              style={{ border: "1px solid rgba(255,255,255,0.04)" }}
            >
              <span className="text-sm text-gray-600">
                + Funnel, Gauge, Treemap...
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* TESTIMONIALS */}
      <section className="relative z-10 max-w-7xl mx-auto px-6 py-24">
        <div className="text-center mb-14">
          <h2 className="text-4xl font-bold text-white mb-3">
            Trusted by Analysts & Executives
          </h2>
          <p className="text-gray-400">Real insights driving real decisions.</p>
        </div>
        <div className="grid md:grid-cols-3 gap-6">
          {TESTIMONIALS.map((t) => (
            <div key={t.name} className="glass p-6 card-hover">
              <div className="flex items-center gap-1 mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star
                    key={i}
                    className="w-3.5 h-3.5 text-[#D4AF37] fill-[#D4AF37]"
                  />
                ))}
              </div>
              <p className="text-gray-300 text-sm leading-relaxed mb-5 italic">
                "{t.quote}"
              </p>
              <div className="pt-4 border-t border-white/5">
                <div className="font-semibold text-white text-sm">{t.name}</div>
                <div className="text-gray-500 text-xs mt-0.5">{t.role}</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="relative z-10 max-w-4xl mx-auto px-6 pb-24 text-center">
        <div className="glass p-12 border border-[#D4AF37]/20 relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-[#D4AF37]/5 via-transparent to-[#00CED1]/5 pointer-events-none" />
          <div className="relative">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-[#D4AF37] to-[#996515] flex items-center justify-center mx-auto mb-6 shadow-xl shadow-yellow-900/30">
              <Sparkles className="w-8 h-8 text-black" />
            </div>
            <h2 className="text-4xl font-bold text-white mb-4">
              Ready to See Your Data Clearly?
            </h2>
            <p className="text-gray-400 mb-8 max-w-lg mx-auto">
              Upload your first dataset now. No credit card required. Just drop
              a CSV and watch the magic.
            </p>
            <Link
              to="/login"
              className="btn-gold text-base px-10 py-4 inline-flex items-center gap-2 shadow-xl shadow-yellow-900/20"
            >
              <Upload className="w-4 h-4" />
              Start Free — Upload a CSV
            </Link>
            <p className="text-gray-600 text-xs mt-5">
              Demo credentials: <span className="text-[#D4AF37]">admin</span> /{" "}
              <span className="text-[#D4AF37]">admin123</span>
            </p>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="relative z-10 border-t border-white/5 py-8 text-center text-gray-600 text-sm">
        <div className="flex items-center justify-center gap-2 mb-2">
          <Sparkles className="w-4 h-4 text-[#D4AF37]" />
          <span className="gradient-text font-semibold">DataFlow</span>
        </div>
        <p>Enterprise Analytics Platform · Built for Decision Makers</p>
      </footer>

      <style>{`
        @keyframes barRise {
          from { transform: scaleY(0); transform-origin: bottom; }
          to { transform: scaleY(1); transform-origin: bottom; }
        }
        @keyframes float-slow {
          0%, 100% { transform: translateY(0px) scale(1); }
          50% { transform: translateY(-30px) scale(1.05); }
        }
        @keyframes float-medium {
          0%, 100% { transform: translateY(0px) scale(1); }
          50% { transform: translateY(-20px) scale(1.03); }
        }
        @keyframes float-fast {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-15px); }
        }
        .animate-float-slow { animation: float-slow 8s ease-in-out infinite; }
        .animate-float-medium { animation: float-medium 6s ease-in-out infinite; }
        .animate-float-fast { animation: float-fast 4s ease-in-out infinite; }
      `}</style>
    </div>
  );
}
