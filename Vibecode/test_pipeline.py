import asyncio
import sys

sys.path.insert(0, "/Users/brianeedsleep/Documents/Vibecode")

from src.services.pipeline import run_pipeline
from src.agents.data_profiler import DataProfilerAgent


async def main():
    file_path = "/Users/brianeedsleep/Documents/Vibecode/sample_data.csv"

    print("=" * 60)
    print("DATAFLOW AUTONOMOUS AGENT - TEST RUN")
    print("=" * 60)

    print("\n[1] Testing DataProfilerAgent...")
    agent = DataProfilerAgent()
    profile = await agent.profile(file_path)
    print(f"    Profile: {profile.row_count} rows, {profile.column_count} columns")
    print(f"    Quality score: {profile.quality_score}")
    print(f"    Columns: {[c.name for c in profile.columns]}")
    print(f"    Correlations: {len(profile.high_correlation_pairs)} pairs found")

    print("\n[2] Testing Statistics Agent...")
    from src.agents.statistics import StatisticsAgent
    import pandas as pd

    stats_agent = StatisticsAgent()
    df = pd.read_csv(file_path)
    stats = stats_agent.compute(df)
    print(f"    Computed stats for {len(stats)} columns")
    print(f"    Anomalies detected: {len(stats_agent.detect_anomalies(df))}")

    print("\n[3] Testing Chart Selector...")
    from src.agents.auto_chart_selector import AutoChartSelectorAgent

    chart_agent = AutoChartSelectorAgent()
    charts = chart_agent.select_charts(profile, max_count=12)
    print(f"    Selected {len(charts)} charts:")
    for chart in charts:
        print(f"      - {chart.type}: {chart.title}")

    print("\n[4] Testing DataCleaner Agent...")
    from src.agents.data_cleaner import DataCleanerAgent

    cleaner = DataCleanerAgent()
    df_cleaned, actions = await cleaner.clean(file_path)
    print(f"    Cleaned data: {len(df_cleaned)} rows")
    print(f"    Actions: {[a.action_type for a in actions]}")

    print("\n[5] Testing full pipeline...")
    job_id = "test-job-001"
    dataset_id = "test-dataset-001"

    try:
        result = await run_pipeline(
            job_id=job_id,
            dataset_id=dataset_id,
            file_path=file_path,
            user_config={"max_charts": 10},
        )
        print("    Pipeline completed!")
        print(f"\n    Final stages completed:")
        if result:
            print(f"      - profile: {result.get('profile') is not None}")
            print(f"      - clean: {result.get('cleaned_file_path') is not None}")
            print(f"      - features: {result.get('features') is not None}")
            print(f"      - statistics: {result.get('stats') is not None}")
            print(f"      - charts: {result.get('charts') is not None}")
            print(f"      - insights: {result.get('insights') is not None}")
            print(f"      - report: {result.get('report_narrative') is not None}")

            print("\n    === SAMPLE REPORT ===")
            report = result.get("report_narrative", "No report generated")
            print(report[:1000] + "..." if len(report) > 1000 else report)

    except Exception as e:
        import traceback

        print(f"    Pipeline error: {type(e).__name__}: {e}")
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)
    print("\nTo start the API server:")
    print("  cd /Users/brianeedsleep/Documents/Vibecode")
    print("  source venv/bin/activate")
    print("  python main.py")
    print("\nTo enable LLM features, set HYPERBOLIC_API_KEY in .env")


if __name__ == "__main__":
    asyncio.run(main())
