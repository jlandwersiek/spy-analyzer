# 📊 SPY Hourly Pattern Analysis Tool

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://spy-analyzer.streamlit.app)

## Overview

A professional statistical analysis tool that examines SPY intraday trading patterns to answer key research questions about market behavior across different volatility regimes.

## 🎯 Research Questions Answered

**Question 1:** Do up days and down days show different hourly patterns?

**Question 2:** How do hourly patterns change during high vs low volatility days?

**Question 3:** Are hourly moves really small compared to daily moves?

**Question 4:** Does SPY follow the normal distribution "bell curve"?

## 🚀 Live Analysis

**Access the tool:** [https://spy-analyzer.streamlit.app](https://spy-analyzer.streamlit.app)

- No installation required
- Runs directly in browser
- Professional statistical analysis in 60 seconds
- Interactive charts and clear answers

## 📈 Key Features

### Statistical Analysis
- **Multi-year SPY data analysis**
- **Up vs Down day classification** with hourly breakdowns
- **Volatility buckets**: 0-1σ, 1-2σ, 2-3σ, 3σ+ performance analysis
- **Bell curve validation**: Real SPY vs theoretical normal distribution
- **Move size quantification**: Hourly vs daily comparison

### Interactive Visualizations
- 📊 Up vs Down days performance charts
- 📈 Hour-by-hour pattern analysis
- ⚡ Volatility bucket performance bars
- 🔍 Move size distribution histograms
- 🔔 Bell curve reality vs theory comparisons
- 📋 Professional statistical tables

### Data Quality
- **Primary Data Source**: Yahoo Finance (institutional-grade, free)
- **Market Hours Only**: 9:30 AM - 4:00 PM ET
- **Real-time Analysis**: Fresh data on every run
- **Comprehensive Coverage**: 3+ years daily, 6+ months hourly

## 📊 Sample Results

```
📈 ANSWER 1: Up Days vs Down Days
Up Days Average: +0.042%    Down Days Average: -0.031%
✅ Answer: YES - Up days average +0.073% better per hour

⚡ ANSWER 2: High vs Low Volatility Days  
• 0-1σ (Normal): +0.012% per hour
• 3σ+ (Extreme): +0.087% per hour
✅ Answer: YES - High volatility days show different patterns

🔍 ANSWER 3: Are Hourly Moves Small?
Average Hourly: 0.156%    Average Daily: 1.23%    (7.9x difference)
✅ Answer: YES - Hourly moves are very small

🔔 ANSWER 4: Does SPY Follow the Bell Curve?
Within 1σ: 69.2% (Theory: 68.3%)    Within 2σ: 94.1% (Theory: 95.4%)
✅ Answer: YES - SPY closely follows normal distribution
```

## 🛠️ Technical Implementation

### Data Processing
- **Multi-period analysis**: 3 years daily + 6 months hourly data
- **Volatility classification**: Statistical bucketing by standard deviation
- **Market hours filtering**: Only analyzes 9:30 AM - 4:00 PM ET
- **Day type classification**: Up/Down based on daily close vs open

### Statistical Methods
- **Standard deviation buckets**: Proper statistical classification by daily volatility
- **Bell curve analysis**: Empirical distribution testing vs normal distribution
- **Pattern recognition**: Time-series analysis of intraday behavior
- **Bias quantification**: Statistical significance testing of hourly patterns

### Visualization Technology
- **Interactive Charts**: Professional Plotly visualizations
- **Multiple Chart Types**: Bar charts, line graphs, histograms, pie charts, overlays
- **Real-time Updates**: Charts update with fresh data on each analysis
- **Professional Quality**: Publication-ready statistical graphics

## 🎯 Use Cases

### Financial Research
- Market microstructure analysis
- Intraday efficiency studies
- Volatility clustering research
- Statistical distribution validation

### Investment Strategy Development
- Optimal timing analysis
- Volatility regime identification
- Risk management insights
- Market behavior research

### Educational Applications
- Statistical distribution education
- Market behavior understanding
- Data science methodology demonstration
- Financial analysis training

## 🚀 Quick Start

1. **Visit the app**: [https://spy-analyzer.streamlit.app](https://spy-analyzer.streamlit.app)
2. **Click "Run Statistical Analysis"**
3. **Wait ~60 seconds** for data processing
4. **Explore results** with interactive charts and clear answers

## 📊 Data Sources & Methodology

### Data Sources
- **Yahoo Finance API**: Primary source for all SPY data
- **Coverage**: 3+ years of daily data, 6+ months of hourly data
- **Quality**: Institutional-grade data used in academic research
- **Reliability**: Free, widely-used, extensively validated

### Analysis Methodology
- **Standard Deviation Calculation**: Multi-year rolling calculation
- **Volatility Bucketing**: Statistical classification (0-1σ, 1-2σ, 2-3σ, 3σ+)
- **Pattern Detection**: Hour-by-hour analysis of return behavior
- **Distribution Testing**: Empirical vs theoretical normal distribution comparison

## 📄 Repository Structure

```
spy-analyzer/
├── streamlit_app.py          # Main analysis application
├── requirements.txt          # Python dependencies
├── README.md                # This documentation
├── .streamlit/
│   └── config.toml          # Application configuration
└── .gitignore               # Version control settings
```

## 🤝 Contributing

This tool is designed for educational and research purposes. Contributions welcome for:
- Additional statistical tests
- Enhanced visualizations
- Performance optimizations
- Extended data sources

## 📄 License

Open source project available under the MIT License.

---

**Live Analysis Tool**: [https://spy-analyzer.streamlit.app](https://spy-analyzer.streamlit.app)

*Professional SPY Statistical Analysis • Interactive Charts • Real-time Data*
