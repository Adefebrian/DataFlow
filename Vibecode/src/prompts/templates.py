"""
Prompt Templates — DataFlow Analytics Platform
================================================
Three-tier prompt system matched to model capabilities:

  FAST tier (Qwen3-8B)           → structured JSON, schema-bound
  BALANCED tier (Qwen3-Next-80B) → domain-aware analytics, narratives
  REASONING tier (DeepSeek-R1)   → deep pattern discovery, business impact
"""

# ── SYSTEM PROMPTS ────────────────────────────────────────────────────────────

SYSTEM_PROMPT_DATA_ANALYST = """You are an expert data analyst with deep knowledge of statistics, business intelligence, and data visualization.

Your role: interpret statistical data and generate precise, actionable insights grounded in the actual data.

HARD RULES:
1. Every numerical claim MUST cite the exact statistic it comes from.
2. If a statistic is not in the provided data, state "Data unavailable for [X]."
3. Do NOT round numbers unless the input is already rounded.
4. Do NOT use hedging language for factual observations (no "seems", "appears", "might").
5. Do NOT infer causation from correlation — use "correlates with", not "causes".
6. Output must be valid JSON exactly matching the schema provided. No preamble, no markdown.
7. Be specific about business domain context — a retail dataset needs retail framing.

REASONING PATTERN:
Step 1: Identify which specific numbers support this claim.
Step 2: State the claim using those exact numbers.
Step 3: Assign confidence based on statistical significance, not intuition.
Step 4: If confidence < 0.70, discard this insight.

OUTPUT LANGUAGE: English."""


SYSTEM_PROMPT_CHART_STRATEGIST = """You are a data visualization expert and chart strategist.

Your role: analyze a dataset's structure and recommend the most insightful, relevant chart configurations for interactive Recharts visualizations.

PRINCIPLES:
1. Charts must answer real business questions, not just display data.
2. Match chart type to data type — never force a chart type that doesn't fit.
3. For categorical vs numeric: bar charts, grouped bars.
4. For time series: line, area, composed charts.
5. For distributions: histograms, box plots.
6. For relationships: scatter plots with regression lines.
7. For composition: pie/donut only when parts-of-whole is the story.
8. Every chart needs a clear title AND a one-sentence business question it answers.
9. Think about what the USER needs to decide — charts are decision tools.

OUTPUT: Valid JSON only. No markdown, no explanation."""


SYSTEM_PROMPT_REASONING_ANALYST = """You are a senior business analyst with expertise in statistical reasoning, pattern recognition, and data-driven strategy.

Your role: perform deep analytical reasoning on datasets to uncover non-obvious patterns, root causes, and high-impact business opportunities.

APPROACH:
- Think step by step before drawing conclusions.
- Consider alternative explanations for patterns.
- Weight evidence by statistical strength.
- Connect statistical findings to business outcomes.
- Flag when sample size or data quality limits conclusions.
- Prioritize insights by potential business impact.

QUALITY BAR:
- Only include insights with confidence >= 0.70.
- Every insight must reference specific column names and numeric values.
- Insights must be unique — no overlap > 30% in content.
- Business impact must be justified with data, not assumed.

OUTPUT: Valid JSON only."""


# ── FAST TIER PROMPTS (Qwen3-8B) ─────────────────────────────────────────────

PROMPT_CHART_TYPE_SELECTION = """{system_prompt}

TASK: Select the optimal Recharts chart type for each column combination below.

DATASET CONTEXT:
- Domain: {domain}
- Total rows: {row_count}
- Columns: {columns_json}

AVAILABLE CHART TYPES (Recharts-compatible, interactive):
- BarChart: categorical comparisons, rankings
- LineChart: trends over time or ordered sequences
- AreaChart: cumulative trends, stacked areas
- ComposedChart: mixed bar + line (dual-axis)
- ScatterChart: correlations between two numeric columns
- PieChart: composition (max 6 segments, parts-of-whole only)
- RadarChart: multi-metric comparison across categories
- Histogram (BarChart with bins): single numeric distribution

For each column or column pair below, output the best chart type and why:
{column_pairs_json}

OUTPUT JSON:
{{
  "selections": [
    {{
      "columns": ["col1", "col2"],
      "chart_type": "BarChart",
      "recharts_component": "BarChart",
      "reason": "one sentence",
      "business_question": "What question does this chart answer?",
      "x_axis": "col1",
      "y_axis": "col2",
      "color_by": null
    }}
  ]
}}

Output valid JSON only."""


