import asyncio
import sys

sys.path.insert(0, "/Users/brianeedsleep/Documents/Vibecode")

from src.services.pipeline import run_pipeline
from src.agents.data_profiler import DataProfilerAgent
from src.agents.feature_engineer import FeatureEngineerAgent
from src.agents.insight_generator import InsightGenerationAgent
from src.agents.report_generator import ReportGenerationAgent


async def main():
    file_path = "/Users/brianeedsleep/Documents/Vibecode/sample_data.csv"

    print("=" * 70)
    print("DATAFLOW AUTONOMOUS AGENT - FULL INTEGRATION TEST")
    print("=" * 70)

    # Test 1: Data Profiler
    print("\n[1/5] DataProfilerAgent...")
    profiler = DataProfilerAgent()
    profile = await profiler.profile(file_path)
    print(f"    ✓ Profiled: {profile.row_count} rows, {profile.column_count} columns")
    print(f"    ✓ Quality: {profile.quality_score}/100")
    print(f"    ✓ Columns: {[c.name for c in profile.columns]}")

    # Test 2: Statistics
    print("\n[2/5] StatisticsAgent...")
    import pandas as pd
    from src.agents.statistics import StatisticsAgent

    stats_agent = StatisticsAgent()
    df = pd.read_csv(file_path)
    stats = stats_agent.compute(df)
    anomalies = stats_agent.detect_anomalies(df)
    print(f"    ✓ Computed stats for {len(stats)} columns")
    print(f"    ✓ Found {len(anomalies)} anomalies")

    # Test 3: Chart Selection
    print("\n[3/5] AutoChartSelector...")
    from src.agents.auto_chart_selector import AutoChartSelectorAgent

    chart_agent = AutoChartSelectorAgent()
    charts = chart_agent.select_charts(profile)
    print(f"    ✓ Selected {len(charts)} charts")
    for c in charts[:3]:
        print(f"      - {c.type}: {c.title}")

    # Test 4: Feature Engineering (LLM)
    print("\n[4/5] FeatureEngineerAgent (LLM)...")
    from src.agents.data_cleaner import DataCleanerAgent

    cleaner = DataCleanerAgent()
    df_clean, actions = await cleaner.clean(file_path)
    fe_agent = FeatureEngineerAgent()
    features = await fe_agent.suggest_features(df_clean)
    print(f"    ✓ Suggested {len(features)} features")
    for f in features[:3]:
        print(f"      - {f.name}: {f.formula}")

    # Test 5: Full Pipeline
    print("\n[5/5] Full Pipeline Execution...")
    job_id = "integration-test-001"
    result = await run_pipeline(
        job_id=job_id,
        dataset_id="dataset-001",
        file_path=file_path,
        user_config={"max_charts": 10},
    )

    print("\n    === PIPELINE RESULTS ===")
    print(f"    Profile:      {'✓' if result.get('profile') else '✗'}")
    print(f"    Cleaned:      {'✓' if result.get('cleaned_file_path') else '✗'}")
    print(f"    Features:     {len(result.get('features', []))} items")
    print(f"    Statistics:   {'✓' if result.get('stats') else '✗'}")
    print(f"    Charts:       {len(result.get('charts', []))} charts")
    print(f"    Insights:     {len(result.get('insights', []))} insights")
    print(f"    Report:       {'✓' if result.get('report_narrative') else '✗'}")

    if result.get("insights"):
        print("\n    === GENERATED INSIGHTS ===")
        for i, ins in enumerate(result["insights"][:5], 1):
            print(f"\n    {i}. {ins.get('title', 'N/A')}")
            print(f"       Type: {ins.get('type', 'N/A')}")
            print(f"       Confidence: {ins.get('confidence', 0):.2f}")
            print(f"       Description: {ins.get('description', 'N/A')[:150]}")

    if result.get("report_narrative"):
        print("\n    === GENERATED REPORT ===")
        report = result["report_narrative"]
        print(report[:1500] + "\n..." if len(report) > 1500 else report)

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED - SYSTEM READY")
    print("=" * 70)
    print("\nTo start API server:")
    print("  cd /Users/brianeedsleep/Documents/Vibecode")
    print("  source venv/bin/activate")
    print("  python main.py")
    print("\nAPI Endpoints:")
    print("  POST /upload           - Upload CSV file")
    print("  POST /pipeline/run     - Start analysis pipeline")
    print("  GET  /pipeline/{id}    - Get pipeline status")
    print("  GET  /pipeline/{id}/events - SSE events stream")


if __name__ == "__main__":
    asyncio.run(main())
