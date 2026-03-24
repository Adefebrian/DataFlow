"""
AI-Powered Data Understanding Module
====================================

Uses OpenAI API for intelligent data analysis and chart selection
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
import json
import os

# OpenAI API configuration
OPENAI_API_KEY = "sk-f616wEWWXQftbJmE5UWc3EcRx29UcIPR08LrRcvLxhgD8k5I572dkAmhBtQwtEdA"
OPENAI_BASE_URL = "https://api.openai.com/v1"


def call_openai_api(
    prompt: str, system_prompt: str = "", max_tokens: int = 2000
) -> str:
    """Call OpenAI API for data analysis"""
    try:
        import requests

        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": "gpt-4o-mini",
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.3,
        }

        response = requests.post(
            f"{OPENAI_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            print(f"API Error: {response.status_code} - {response.text}")
            return ""
    except Exception as e:
        print(f"API call failed: {e}")
        return ""


class AIDataAnalyzer:
    """
    AI-Powered Data Analyzer
    Uses GPT to understand data and recommend visualizations
    """

    def __init__(self, df: pd.DataFrame, data_context: Dict = None):
        self.df = df.copy()
        self.data_context = data_context or {}
        self.ai_insights = {}
        self.recommended_charts = []
        self.column_analysis = {}

    def analyze_with_ai(self) -> Dict:
        """Run AI-powered analysis"""
        # Step 1: Analyze data structure
        data_summary = self._create_data_summary()

        # Step 2: Get AI insights on data
        self.ai_insights = self._get_ai_insights(data_summary)

        # Step 3: Get recommended charts from AI
        self.recommended_charts = self._get_ai_chart_recommendations(data_summary)

        # Step 4: Get column-level analysis
        self.column_analysis = self._get_ai_column_analysis(data_summary)

        return {
            "success": True,
            "ai_insights": self.ai_insights,
            "recommended_charts": self.recommended_charts,
            "column_analysis": self.column_analysis,
            "data_summary": data_summary,
        }

    def _create_data_summary(self) -> Dict:
        """Create a summary of the data for AI analysis"""
        summary = {
            "row_count": len(self.df),
            "column_count": len(self.df.columns),
            "columns": [],
        }

        for col in self.df.columns:
            dtype = str(self.df[col].dtype)
            unique_count = self.df[col].nunique()
            null_count = int(self.df[col].isnull().sum())
            null_pct = null_count / len(self.df) * 100

            col_info = {
                "name": col,
                "dtype": dtype,
                "unique_count": unique_count,
                "null_count": null_count,
                "null_pct": round(null_pct, 2),
                "sample_values": self.df[col].dropna().head(5).tolist(),
            }

            # Add numeric stats if applicable
            if any(x in dtype for x in ["int", "float", "number"]):
                try:
                    data = pd.to_numeric(self.df[col], errors="coerce").dropna()
                    if len(data) > 0:
                        col_info["stats"] = {
                            "mean": round(float(data.mean()), 2),
                            "median": round(float(data.median()), 2),
                            "std": round(float(data.std()), 2),
                            "min": round(float(data.min()), 2),
                            "max": round(float(data.max()), 2),
                            "skewness": round(float(data.skew()), 2),
                        }
                except:
                    pass

            summary["columns"].append(col_info)

        return summary

    def _get_ai_insights(self, data_summary: Dict) -> Dict:
        """Get AI insights about the data"""
        system_prompt = """You are a Senior Data Analyst with 30 years of experience. 
        Analyze the data and provide actionable business insights.
        Return your analysis as JSON with the following structure:
        {
            "business_domain": "detected domain",
            "key_metrics": ["list of important metrics"],
            "data_quality_assessment": "assessment text",
            "top_3_findings": ["finding1", "finding2", "finding3"],
            "recommendations": ["rec1", "rec2", "rec3"],
            "anomalies_detected": ["anomaly1", "anomaly2"],
            "trends_detected": ["trend1", "trend2"]
        }"""

        prompt = f"""Analyze this dataset and provide business insights:

Data Summary:
{json.dumps(data_summary, indent=2, default=str)}

Please provide:
1. Business domain detection
2. Key metrics identification
3. Data quality assessment
4. Top 3 findings
5. Actionable recommendations
6. Any anomalies or unusual patterns
7. Detected trends

Return as JSON only, no markdown."""

        response = call_openai_api(prompt, system_prompt)

        try:
            # Try to extract JSON from response
            if "{" in response and "}" in response:
                json_str = response[response.find("{") : response.rfind("}") + 1]
                return json.loads(json_str)
        except:
            pass

        return {
            "business_domain": "General Business",
            "key_metrics": [],
            "data_quality_assessment": "Analysis pending",
            "top_3_findings": [],
            "recommendations": [],
            "anomalies_detected": [],
            "trends_detected": [],
        }

    def _get_ai_chart_recommendations(self, data_summary: Dict) -> List[Dict]:
        """Get AI-recommended charts based on data"""
        system_prompt = """You are a Data Visualization Expert.
        Recommend the best charts for this data based on column types and relationships.
        Return as JSON array with this structure:
        [
            {
                "chart_type": "chart type name",
                "columns": ["col1", "col2"],
                "title": "chart title",
                "purpose": "what insight this chart provides",
                "priority": 1-10
            }
        ]"""

        prompt = f"""Based on this data, recommend the best visualizations:

Data Summary:
{json.dumps(data_summary, indent=2, default=str)}

Recommend 8-10 diverse charts that would provide the most valuable insights.
Consider:
- Time series charts if date columns exist
- Correlation charts for numeric columns
- Distribution charts for understanding data spread
- Ranking charts for categorical vs numeric
- Composition charts for segment breakdown

Return as JSON array only, no markdown."""

        response = call_openai_api(prompt, system_prompt)

        try:
            if "[" in response and "]" in response:
                json_str = response[response.find("[") : response.rfind("]") + 1]
                charts = json.loads(json_str)
                return sorted(charts, key=lambda x: x.get("priority", 5), reverse=True)
        except:
            pass

        return []

    def _get_ai_column_analysis(self, data_summary: Dict) -> Dict:
        """Get AI analysis of each column"""
        system_prompt = """You are a Data Quality Expert.
        Analyze each column and provide insights about data types, quality, and relationships.
        Return as JSON with column names as keys."""

        prompt = f"""Analyze each column in this dataset:

Data Summary:
{json.dumps(data_summary, indent=2, default=str)}

For each column, provide:
1. Semantic type (e.g., "currency", "age", "category", "identifier", "date")
2. Data quality issues
3. Suggested transformations
4. Relationships with other columns
5. Business meaning

Return as JSON object with column names as keys."""

        response = call_openai_api(prompt, system_prompt)

        try:
            if "{" in response and "}" in response:
                json_str = response[response.find("{") : response.rfind("}") + 1]
                return json.loads(json_str)
        except:
            pass

        return {}


def run_ai_analysis(df: pd.DataFrame, data_context: Dict = None) -> Dict:
    """Run AI-powered analysis"""
    analyzer = AIDataAnalyzer(df, data_context)
    return analyzer.analyze_with_ai()