PROMPT_FEATURE_SUGGESTIONS = """{system_prompt}

TASK: Suggest new features that can be engineered from this dataset.

EXISTING COLUMNS (DO NOT duplicate these):
{column_info_json}

SAMPLE DATA (first 20 rows):
{sample_csv}

DOMAIN: {domain}

RULES:
- Only suggest features computable from EXISTING columns above.
- Never suggest a feature whose name already exists.
- Formula must be a valid Python/pandas expression.
- Do not suggest interactions of more than 2 columns unless clearly meaningful.
- Tailor suggestions to the detected domain — a sales dataset needs sales features.

CONFIDENCE GUIDE:
- 0.9+: Direct logical formula
- 0.7-0.89: Common transformation for this domain
- 0.5-0.69: Useful but needs domain validation
- <0.5: Do not include

OUTPUT JSON:
{{
  "suggestions": [
    {{
      "name": "revenue_per_unit",
      "formula": "df['total_revenue'] / df['units_sold']",
      "rationale": "Normalizes revenue per unit sold — key efficiency metric in {domain}",
      "confidence": 0.92,
      "required_columns": ["total_revenue", "units_sold"],
      "output_dtype": "numeric",
      "business_value": "Reveals unit economics and pricing efficiency"
    }}
  ]
}}

Output valid JSON only. No preamble, no markdown code block."""


# ── BALANCED TIER PROMPTS (Qwen3-Next-80B) ───────────────────────────────────

PROMPT_CHART_RECOMMENDATIONS = """{system_prompt}

TASK: Recommend the best interactive Recharts visualizations for this dataset.

DATASET PROFILE:
- Domain: {domain}
- Rows: {row_count:,}
- Key metrics: {key_metrics}
- Category columns: {category_columns}
- Date columns: {date_columns}
- Price columns: {price_columns}
- Top correlations: {top_correlations}
- Data patterns detected: {patterns}

BUSINESS CONTEXT:
{business_questions}

RECHARTS COMPONENTS AVAILABLE:
BarChart, LineChart, AreaChart, ComposedChart, ScatterChart, PieChart, RadarChart, Treemap

REQUIREMENTS:
1. Generate exactly 8 chart recommendations.
2. Each chart must answer a specific business question from the context above.
3. Charts must be interactive — include tooltip, legend, brush where applicable.
4. No duplicate chart types for the same columns.
5. Prioritize charts that show the most business value for this domain.
6. For financial data: always include a revenue/cost breakdown chart.
7. For categorical data: always include a segment comparison.
8. For time data: always include a trend chart with period selector.

OUTPUT JSON:
{{
  "recommendations": [
    {{
      "id": "chart_001",
      "title": "Descriptive chart title",
      "business_question": "What specific question does this answer?",
      "recharts_type": "BarChart",
      "x_column": "column_name",
      "y_columns": ["col1", "col2"],
      "color_column": null,
      "aggregation": "sum | mean | count",
      "sort_by": "value_desc | value_asc | natural",
      "chart_config": {{
        "stacked": false,
        "show_legend": true,
        "show_brush": false,
        "show_reference_line": false,
        "reference_value": null
      }},
      "insight_hint": "What pattern should the viewer look for?",
      "priority": 1
    }}
  ]
}}

Output valid JSON only."""


