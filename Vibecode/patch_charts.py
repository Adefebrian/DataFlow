import re
import os

FILES_TO_PATCH = [
    "src/api/charts.py",
    "src/api/interactive_charts.py",
    "src/api/dynamic_charts.py",
    "src/api/ai_charts.py",
    "src/api/decision_charts.py",
    "src/api/routes.py",
]

def patch_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Add import if missing
    if "from src.utils.math_utils import safe_histogram_range" not in content:
        # insert after first import
        content = re.sub(r'^(import|from)\s+.*$', r'\g<0>\nfrom src.utils.math_utils import safe_histogram_range', content, count=1, flags=re.MULTILINE)
    
    # 1. Patch ax.hist(...) calls with data as first arg
    # This regex is a bit simplistic, let's just use string replacement for specific lines, or a more robust regex.
    # Actually, we can just replace `ax.hist(data,` with `ax.hist(data, range=safe_histogram_range(data),`
    content = content.replace("ax.hist(data,", "ax.hist(data, range=safe_histogram_range(data),")
    content = content.replace("ax.hist(\n                    data,", "ax.hist(\n                    data,\n                    range=safe_histogram_range(data),")
    
    # Also patch routes.py:
    content = content.replace("ax1.hist(\n        data,", "ax1.hist(\n        data,\n        range=safe_histogram_range(data),")
    
    # 2. Patch np.histogram
    content = content.replace("np.histogram(data,", "np.histogram(data, range=safe_histogram_range(data),")

    with open(filepath, 'w') as f:
        f.write(content)

for filepath in FILES_TO_PATCH:
    if os.path.exists(filepath):
        patch_file(filepath)
