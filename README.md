# DataFlow - Enterprise Analytics Platform

DataFlow is a production-ready autonomous data analysis system with a beautiful glassmorphism UI. Upload CSV files and get AI-powered insights, interactive charts, predictions, and comprehensive analytics.

## Features

### Core Capabilities
- **CSV Upload and Processing** - Drag and drop CSV files for instant analysis
- **Auto Data Profiling** - Automatic data type detection, statistics, and quality assessment
- **Data Cleaning** - Automatic handling of missing values, outliers, and duplicates
- **Feature Engineering** - Intelligent feature creation and transformation

### AI-Powered Analytics
- **Smart Chart Selection** - AI recommends the best visualization for your data
- **Automated Insights** - Generate business insights using LLM (Hyperbolic API)
- **Anti-Hallucination** - Validates AI-generated insights against actual data
- **Custom Analytics** - Tableau and Power BI style free-form workspace

### Visualizations
- **30+ Chart Types** - Bar, line, area, pie, donut, treemap, scatter, heatmap, and more
- **Interactive Charts** - Zoom, pan, hover tooltips, real-time updates
- **Prediction Charts** - Trend projection, moving averages, growth rate forecasting
- **Custom Analytics** - Build custom dashboards with multiple charts

### Dashboard and Reporting
- **My Dashboard** - Pin and arrange favorite visualizations
- **PDF Export** - Export dashboards and reports as PDF
- **HTML Reports** - Beautiful dark-themed reports with all analytics
- **Currency-Aware KPIs** - Support for USD, IDR, EUR, GBP, JPY, SGD

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.12+ (for local development)
- Node.js 20+ (for frontend development)

### Option 1: Docker (Recommended)

#### Production Mode
```bash
# Clone the repository
git clone https://github.com/Adefebrian/DataFlow.git
cd DataFlow

# Start production (nginx static build)
make up

# Or without make:
docker compose --profile prod up -d --build
```

#### Development Mode (Hot Reload)
```bash
# Start with Vite hot-reload
make dev

# Or without make:
docker compose --profile dev up -d
```

**Access**: http://localhost:3000  
**Login**: admin / admin123

### Option 2: Local Development

#### Backend
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your settings

# Run the server
python main.py
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection string | SQLite (local) |
| REDIS_URL | Redis connection string | None |
| HYPERBOLIC_API_KEY | API key for AI insights | Required |
| USE_SQLITE | Use SQLite instead of PostgreSQL | true |
| R2_* | Cloudflare R2 storage (optional) | None |

### Getting a Hyperbolic API Key
1. Visit [hyperbolic.xyz](https://hyperbolic.xyz)
2. Sign up for an account
3. Generate an API key
4. Add it to your `.env` file

## Project Structure

```
DataFlow/
├── Makefile                     # Docker shortcuts
├── docker-compose.yml           # Multi-container setup
├── Dockerfile                   # Backend (Python/FastAPI)
├── requirements.txt             # Python dependencies
├── main.py                      # Entry point
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
│
├── src/
│   ├── api/
│   │   ├── routes.py            # Main API routes
│   │   ├── charts.py            # Chart generation
│   │   ├── insights.py          # AI insights
│   │   ├── prediction_charts.py # Forecasting
│   │   └── ...
│   ├── agents/
│   │   ├── data_profiler.py     # Data analysis
│   │   ├── feature_engineer.py  # Feature creation
│   │   ├── report_generator.py  # Report generation
│   │   └── ...
│   ├── services/
│   │   ├── llm.py               # LLM integration
│   │   ├── storage.py           # File storage
│   │   └── ...
│   └── ...
│
└── frontend/
    ├── Dockerfile               # Frontend build
    ├── nginx.conf               # Production server
    ├── vite.config.ts           # Vite configuration
    ├── package.json             # Node dependencies
    └── src/
        ├── pages/               # React pages
        ├── components/          # UI components
        ├── hooks/              # Custom hooks
        └── ...
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/login | User authentication |
| POST | /upload | Upload CSV file |
| POST | /pipeline/run | Start analysis pipeline |
| GET | /pipeline/{job_id}/status | Get job status |
| GET | /pipeline/{job_id}/analytics | Get analytics results |
| GET | /pipeline/all | List all jobs |
| GET | /health | Health check |

## Docker Commands

```bash
make up          # Production build
make dev         # Development mode
make down        # Stop all containers
make rebuild     # Force rebuild
make logs        # View all logs
make logs-api    # View API logs
make shell       # Shell into container
```

## Deployment

### Render.com (Recommended for Free Tier)

1. Push to GitHub
2. Connect GitHub to Render
3. Create a new Web Service
4. Settings:
   - Build Command: pip install -r requirements.txt
   - Start Command: uvicorn src.api.routes:app --host 0.0.0.0 --port $PORT

### Railway

1. Install Railway CLI
2. Run: railway init
3. Run: railway up
4. Set environment variables in Railway dashboard

### Fly.io

1. Install Fly CLI
2. Run: fly launch
3. Run: fly deploy

### Heroku

1. Create a Procfile with:
   ```
   web: uvicorn src.api.routes:app --host 0.0.0.0 --port $PORT
   ```
2. Run: heroku create
3. Run: git push heroku main

## Tech Stack

### Backend
- FastAPI - Modern Python web framework
- Pandas - Data manipulation
- LangGraph - AI agent orchestration
- Plotly - Interactive charts
- SQLite/PostgreSQL - Database

### Frontend
- React 18 - UI framework
- Vite - Build tool
- Tailwind CSS - Styling
- Plotly.js - Chart rendering
- Recharts - Additional charts

## Screenshots

The platform features a modern glassmorphism design with:
- Dark theme by default
- Interactive charts with tooltips
- Drag and drop file upload
- Custom analytics workspace
- Dashboard with pinned charts

## License

Personal Use Only - This software is for personal use only. Commercial use is not permitted.

## Contact

For questions or inquiries:
- Instagram: @prerich.brian
- Email: adefebrianpro@gmail.com

---

Built with love using FastAPI, React, and Plotly