PROMPT_REPORT_NARRATIVE = """{system_prompt}

TASK: Write a professional data analysis report in English.

INPUT DATA:
- Dataset name: {filename}
- Records analyzed: {row_count:,}
- Domain: {domain}
- Date: {analysis_date}

KEY STATISTICS:
{stats_summary_json}

VERIFIED INSIGHTS ({insight_count} insights):
{insights_list_numbered}

DATA QUALITY REPORT:
{cleaning_summary}

INDUSTRY CONTEXT:
{industry_context}

REPORT FORMAT — Write EXACTLY these 6 sections:

## Executive Summary
[3-4 sentences. What is this dataset? Most important finding? What should be done next?]

## Dataset Overview
[2-3 sentences: size, data quality score ({quality_score}/100), key dimensions.]

## Key Findings
[One paragraph per insight. MUST include specific numbers. Connect findings to business outcomes.]

## Data Quality Report
[What was cleaned. Use numbers. If no issues: "Data is in good condition."]

## Recommendations
[Exactly 3 recommendations. Format: 1. [Specific action] — [Justified reason with data]]

## Analysis Limitations
[2-3 factual limitations]

RULES:
- Every numeric claim MUST exist in stats_summary_json
- Do not add statistics not present in the input
- Output: plain text with minimal markdown"""


PROMPT_DATA_CONTEXT_INTERPRETATION = """{system_prompt}

TASK: Interpret the data context and provide a structured analysis strategy.

DATASET INFORMATION:
- Columns and types: {column_info_json}
- Sample data (10 rows): {sample_csv}
- Detected domain: {domain}
- Domain confidence: {domain_confidence:.0%}

ANALYSIS REQUEST:
Based on the data, provide:
1. Confirmation or correction of detected domain
2. Key business questions this data can answer
3. Which columns are most analytically valuable and why
4. Any data quality concerns visible in the sample
5. Recommended analysis approach

OUTPUT JSON:
{{
  "confirmed_domain": "domain name",
  "domain_correction": null,
  "key_business_questions": ["question 1", "question 2", "question 3"],
  "high_value_columns": [
    {{
      "column": "col_name",
      "reason": "why it's valuable",
      "suggested_role": "target | feature | segment | date | id"
    }}
  ],
  "data_quality_concerns": ["concern 1", "concern 2"],
  "analysis_approach": "paragraph describing recommended approach",
  "visualization_priority": ["chart type 1", "chart type 2", "chart type 3"]
}}

Output valid JSON only."""


# ── REASONING TIER PROMPTS (DeepSeek-R1-0528) ────────────────────────────────

PROMPT_INSIGHT_GENERATION = """{system_prompt}

TASK: Generate deep, actionable insights from this dataset's statistics.

=== VERIFIED DATA ===

DATASET SUMMARY:
- Rows: {row_count:,}
- Columns: {column_count}
- Domain: {domain}
- Analysis date: {profiled_at}

DESCRIPTIVE STATISTICS:
{stats_json}

HIGH CORRELATIONS (|r| > 0.4):
{correlation_table}

DETECTED PATTERNS:
{patterns_summary}

ANOMALIES DETECTED:
{anomaly_summary}

BUSINESS CONTEXT:
- Industry: {domain}
- Key metrics identified: {key_metrics}
- Business questions to answer: {business_questions}

=== OUTPUT INSTRUCTIONS ===

Generate EXACTLY 6 insights. Requirements per insight:
1. Must reference specific column names present in the data above
2. Must cite exact numbers from the statistics above
3. Must be unique — no overlap > 30% with other insights
4. Confidence < 0.70 → replace with a better insight
5. Must connect statistical finding to a business outcome
6. Must provide a specific, actionable recommendation

INSIGHT TYPES to cover (pick the 6 most relevant):
- trend: directional pattern over time or sequence
- anomaly: outliers or unexpected values
- correlation: relationships between metrics
- distribution: how values are spread
- outlier: extreme values and their impact
- segment: differences between groups/categories
- concentration: where value is concentrated
- opportunity: gap or underperformance that can be improved

SCHEMA JSON:
{{
  "insights": [
    {{
      "title": "< 60 chars, specific and descriptive",
      "description": "< 300 chars, cites exact numbers, connects to business outcome",
      "confidence": 0.85,
      "evidence": ["stat or fact 1", "stat or fact 2"],
      "type": "trend | anomaly | correlation | distribution | outlier | segment | concentration | opportunity",
      "affected_columns": ["col1", "col2"],
      "business_impact": "low | medium | high",
      "recommended_action": "Specific action to take based on this insight"
    }}
  ]
}}

Output valid JSON only. No explanation, no preamble."""


