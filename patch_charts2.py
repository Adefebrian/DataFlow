import os
filepath = "src/api/routes.py"
with open(filepath, 'r') as f:
    content = f.read()

content = content.replace("ax.hist(\n                    df[cols[i]].dropna(),", "ax.hist(\n                    df[cols[i]].dropna(),\n                    range=safe_histogram_range(df[cols[i]].dropna()),")
with open(filepath, 'w') as f:
    f.write(content)
