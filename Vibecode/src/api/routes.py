"""
DataFlow — Main API Routes
Multi-LLM pipeline:
  FAST     → Qwen/Qwen3-8B              (classification, JSON, validation)
  BALANCED → Qwen/Qwen3-Next-80B-A3B-Instruct (chart strategy, features, report)
  REASONING→ deepseek-ai/DeepSeek-R1-0528     (insights, correlations, patterns)
"""
import asyncio
import base64
import json
import logging
import uuid
from datetime import datetime
from typing import Optional

from fastapi import (
    BackgroundTasks, Depends, FastAPI, File, HTTPException, Request, UploadFile,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from sse_starlette.sse import EventSourceResponse

from src.api.auth import router as auth_router
from src.api.charts import generate_beautiful_charts
from src.api.decision_charts import generate_decision_charts
from src.api.ai_charts import generate_ai_charts
from src.api.prediction_charts import generate_prediction_charts
from src.api.comprehensive_analytics import run_comprehensive_analysis
from src.api.insights import generate_comprehensive_insights, get_skill_category
from src.api.interactive_charts import generate_interactive_analytics
from src.api.llm_charts import enrich_analytics_with_llm
from src.agents.insight_generator import InsightGenerationAgent
from src.agents.report_generator import ReportGenerationAgent
from src.agents.feature_engineer import FeatureEngineerAgent
from src.db.database import job_store
from src.services.auth import AuthService, get_auth
from src.services.redis import get_redis
from src.services.storage import get_r2_storage
from src.utils.math_utils import safe_histogram_range

logger = logging.getLogger(__name__)

# ─── App setup ────────────────────────────────────────────────────────────────
app = FastAPI(title="DataFlow — Enterprise Analytics Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(
    api_key: str = Depends(api_key_header),
    auth: AuthService = Depends(get_auth),
):
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")
    user = auth.get_user_by_api_key(api_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return user


@app.on_event("startup")
async def startup():
    redis = await get_redis()
    await redis.connect()


@app.on_event("shutdown")
async def shutdown():
    redis = await get_redis()
    await redis.disconnect()


# ─── Upload ───────────────────────────────────────────────────────────────────
@app.post("/upload")
async def upload_file(file: UploadFile = File(...), user=Depends(verify_api_key)):
    r2 = get_r2_storage()
    storage_key = f"uploads/{uuid.uuid4()}_{file.filename}"
    bytes_written, actual_path = await r2.stream_upload(file, storage_key)
    return {
        "file_path": actual_path,
        "storage_key": storage_key,
        "size_bytes": bytes_written,
        "dataset_id": file.filename.replace(".csv", ""),
    }


# ─── Pipeline trigger ─────────────────────────────────────────────────────────
@app.post("/pipeline/run")
async def run_pipeline_endpoint(
    request: Request,
    background_tasks: BackgroundTasks,
    user=Depends(verify_api_key),
):
    body = await request.json()
    file_path = body.get("file_path")
    dataset_id = body.get("dataset_id", str(uuid.uuid4()))
    user_config = body.get("user_config", {})
    job_id = str(uuid.uuid4())
    job_store.create_job(job_id, dataset_id, file_path, user_config)
    background_tasks.add_task(run_enterprise_analysis, job_id, dataset_id, file_path, user_config)
    return {"job_id": job_id, "status": "STARTED", "dataset_id": dataset_id}


# ─── Pipeline execution ───────────────────────────────────────────────────────
def run_enterprise_analysis(job_id: str, dataset_id: str, file_path: str, user_config: dict):
    """
    Multi-LLM pipeline stages:
      1  Profile        — pure Python stats
      2  Statistics     — pure Python stats
      3  Clean          — pure Python
      4  Features       — Qwen3-Next-80B: domain-aware feature engineering
      5  Charts         — matplotlib + LLM chart recommendations (async injected)
      6  Analytics      — Recharts-compatible data + LLM chart strategy
      7  Comprehensive  — extended analytics
      8  Insights       — DeepSeek-R1: deep pattern reasoning
      9  Report         — Qwen3-Next-80B: professional narrative
    """
    import asyncio
    import warnings
    import matplotlib
    import numpy as np
    import pandas as pd
    matplotlib.use("Agg")
    warnings.filterwarnings("ignore")

    def run_async(coro):
        """Run an async coroutine from a background thread safely."""
        # Always create a fresh event loop — background threads must not reuse
        # the main FastAPI event loop (which is already running).
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            try:
                loop.close()
            except Exception:
                pass

    try:
        job_store.update_job(job_id, status="RUNNING")
        df = pd.read_csv(file_path)
        data_context = analyze_data_context(df)

        # ── Stage 1: Profile ─────────────────────────────────────────────
        profile = analyze_profile(df)
        job_store.update_stage(job_id, "profile", "COMPLETE", profile)

        # ── Stage 2: Statistics ──────────────────────────────────────────
        stats = compute_statistics(df)
        job_store.update_stage(job_id, "statistics", "COMPLETE", stats)

        # ── Stage 3: Clean ───────────────────────────────────────────────
        _, clean_actions = clean_data(df)
        job_store.update_stage(job_id, "clean", "COMPLETE", {"actions": clean_actions})

        # ── Stage 4: Feature Engineering (Qwen3-Next-80B) ────────────────
        # Domain-aware feature suggestions based on detected business context
        try:
            feature_agent = FeatureEngineerAgent()
            llm_features = run_async(
                feature_agent.suggest_features(df, data_context)
            )
            feature_output = {
                "llm_suggestions": [f.model_dump() for f in llm_features],
                "count": len(llm_features),
                "model": "Qwen/Qwen3-Next-80B-A3B-Instruct",
            }
            logger.info(f"[Pipeline] Feature engineering: {len(llm_features)} suggestions")
        except Exception as e:
            import traceback; traceback.print_exc()
            feature_output = {"llm_suggestions": [], "count": 0, "error": str(e)}
        job_store.update_stage(job_id, "features", "COMPLETE", feature_output)

        # ── Stage 5: Charts (matplotlib static + prediction) ─────────────
        try:
            charts = generate_beautiful_charts(df, data_context, stats, profile)
            for generator_fn in [generate_decision_charts, generate_ai_charts]:
                if len(charts) < 5:
                    existing_titles = {c.get("title") for c in charts}
                    for c in (generator_fn(df, data_context) or []):
                        if c and c.get("image_base64") and c.get("title") not in existing_titles:
                            charts.append(c)
                            existing_titles.add(c.get("title"))
            try:
                pred_charts = generate_prediction_charts(df, data_context)
                existing_titles = {c.get("title") for c in charts}
                for c in pred_charts:
                    if c and c.get("image_base64") and c.get("title") not in existing_titles:
                        charts.append(c)
                        existing_titles.add(c.get("title"))
            except Exception:
                pass

            if not charts:
                charts = [{"type": "empty", "title": "No visualizations generated",
                           "summary": "Dataset did not produce qualifying charts."}]
        except Exception as e:
            import traceback; traceback.print_exc()
            charts = [{"type": "error", "title": "Chart generation failed", "summary": str(e)}]

        dashboard_charts = [c for c in charts if c.get("image_base64")][:6]
        job_store.update_stage(job_id, "charts", "COMPLETE",
                               {"charts": charts, "dashboard": dashboard_charts})

        # ── Stage 6: Interactive Analytics + LLM Chart Strategy ───────────
        analytics = {"success": False, "error": "not started", "llm_powered": False}
        try:
            analytics = generate_interactive_analytics(df, data_context, stats, profile)
        except Exception as e:
            import traceback; traceback.print_exc()
            logger.error(f"[Pipeline] generate_interactive_analytics failed: {e}")
            analytics = {"success": False, "error": str(e), "llm_powered": False}

        # LLM enrichment — completely optional, never allowed to crash pipeline
        try:
            analytics = run_async(
                enrich_analytics_with_llm(analytics, data_context, stats, profile)
            )
            logger.info("[Pipeline] Analytics enriched with LLM chart strategy")
        except Exception as e:
            logger.warning(f"[Pipeline] LLM chart enrichment skipped: {e}")
            if isinstance(analytics, dict):
                analytics["llm_charts"] = {"success": False, "recommendations": []}
                analytics["llm_powered"] = False

        try:
            job_store.update_stage(job_id, "analytics", "COMPLETE", analytics)
        except Exception as e:
            logger.error(f"[Pipeline] Failed to save analytics stage: {e}")
            # Try saving minimal payload
            job_store.update_stage(job_id, "analytics", "COMPLETE",
                                   {"success": False, "error": str(e)})

        # ── Stage 7: Comprehensive deep analysis ──────────────────────────
        try:
            comprehensive_data = run_comprehensive_analysis(df, data_context)
        except Exception as e:
            comprehensive_data = {"success": False, "error": str(e)}
        job_store.update_stage(job_id, "comprehensive", "COMPLETE", comprehensive_data)

        # ── Stage 8: Insights (DeepSeek-R1-0528 — reasoning tier) ─────────
        # Two-pass: main insights + correlation interpretation
        # Falls back to rule-based insights on API failure
        llm_insights = []
        try:
            # Build a minimal DataProfile for the agent
            from src.models.types import DataProfile, ColumnInfo
            col_objects = []
            for col in df.columns:
                dtype_str = "numeric" if pd.api.types.is_numeric_dtype(df[col]) else \
                            "datetime" if pd.api.types.is_datetime64_any_dtype(df[col]) else \
                            "categorical" if df[col].nunique() <= 15 else "string"
                col_objects.append(ColumnInfo(
                    name=col,
                    dtype=dtype_str,
                    unique_count=int(df[col].nunique()),
                    null_count=int(df[col].isnull().sum()),
                    sample_values=df[col].dropna().head(3).tolist(),
                ))
            # Build correlation pairs for the agent
            corr_pairs = [
                {"col_a": c["var1"], "col_b": c["var2"], "correlation": c["r"]}
                for c in stats.get("correlations", [])
            ]
            agent_profile = DataProfile(
                row_count=len(df),
                column_count=len(df.columns),
                columns=col_objects,
                file_path=file_path,
                quality_score=float(profile.get("quality_score", 100)),
                high_correlation_pairs=corr_pairs,
            )
            insight_agent = InsightGenerationAgent()
            llm_insights = run_async(
                insight_agent.generate(agent_profile, stats, data_context)
            )
            logger.info(f"[Pipeline] DeepSeek-R1 generated {len(llm_insights)} insights")
        except Exception as e:
            import traceback; traceback.print_exc()
            logger.warning(f"[Pipeline] LLM insight generation failed, falling back: {e}")

        # Merge with rule-based insights
        comprehensive = generate_comprehensive_insights(df, stats, profile, data_context)
        rule_insights = comprehensive.get("all_insights", [])

        # LLM insights take priority, rule-based fill in the gaps
        all_insight_ids = {ins.get("title", "") for ins in llm_insights}
        for ri in rule_insights:
            if ri.get("title", "") not in all_insight_ids:
                llm_insights.append(ri)

        insights = llm_insights
        skill_info = get_skill_category(data_context.get("business_domain", "General"), data_context)

        job_store.update_stage(job_id, "insights", "COMPLETE", {
            "insights": insights,
            "llm_insights_count": len([i for i in insights if i.get("category") == "data_analysis"]),
            "llm_model": "deepseek-ai/DeepSeek-R1-0528",
            "skills": skill_info,
            "by_category": comprehensive.get("by_category", {}),
            "summary": comprehensive.get("summary", {}),
        })

        # ── Stage 9: Report (Qwen3-Next-80B — business narrative) ─────────
        try:
            report_agent = ReportGenerationAgent()
            llm_narrative = run_async(
                report_agent.generate(
                    filename=dataset_id,
                    row_count=len(df),
                    stats=stats,
                    insights=insights[:8],
                    cleaning_summary={"actions": clean_actions, "total_issues": len(clean_actions)},
                    data_context=data_context,
                )
            )
            logger.info(f"[Pipeline] Qwen3-Next-80B report narrative: {len(llm_narrative)} chars")
        except Exception as e:
            logger.warning(f"[Pipeline] LLM report generation failed: {e}")
            llm_narrative = ""

        html_report = generate_styled_report(
            dataset_id, df, profile, stats, insights, charts, dashboard_charts, data_context
        )
        text_summary = llm_narrative if llm_narrative else generate_text_summary(
            profile, insights, stats, data_context
        )

        job_store.update_stage(job_id, "report", "COMPLETE", {
            "report_html": html_report,
            "report_summary": text_summary,
            "llm_narrative": llm_narrative,
            "llm_model": "Qwen/Qwen3-Next-80B-A3B-Instruct",
        })

        job_store.update_job(job_id, status="COMPLETE", total_tokens_used=0, total_cost_usd=0.0)
        logger.info(f"[Pipeline] Job {job_id} COMPLETE")

    except Exception:
        import traceback; traceback.print_exc()
        job_store.update_job(job_id, status="FAILED")


# ─── Data context analysis ────────────────────────────────────────────────────
def analyze_data_context(df) -> dict:
    import numpy as np
    import pandas as pd

    context = {
        "column_meanings": {}, "price_columns": [], "date_columns": [],
        "id_columns": [], "category_columns": [], "metric_columns": [],
        "percentage_columns": [], "count_columns": [], "ratio_columns": [],
        "score_columns": [], "time_series_columns": [], "target_columns": [],
        "friendly_names": {}, "business_domain": "General Business",
        "domain_confidence": 0, "domain_industry": None,
        "key_metrics": [], "kpis": [], "primary_key": None,
        "column_importance": {}, "patterns": [],
        "business_questions": [], "recommended_metrics": [],
        "chart_recommendations": [], "benchmarks": {}, "industry_benchmarks": {},
    }

    financial_kw = {
        "price","cost","amount","revenue","sales","profit","budget","fee","charge",
        "payment","expense","income","salary","wage","discount","valuation","value",
        "worth","total","margin","cash","capital","investment","turnover","tax",
        "gross","net","commission","bonus","allowance","deduction","ebitda",
    }
    volume_kw = {
        "count","quantity","units","items","pieces","qty","num","number","order",
        "transaction","frequency","tickets","volume","visits","sessions","views",
        "impressions","clicks","downloads","deliveries","shipments",
    }
    rate_kw = {
        "rate","percentage","pct","percent","ratio","share","contribution","margin",
        "growth","change","conversion","churn","retention","utilization","efficiency",
        "yield","return","satisfaction","engagement","occupancy","productivity",
    }
    score_kw = {
        "score","rating","grade","rank","stars","review","feedback","sentiment",
        "nps","csat","ces","performance","appraisal","health","risk","credit",
        "probability","likelihood","potential",
    }
    time_kw = {
        "date","time","year","month","day","created","updated","timestamp","period",
        "quarter","week","hour","minute","dob","birth","deadline","due","expire",
        "start","end","duration","lead_time","tenure","seniority",
    }
    id_kw = {
        "id","code","no","key","ref","reference","uuid","guid","token","user_id",
        "customer_id","order_id","transaction_id","invoice_id","product_id",
    }

    domain_signals = {
        "Retail/Ecommerce": {
            "keywords": ["product","sku","inventory","cart","checkout","shipping",
                         "discount","coupon","store","catalog","total_bill","tip","invoice"],
            "benchmarks": {"avg_order_value": 50, "conversion_rate": 3.0},
        },
        "Sales": {
            "keywords": ["customer","order","sale","deal","lead","prospect","pipeline",
                         "quota","opportunity","forecast","booking"],
            "benchmarks": {"win_rate": 20, "avg_deal_size": 10000},
        },
        "Marketing": {
            "keywords": ["campaign","impression","click","conversion","engagement",
                         "reach","cpc","cpm","roi","advertising","spend","ctr","cac","ltv"],
            "benchmarks": {"ctr": 2, "conversion_rate": 5, "roi": 300},
        },
        "HR": {
            "keywords": ["employee","staff","hire","department","manager","leave",
                         "overtime","bonus","appraisal","tenure","headcount","attrition"],
            "benchmarks": {"turnover_rate": 15, "engagement": 70},
        },
        "Finance": {
            "keywords": ["budget","expense","invoice","payment","tax","asset","liability",
                         "equity","debt","interest","dividend","ebitda","gross_margin"],
            "benchmarks": {"gross_margin": 30, "net_margin": 10},
        },
        "Operations": {
            "keywords": ["inventory","stock","warehouse","shipment","delivery","supplier",
                         "procurement","production","throughput","lead_time","fulfillment"],
            "benchmarks": {"fill_rate": 95, "on_time_delivery": 95},
        },
        "Healthcare": {
            "keywords": ["patient","diagnosis","treatment","admission","discharge",
                         "appointment","prescription","doctor","nurse","readmission"],
            "benchmarks": {"readmission_rate": 10, "bed_occupancy": 85},
        },
        "Education": {
            "keywords": ["student","grade","gpa","enrollment","attendance","course",
                         "graduation","dropout","scholarship","exam"],
            "benchmarks": {"graduation_rate": 60, "avg_gpa": 3.0},
        },
        "Customer Service": {
            "keywords": ["ticket","resolution","response_time","csat","nps","agent",
                         "support","complaint","escalation","sla","handle_time"],
            "benchmarks": {"first_response_time": 60, "csat": 85},
        },
        "Banking/Fintech": {
            "keywords": ["balance","deposit","withdrawal","transfer","transaction",
                         "credit_score","default","loan","mortgage","lending","approval"],
            "benchmarks": {"default_rate": 3, "approval_rate": 60},
        },
        "Manufacturing": {
            "keywords": ["production","output","defect","yield","cycle_time","downtime",
                         "oee","throughput","scrap","rework","utilization","maintenance"],
            "benchmarks": {"oee": 85, "yield": 95, "defect_rate": 2},
        },
    }

    def friendly(col: str) -> str:
        abbrevs = {
            "id": "ID", "qty": "Quantity", "amt": "Amount", "pct": "Percentage",
            "ytd": "Year to Date", "mtd": "Month to Date", "yoy": "Year over Year",
            "aov": "Average Order Value", "ltv": "Lifetime Value",
            "roi": "Return on Investment", "ctr": "Click Through Rate",
            "nps": "Net Promoter Score", "csat": "Customer Satisfaction",
            "avg": "Average", "num": "Number", "total_bill": "Total Bill",
        }
        col_lower = col.lower()
        for abbr, full in abbrevs.items():
            if abbr in col_lower:
                return full
        return col.replace("_", " ").replace("-", " ").title()

    def classify_col(col: str, series) -> dict:
        cl = col.lower().replace("_", " ").replace("-", " ")
        p = {
            "type": "metric", "friendly_name": friendly(col),
            "importance": 0.5, "unit": None,
            "direction": "higher_is_better", "benchmark": None,
        }
        if any(kw in cl for kw in financial_kw):
            p["type"] = "price"; p["unit"] = "$"; p["importance"] = 0.9
            if any(kw in cl for kw in ["revenue","sales","profit","income"]):
                p["importance"] = 0.95
            elif any(kw in cl for kw in ["cost","expense","loss","debt"]):
                p["importance"] = 0.85; p["direction"] = "lower_is_better"
        elif any(kw in cl for kw in volume_kw):
            p["type"] = "count"; p["unit"] = "count"; p["importance"] = 0.7
        elif any(kw in cl for kw in rate_kw) or "%" in col or "rate" in cl:
            p["type"] = "percentage"; p["unit"] = "%"; p["importance"] = 0.75
            if any(kw in cl for kw in ["churn","attrition"]):
                p["direction"] = "lower_is_better"; p["importance"] = 0.9
        elif any(kw in cl for kw in score_kw):
            p["type"] = "score"; p["importance"] = 0.75
        elif any(kw in cl for kw in time_kw):
            p["type"] = "date"; p["importance"] = 0.3
        elif any(kw in cl for kw in id_kw) or cl.endswith(" id") or cl == "id":
            p["type"] = "id"; p["importance"] = 0.05
        elif series.dtype == "object":
            n = series.nunique()
            p["type"] = "category"
            p["importance"] = 0.75 if n <= 5 else 0.6 if n <= 15 else 0.3
        elif pd.api.types.is_numeric_dtype(series):
            if series.dropna().min() >= 1 and series.dropna().max() <= 5:
                p["type"] = "score"; p["importance"] = 0.7
            else:
                p["type"] = "ratio"; p["importance"] = 0.6
        return p

    def detect_domain(columns):
        scores = {d: 0 for d in domain_signals}
        for col in columns:
            cl = col.lower().replace("_", " ")
            for d, info in domain_signals.items():
                for kw in info["keywords"]:
                    if kw in cl:
                        scores[d] += 1
        mx = max(scores.values())
        if mx > 0:
            best = max(scores, key=scores.get)
            conf = min(mx / max(len(columns) * 0.3, 1), 1.0)
            return best, conf
        return "General Business", 0.0

    def detect_patterns(df):
        patterns = []
        for col in df.select_dtypes(include=["number"]).columns:
            data = df[col].dropna()
            if len(data) < 5:
                continue
            sk = data.skew()
            if sk > 1:
                patterns.append({"type": "right_skew", "column": col,
                                  "description": f"{col} is right-skewed — most values are low with a few high outliers."})
            elif sk < -1:
                patterns.append({"type": "left_skew", "column": col,
                                  "description": f"{col} is left-skewed — most values are high with a few low outliers."})
            if len(data) > 10:
                hist, _ = np.histogram(data, range=safe_histogram_range(data), bins=10)
                peaks = np.where((hist[1:-1] > hist[:-2]) & (hist[1:-1] > hist[2:]))[0]
                if len(peaks) > 1:
                    patterns.append({"type": "bimodal", "column": col,
                                     "description": f"{col} shows bimodal distribution — data clusters in two groups."})
        return patterns

    domain, conf = detect_domain(df.columns)
    context["business_domain"] = domain
    context["domain_confidence"] = conf
    context["domain_industry"] = domain
    if domain in domain_signals:
        context["industry_benchmarks"] = domain_signals[domain].get("benchmarks", {})

    for col in df.columns:
        p = classify_col(col, df[col])
        context["friendly_names"][col] = p["friendly_name"]
        context["column_meanings"][col] = p
        context["column_importance"][col] = p["importance"]
        t = p["type"]
        if t == "price":      context["price_columns"].append(col)
        elif t == "date":     context["date_columns"].append(col)
        elif t == "id":       context["id_columns"].append(col)
        elif t == "category": context["category_columns"].append(col)
        elif t == "percentage": context["percentage_columns"].append(col)
        elif t == "count":    context["count_columns"].append(col)
        elif t == "score":    context["score_columns"].append(col)
        elif t == "ratio":    context["ratio_columns"].append(col)
        else:
            if pd.api.types.is_numeric_dtype(df[col]):
                context["metric_columns"].append(col)
        if p["importance"] > 0.7:
            context["key_metrics"].append(col)

    if not context["key_metrics"]:
        num_cols = df.select_dtypes(include=["number"]).columns.tolist()
        context["key_metrics"] = sorted(num_cols, key=lambda x: df[x].var(), reverse=True)[:3]

    for col in df.select_dtypes(include=["number"]).columns:
        if df[col].std() > 0:
            cv = abs(df[col].std() / df[col].mean() * 100) if df[col].mean() != 0 else 0
            if cv > 10:
                context["recommended_metrics"].append(col)

    if context["category_columns"]:
        context["primary_key"] = context["category_columns"][0]

    context["patterns"] = detect_patterns(df)

    questions = {
        "Retail/Ecommerce": ["What is average order value?", "Which products convert best?",
                             "What drives revenue growth?", "How do segments compare?"],
        "Sales": ["What is deal win rate?", "How long is the sales cycle?",
                  "Which territories perform best?"],
        "HR": ["What is employee turnover rate?", "Which departments have highest retention?"],
        "Finance": ["What are major expense categories?", "How is margin trending?"],
        "General Business": ["What drives performance?", "How do segments compare?",
                             "Are there data anomalies?"],
    }
    context["business_questions"] = questions.get(domain, questions["General Business"])

    recs = []
    if context["price_columns"]:     recs.append({"type": "financial_overview"})
    if context["category_columns"]:  recs.append({"type": "segment_performance"})
    if len(context["key_metrics"]) >= 2: recs.append({"type": "correlation_analysis"})
    if context["date_columns"]:      recs.append({"type": "trend_analysis"})
    context["chart_recommendations"] = recs

    return context


# ─── Helpers ──────────────────────────────────────────────────────────────────
def format_value(value: float, col: str, data_context: dict) -> str:
    if col in data_context.get("price_columns", []):
        if abs(value) >= 1_000_000: return f"${value/1_000_000:.1f}M"
        if abs(value) >= 1_000:     return f"${value/1_000:.1f}K"
        return f"${value:.2f}"
    if abs(value) >= 1_000_000: return f"{value/1_000_000:.1f}M"
    if abs(value) >= 1_000:     return f"{value/1_000:.1f}K"
    return f"{value:.2f}"


def get_friendly_name(col: str, data_context: dict) -> str:
    return data_context.get("friendly_names", {}).get(col, col.replace("_", " ").title())


# ─── Profile & stats ──────────────────────────────────────────────────────────
def analyze_profile(df) -> dict:
    total_cells = len(df) * len(df.columns)
    filled_cells = total_cells - df.isnull().sum().sum()
    null_pct = df.isnull().sum().sum() / total_cells * 100
    quality_score = max(0.0, round(100.0 - min(null_pct * 2, 30), 1))
    return {
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": list(df.columns),
        "dtypes": {col: str(dt) for col, dt in df.dtypes.items()},
        "numeric_columns": df.select_dtypes(include=["number"]).columns.tolist(),
        "categorical_columns": df.select_dtypes(include=["object"]).columns.tolist(),
        "null_counts": {col: int(df[col].isnull().sum()) for col in df.columns},
        "duplicate_rows": int(df.duplicated().sum()),
        "quality_score": quality_score,
        "completeness": round(filled_cells / total_cells * 100, 1),
        "memory_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
    }


def compute_statistics(df) -> dict:
    import numpy as np
    import pandas as pd
    stats = {"numeric": {}, "categorical": {}, "correlations": []}
    num_cols = df.select_dtypes(include=["number"]).columns.tolist()
    for col in num_cols:
        try:
            data = df[col].dropna()
            if len(data) < 2: continue
            q1, med, q3 = data.quantile([0.25, 0.5, 0.75])
            iqr = q3 - q1
            om = (data < q1 - 1.5*iqr) | (data > q3 + 1.5*iqr)
            stats["numeric"][col] = {
                "mean": round(float(data.mean()), 2),
                "median": round(float(med), 2),
                "std": round(float(data.std()), 2),
                "min": round(float(data.min()), 2),
                "max": round(float(data.max()), 2),
                "q1": round(float(q1), 2), "q3": round(float(q3), 2),
                "skewness": round(float(data.skew()), 3),
                "kurtosis": round(float(data.kurtosis()), 3),
                "cv": round(float(data.std()/data.mean()*100) if data.mean() != 0 else 0, 1),
                "range": round(float(data.max()-data.min()), 2),
                "total": round(float(data.sum()), 2),
                "outliers": int(om.sum()),
                "outlier_pct": round(om.sum()/len(data)*100, 1),
            }
        except Exception:
            continue
    for col in df.select_dtypes(include=["object"]).columns:
        data = df[col].dropna()
        if len(data) > 0:
            vc = data.value_counts()
            stats["categorical"][col] = {
                "unique": int(data.nunique()),
                "top3": {str(k): int(v) for k, v in vc.head(3).items()},
                "distribution": {str(k): round(v/len(data)*100, 1) for k, v in vc.items()},
            }
    if len(num_cols) >= 2:
        corr = df[num_cols].corr()
        for i, c1 in enumerate(num_cols):
            for c2 in num_cols[i+1:]:
                r = corr.loc[c1, c2]
                if abs(r) >= 0.5:
                    stats["correlations"].append({
                        "var1": c1, "var2": c2, "r": round(float(r), 3),
                        "strength": "Very Strong" if abs(r) >= 0.9 else "Strong" if abs(r) >= 0.7 else "Moderate",
                        "direction": "positive" if r > 0 else "negative",
                    })
    return stats


def clean_data(df) -> tuple:
    import pandas as pd
    actions = []
    cleaned = df.copy()
    for col in cleaned.columns:
        nc = cleaned[col].isnull().sum()
        if nc > 0:
            if cleaned[col].dtype in ["int64", "float64"]:
                val = cleaned[col].median()
                cleaned[col].fillna(val, inplace=True)
                actions.append(f"Filled {nc} nulls in '{col}' with median ({val:.2f})")
            else:
                val = cleaned[col].mode().iloc[0] if len(cleaned[col].mode()) > 0 else "Unknown"
                cleaned[col].fillna(val, inplace=True)
                actions.append(f"Filled {nc} nulls in '{col}' with mode ('{val}')")
    return cleaned, actions


def generate_business_insight_for_column(col: str, col_stats: dict, data_context: dict) -> str:
    fn = get_friendly_name(col, data_context)
    parts = []
    cv = col_stats.get("cv", 0)
    if cv > 50:
        parts.append(f"{fn} varies significantly — strong optimization opportunity")
    elif cv > 25:
        parts.append(f"{fn} shows moderate variation")
    else:
        parts.append(f"{fn} is stable across the dataset")
    sk = col_stats.get("skewness", 0)
    if sk > 1:
        parts.append("Most values are low with few high outliers")
    elif sk < -1:
        parts.append("Most values are high with few low outliers")
    ol = col_stats.get("outliers", 0)
    if ol > 0:
        parts.append(f"{ol} unusual values detected")
    return " | ".join(parts) if parts else "Normal distribution pattern"


# ─── Styled HTML Report ───────────────────────────────────────────────────────
def generate_styled_report(
    dataset_id: str, df, profile: dict, stats: dict,
    insights: list, charts: list, dashboard_charts: list, data_context: dict
) -> str:
    domain = data_context.get("business_domain", "General")
    generated_at = datetime.now().strftime("%B %d, %Y %H:%M")
    quality_color = "#2ECC71" if profile["quality_score"] >= 80 else "#F39C12" if profile["quality_score"] >= 60 else "#FF6B6B"

    impact_colors = {"critical": "#FF6B6B", "high": "#D4AF37", "medium": "#3498DB", "low": "#888888"}
    insight_html = ""
    for ins in insights[:10]:
        color = impact_colors.get(ins.get("impact", "low"), "#888")
        insight_html += f"""
        <div class="insight-card" style="border-left-color:{color}">
            <div class="insight-title">{ins.get('title','')}</div>
            <div class="insight-body">{ins.get('description','')}</div>
            {f'<div class="insight-action">{ins.get("action","")}</div>' if ins.get('action') else ''}
        </div>"""

    visible_charts = [c for c in charts if c.get("image_base64")]
    chart_html = ""
    for c in visible_charts[:8]:
        chart_html += f"""
        <div class="chart-card">
            <div class="chart-title">{c.get('title','Chart')}</div>
            {f'<div class="chart-sub">{c.get("subtitle","")}</div>' if c.get('subtitle') else ''}
            <img src="data:image/png;base64,{c['image_base64']}" alt="{c.get('title','')}" />
            {f'<div class="chart-summary">{c.get("summary","")}</div>' if c.get('summary') else ''}
        </div>"""

    corrs = stats.get("correlations", [])
    corr_rows = ""
    for corr in corrs[:8]:
        n1 = get_friendly_name(corr["var1"], data_context)
        n2 = get_friendly_name(corr["var2"], data_context)
        r_color = "#2ECC71" if corr["r"] > 0 else "#FF6B6B"
        corr_rows += f"""
        <tr>
            <td>{n1}</td><td>{n2}</td>
            <td style="color:{r_color};font-weight:700">{corr['r']:+.3f}</td>
            <td>{corr['strength']}</td><td>{corr['direction']}</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DataFlow Report — {dataset_id}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,'Segoe UI',system-ui,sans-serif;background:#080810;color:#e0e0e0;min-height:100vh;padding:32px 24px;background-image:radial-gradient(ellipse at 0% 0%,rgba(212,175,55,.06) 0%,transparent 60%),radial-gradient(ellipse at 100% 100%,rgba(0,206,209,.04) 0%,transparent 60%)}}
.container{{max-width:1200px;margin:0 auto}}
.report-header{{background:rgba(255,255,255,.02);border:1px solid rgba(212,175,55,.15);border-radius:20px;padding:40px;text-align:center;margin-bottom:28px}}
.logo-text{{font-size:1.4em;font-weight:800;color:#D4AF37}}
.report-title{{font-size:2em;font-weight:800;color:#fff;margin-bottom:8px}}
.report-domain{{display:inline-block;margin-bottom:10px;padding:4px 16px;border-radius:20px;background:rgba(0,206,209,.12);border:1px solid rgba(0,206,209,.25);color:#00CED1;font-size:.85em;font-weight:600}}
.report-meta{{color:rgba(255,255,255,.35);font-size:.85em}}
.kpi-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px;margin-bottom:28px}}
.kpi-card{{background:rgba(255,255,255,.025);border:1px solid rgba(212,175,55,.12);border-radius:16px;padding:24px;text-align:center}}
.kpi-value{{font-size:2.2em;font-weight:900;background:linear-gradient(135deg,#D4AF37,#F4E4BA);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.kpi-label{{color:rgba(255,255,255,.4);font-size:.8em;margin-top:4px}}
.section{{background:rgba(255,255,255,.02);border:1px solid rgba(212,175,55,.1);border-radius:20px;padding:28px;margin-bottom:24px}}
.section-title{{font-size:1.15em;font-weight:700;color:#D4AF37;margin-bottom:20px;padding-bottom:12px;border-bottom:1px solid rgba(212,175,55,.15)}}
.insight-card{{border-left:3px solid #D4AF37;background:rgba(0,0,0,.2);border-radius:10px;padding:16px;margin-bottom:12px}}
.insight-title{{font-size:.95em;font-weight:700;color:#fff;margin-bottom:6px}}
.insight-body{{color:rgba(255,255,255,.6);font-size:.88em;line-height:1.6}}
.insight-action{{margin-top:10px;padding:8px 12px;background:rgba(212,175,55,.08);border-radius:8px;color:#D4AF37;font-size:.82em}}
.charts-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(480px,1fr));gap:20px}}
.chart-card{{background:rgba(0,0,0,.2);border:1px solid rgba(212,175,55,.1);border-radius:14px;overflow:hidden}}
.chart-title{{font-weight:700;color:#fff;padding:14px 16px 0;font-size:.95em}}
.chart-card img{{width:100%;display:block;margin-top:10px}}
.chart-summary{{padding:12px 16px;font-size:.8em;color:rgba(255,255,255,.45);line-height:1.6}}
table{{width:100%;border-collapse:collapse;font-size:.88em}}
th{{color:rgba(212,175,55,.7);font-weight:600;padding:10px 12px;border-bottom:1px solid rgba(212,175,55,.12);text-align:left}}
td{{padding:10px 12px;color:rgba(255,255,255,.65);border-bottom:1px solid rgba(255,255,255,.04)}}
.footer{{text-align:center;padding:28px;color:rgba(255,255,255,.2);font-size:.8em}}
</style></head><body><div class="container">
<div class="report-header">
  <div style="display:flex;align-items:center;justify-content:center;gap:10px;margin-bottom:20px">
    <div style="width:40px;height:40px;border-radius:12px;background:linear-gradient(135deg,#D4AF37,#996515);display:flex;align-items:center;justify-content:center;font-size:20px;color:#000">✦</div>
    <span class="logo-text">DataFlow</span>
  </div>
  <h1 class="report-title">Analysis Report</h1>
  <p class="report-domain">{domain}</p>
  <p class="report-meta">Dataset: <strong style="color:rgba(255,255,255,.5)">{dataset_id}</strong> · {generated_at}</p>
</div>
<div class="kpi-grid">
  <div class="kpi-card"><div class="kpi-value">{profile["row_count"]:,}</div><div class="kpi-label">Total Records</div></div>
  <div class="kpi-card"><div class="kpi-value">{profile["column_count"]}</div><div class="kpi-label">Dimensions</div></div>
  <div class="kpi-card"><div class="kpi-value" style="color:{quality_color};-webkit-text-fill-color:{quality_color}">{profile["quality_score"]}%</div><div class="kpi-label">Data Quality</div></div>
  <div class="kpi-card"><div class="kpi-value">{profile["completeness"]}%</div><div class="kpi-label">Completeness</div></div>
  <div class="kpi-card"><div class="kpi-value">{len(visible_charts)}</div><div class="kpi-label">Charts</div></div>
</div>
<div class="section"><div class="section-title">Key Business Insights</div>{insight_html}</div>
{"" if not visible_charts else f'<div class="section"><div class="section-title">Visual Analysis</div><div class="charts-grid">{chart_html}</div></div>'}
{"" if not corrs else f'<div class="section"><div class="section-title">Metric Relationships</div><table><thead><tr><th>Metric A</th><th>Metric B</th><th>Correlation</th><th>Strength</th><th>Direction</th></tr></thead><tbody>{corr_rows}</tbody></table></div>'}
<div class="footer">Generated by <strong>DataFlow</strong> Enterprise Analytics · {generated_at}</div>
</div></body></html>"""


def generate_stylish_report(dataset_id, df, profile, stats, insights, charts, dashboard_charts, data_context):
    return generate_styled_report(dataset_id, df, profile, stats, insights, charts, dashboard_charts, data_context)


def generate_text_summary(profile: dict, insights: list, stats: dict, data_context: dict) -> str:
    """Generate HTML executive summary — rich card-based layout, no plain text."""
    domain = data_context.get("business_domain", "General Business")
    generated_at = datetime.now().strftime("%B %d, %Y %H:%M")
    quality_color = "#2ECC71" if profile['quality_score'] >= 80 else "#F39C12" if profile['quality_score'] >= 60 else "#FF6B6B"

    impact_colors = {"critical": "#FF6B6B", "high": "#D4AF37", "medium": "#3498DB", "low": "#607D8B"}
    impact_icons  = {"critical": "🔴", "high": "🟡", "medium": "🔵", "low": "⚪"}

    # Build insight cards
    insight_cards = ""
    for ins in insights[:8]:
        col   = impact_colors.get(ins.get("impact", "low"), "#607D8B")
        icon  = impact_icons.get(ins.get("impact", "low"), "⚪")
        action_html = f'<div style="margin-top:10px;padding:8px 12px;background:{col}15;border-radius:8px;color:{col};font-size:0.82em;border-left:3px solid {col}40">{ins.get("action","")}</div>' if ins.get("action") else ""
        insight_cards += f"""
        <div style="margin-bottom:12px;padding:16px;border-radius:12px;background:rgba(255,255,255,0.03);border-left:3px solid {col};border:1px solid rgba(255,255,255,0.06)">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
            <span>{icon}</span>
            <strong style="color:#fff;font-size:0.9em">{ins.get('title','')}</strong>
            <span style="font-size:0.72em;padding:2px 8px;border-radius:20px;background:{col}20;color:{col};font-weight:700;margin-left:auto">{ins.get('impact','').upper()}</span>
          </div>
          <p style="color:rgba(255,255,255,0.6);font-size:0.85em;line-height:1.6">{ins.get('description','')}</p>
          {action_html}
        </div>"""

    # Build correlation rows
    corrs = stats.get("correlations", [])
    corr_rows = ""
    for c in corrs[:5]:
        n1 = get_friendly_name(c["var1"], data_context)
        n2 = get_friendly_name(c["var2"], data_context)
        r_color = "#2ECC71" if c["r"] > 0 else "#FF6B6B"
        bar_width = int(abs(c["r"]) * 100)
        corr_rows += f"""
        <tr>
          <td style="padding:10px 12px;color:rgba(255,255,255,0.6);font-size:0.85em">{n1}</td>
          <td style="padding:10px 12px;color:rgba(255,255,255,0.6);font-size:0.85em">{n2}</td>
          <td style="padding:10px 12px">
            <div style="display:flex;align-items:center;gap:8px">
              <div style="flex:1;height:6px;background:rgba(255,255,255,0.08);border-radius:3px;overflow:hidden">
                <div style="width:{bar_width}%;height:100%;background:{r_color};border-radius:3px"></div>
              </div>
              <span style="font-weight:700;color:{r_color};font-size:0.85em;min-width:45px;text-align:right">{c['r']:+.3f}</span>
            </div>
          </td>
          <td style="padding:10px 12px;color:rgba(255,255,255,0.4);font-size:0.8em">{c['strength']}</td>
        </tr>"""

    # Key metrics
    key_metrics = data_context.get("key_metrics", [])
    metrics_html = ""
    num_stats = stats.get("numeric", {})
    for col in key_metrics[:6]:
        if col in num_stats:
            s = num_stats[col]
            fn = get_friendly_name(col, data_context)
            metrics_html += f"""
            <div style="padding:16px;border-radius:12px;background:rgba(212,175,55,0.05);border:1px solid rgba(212,175,55,0.12);text-align:center">
              <div style="font-size:0.78em;color:rgba(255,255,255,0.4);margin-bottom:6px">{fn}</div>
              <div style="font-size:1.5em;font-weight:800;color:#D4AF37">{format_value(s.get('mean',0), col, data_context)}</div>
              <div style="font-size:0.72em;color:rgba(255,255,255,0.25);margin-top:4px">avg · range {format_value(s.get('min',0),col,data_context)}–{format_value(s.get('max',0),col,data_context)}</div>
            </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box }}
  body {{ font-family: -apple-system,'Segoe UI',system-ui,sans-serif; background:#080810; color:#e0e0e0; padding:24px; }}
  .section {{ margin-bottom:24px; padding:24px; border-radius:16px; background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.06); }}
  .section-title {{ font-size:1em; font-weight:700; color:#D4AF37; margin-bottom:16px; padding-bottom:10px; border-bottom:1px solid rgba(212,175,55,0.15); }}
  table {{ width:100%; border-collapse:collapse; }}
  tr:not(:last-child) td {{ border-bottom:1px solid rgba(255,255,255,0.04); }}
  .kpi-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(130px,1fr)); gap:12px; margin-bottom:24px; }}
  .kpi-card {{ padding:20px; border-radius:12px; background:rgba(255,255,255,0.025); border:1px solid rgba(212,175,55,0.12); text-align:center; }}
  .kpi-value {{ font-size:2em; font-weight:900; }}
  .kpi-label {{ font-size:0.75em; color:rgba(255,255,255,0.4); margin-top:4px; }}
  .metrics-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(150px,1fr)); gap:12px; }}
</style></head>
<body>

<!-- Header -->
<div style="margin-bottom:24px;padding:28px;border-radius:16px;background:rgba(255,255,255,0.02);border:1px solid rgba(212,175,55,0.15);text-align:center">
  <div style="display:flex;align-items:center;justify-content:center;gap:8px;margin-bottom:12px">
    <div style="width:32px;height:32px;border-radius:8px;background:linear-gradient(135deg,#D4AF37,#996515);display:flex;align-items:center;justify-content:center;font-size:16px">✦</div>
    <span style="font-size:1.2em;font-weight:800;color:#D4AF37">DataFlow</span>
  </div>
  <h1 style="font-size:1.6em;font-weight:800;color:#fff;margin-bottom:6px">Executive Summary</h1>
  <span style="display:inline-block;padding:3px 14px;border-radius:20px;background:rgba(0,206,209,0.12);border:1px solid rgba(0,206,209,0.25);color:#00CED1;font-size:0.8em;font-weight:600">{domain}</span>
  <p style="margin-top:8px;color:rgba(255,255,255,0.3);font-size:0.8em">{generated_at}</p>
</div>

<!-- KPIs -->
<div class="kpi-grid">
  <div class="kpi-card"><div class="kpi-value" style="color:#D4AF37">{profile['row_count']:,}</div><div class="kpi-label">Records</div></div>
  <div class="kpi-card"><div class="kpi-value" style="color:#00CED1">{profile['column_count']}</div><div class="kpi-label">Dimensions</div></div>
  <div class="kpi-card"><div class="kpi-value" style="color:{quality_color}">{profile['quality_score']}%</div><div class="kpi-label">Data Quality</div></div>
  <div class="kpi-card"><div class="kpi-value" style="color:#9B59B6">{profile['completeness']}%</div><div class="kpi-label">Completeness</div></div>
  <div class="kpi-card"><div class="kpi-value" style="color:#2ECC71">{len(insights)}</div><div class="kpi-label">Insights</div></div>
  <div class="kpi-card"><div class="kpi-value" style="color:#F39C12">{len(corrs)}</div><div class="kpi-label">Correlations</div></div>
</div>

{f'<!-- Key Metrics --><div class="section"><div class="section-title">📊 Key Metrics</div><div class="metrics-grid">{metrics_html}</div></div>' if metrics_html else ''}

<!-- Insights -->
{f'<div class="section"><div class="section-title">💡 Key Business Insights</div>{insight_cards}</div>' if insight_cards else ''}

<!-- Correlations -->
{f'<div class="section"><div class="section-title">🔗 Metric Relationships</div><table><thead><tr><th style="padding:8px 12px;text-align:left;color:rgba(212,175,55,0.7);font-size:0.8em;border-bottom:1px solid rgba(212,175,55,0.12)">Metric A</th><th style="padding:8px 12px;text-align:left;color:rgba(212,175,55,0.7);font-size:0.8em;border-bottom:1px solid rgba(212,175,55,0.12)">Metric B</th><th style="padding:8px 12px;text-align:left;color:rgba(212,175,55,0.7);font-size:0.8em;border-bottom:1px solid rgba(212,175,55,0.12)">Strength</th><th style="padding:8px 12px;text-align:left;color:rgba(212,175,55,0.7);font-size:0.8em;border-bottom:1px solid rgba(212,175,55,0.12)">Type</th></tr></thead><tbody>{corr_rows}</tbody></table></div>' if corr_rows else ''}

<div style="text-align:center;padding:20px;color:rgba(255,255,255,0.2);font-size:0.75em">
  Generated by <strong style="color:rgba(212,175,55,0.4)">DataFlow</strong> Enterprise Analytics Platform · {generated_at}
</div>

</body></html>"""
    return html


# ─── Pipeline status endpoints ────────────────────────────────────────────────
@app.get("/pipeline/{job_id}/events")
async def pipeline_events(job_id: str):
    redis = await get_redis()
    async def event_gen():
        try:
            async for update in redis.stream_updates(job_id):
                yield {"event": "message", "data": json.dumps(update)}
                await asyncio.sleep(1)
        except Exception:
            pass
    return EventSourceResponse(event_gen())


@app.get("/pipeline/{job_id}/status")
async def get_pipeline_status(job_id: str, user=Depends(verify_api_key)):
    job = job_store.get_job(job_id)
    if not job:
        return {"job": {"job_id": job_id, "status": "NOT_FOUND"}, "stages": []}
    stages = job_store.get_stages(job_id)
    return {
        "job": {
            "job_id": job["job_id"],
            "dataset_id": job["dataset_id"],
            "file_path": job["file_path"],
            "status": job["status"],
            "total_tokens_used": job.get("total_tokens_used", 0),
            "total_cost_usd": job.get("total_cost_usd", 0),
            "created_at": job.get("created_at"),
        },
        "stages": stages,
    }


@app.get("/pipeline/{job_id}/analytics")
async def get_pipeline_analytics(job_id: str, user=Depends(verify_api_key)):
    job = job_store.get_job(job_id)
    if not job:
        return {"job_id": job_id, "status": "NOT_FOUND", "analytics": None}
    stages = job_store.get_stages(job_id)
    analytics_stage = next((s for s in stages if s.get("stage_name") == "analytics"), None)
    if not analytics_stage:
        return {"job_id": job_id, "status": job.get("status", "UNKNOWN"),
                "analytics": None, "message": "Analytics stage not yet available"}
    output = analytics_stage.get("output")
    if isinstance(output, str):
        try:
            output = json.loads(output)
        except Exception:
            output = {"success": False, "error": "Invalid analytics payload"}
    return {"job_id": job_id, "status": job.get("status", "UNKNOWN"), "analytics": output}


@app.get("/pipeline/all")
async def get_all_pipelines(user=Depends(verify_api_key)):
    return [
        {
            "job_id": j["job_id"],
            "dataset_id": j["dataset_id"],
            "file_path": j["file_path"],
            "status": j["status"],
            "total_tokens_used": j.get("total_tokens_used", 0),
            "total_cost_usd": j.get("total_cost_usd", 0),
            "created_at": j.get("created_at"),
        }
        for j in job_store.get_all_jobs()
    ]


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