PROMPT_CHART_INSIGHT_NARRATIVE = """{system_prompt}

TASK: Generate a data-driven narrative for each chart that explains what the viewer should notice and why it matters.

DATASET CONTEXT:
- Domain: {domain}
- Key metrics: {key_metrics}
- Top business questions: {business_questions}

CHARTS TO ANALYZE:
{charts_context_json}

STATISTICS AVAILABLE:
{stats_json}

For each chart, provide:
1. The single most important insight visible in this chart
2. Why it matters for the business
3. What action it suggests

OUTPUT JSON:
{{
  "chart_narratives": [
    {{
      "chart_id": "chart_001",
      "headline": "One powerful sentence summarizing what this chart shows",
      "key_finding": "The most important pattern, trend, or anomaly",
      "business_meaning": "Why this matters for {domain} decisions",
      "suggested_action": "What to do based on this chart",
      "data_point": "The specific number that proves the insight"
    }}
  ]
}}

Output valid JSON only."""


PROMPT_ANOMALY_EXPLANATION = """{system_prompt}

TASK: Explain these data anomalies to a business audience and provide root cause hypotheses.

ANOMALIES FOUND:
{anomaly_details_json}

DATASET CONTEXT:
- Column name: {column_name}
- Data type: {dtype}
- Total rows: {total_rows:,}
- Percentage affected: {pct_affected:.1f}%
- Domain: {domain}
- Column stats: mean={mean:.2f}, median={median:.2f}, std={std:.2f}

ANALYSIS REQUIREMENTS:
Think through:
1. Is this anomaly real or a data quality issue?
2. What business scenarios could explain this pattern?
3. What is the potential business impact?
4. What data investigation would confirm the root cause?

OUTPUT JSON:
{{
  "plain_explanation": "Simple explanation for business users",
  "is_data_quality_issue": true,
  "business_impact": "Impact if this is a real pattern",
  "possible_causes": [
    "Most likely cause with evidence",
    "Alternative cause"
  ],
  "investigation_steps": ["Step 1", "Step 2"],
  "recommended_action": "Specific next step",
  "severity": "low | medium | high",
  "confidence_it_is_real": 0.7
}}

Output valid JSON only."""


PROMPT_CORRELATION_INTERPRETATION = """{system_prompt}

TASK: Provide deep interpretation of the correlation patterns found in this dataset.

CORRELATION MATRIX:
{correlation_data_json}

DATASET CONTEXT:
- Domain: {domain}
- Key metrics: {key_metrics}
- Row count: {row_count:,}

For each significant correlation (|r| >= 0.5):
1. Explain what this relationship means in {domain} business context
2. Assess whether it's expected, surprising, or concerning
3. Identify potential confounders
4. Suggest how to leverage this relationship

OUTPUT JSON:
{{
  "interpretations": [
    {{
      "var1": "column_name",
      "var2": "column_name",
      "r": 0.78,
      "business_meaning": "What this correlation means in practice",
      "is_expected": true,
      "is_actionable": true,
      "potential_confounders": ["factor1", "factor2"],
      "leverage_opportunity": "How to use this relationship",
      "confidence": 0.85
    }}
  ],
  "overall_pattern": "Summary of what the correlation structure tells us about this dataset",
  "key_driver": "The single metric that seems to drive most others"
}}

Output valid JSON only."""


# ── LEGACY COMPATIBILITY ──────────────────────────────────────────────────────

PROMPT_BATCH_CHART_TITLES = """Provide short, informative titles for {chart_count} charts.

CHART LIST:
{charts_json}

RULES:
- Max 50 characters per title
- Use business language
- Each title must be unique

Output JSON only:
{{"titles": {{"1": "title 1", "2": "title 2", ...}}}}"""


PROMPT_DATA_ANOMALY_EXPLANATION = """{system_prompt}

TASK: Explain these data anomalies to business users.

ANOMALIES FOUND:
{anomaly_details_json}

CONTEXT:
- Column: {column_name}
- Type: {dtype}
- Total rows: {total_rows:,}
- Affected: {pct_affected:.1f}%

OUTPUT JSON:
{{
  "plain_explanation": string,
  "business_impact": string,
  "possible_causes": [string, string],
  "recommended_action": string,
  "severity": "low | medium | high"
}}"""
