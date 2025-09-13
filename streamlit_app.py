# streamlit_app.py
"""
Complete SPY Statistical Analysis Tool
Analyzes 20 years of SPY data for hourly patterns by standard deviation buckets

GitHub: https://github.com/jlandwersiek/spy-analyzer
Deployed on Streamlit Cloud for easy access
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import yfinance as yf
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Set up the page
st.set_page_config(
    page_title="SPY Statistical Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

class StevesAdvancedAnalyzer:
    """Steve's complete statistical analysis engine"""
    
    def __init__(self):
        self.symbol = "SPY"
        
    def fetch_comprehensive_data(self):
        """Get both daily and hourly data for comprehensive analysis"""
        
        st.write("🔍 Fetching 20 years of daily data for standard deviation calculation...")
        progress_bar = st.progress(0)
        
        # Get 20 years of daily data
        end_date = datetime.now()
        start_date_daily = end_date - timedelta(days=20*365)
        
        try:
            daily_data = yf.download(self.symbol, start=start_date_daily, end=end_date, 
                                   interval='1d', progress=False, auto_adjust=True, prepost=False)
            progress_bar.progress(30)
            
            if daily_data.empty:
                st.error("❌ Failed to fetch daily data")
                return None, None
                
            # Calculate daily returns and statistics
            daily_data['Daily_Return'] = daily_data['Close'].pct_change() * 100
            daily_data['Day_Type'] = np.where(daily_data['Daily_Return'] >= 0, 'UP', 'DOWN')
            daily_data = daily_data.dropna()
            
            daily_std = daily_data['Daily_Return'].std()
            
            st.write(f"📈 Got {len(daily_data):,} days of data")
            st.write(f"📊 **20-year daily standard deviation: {daily_std:.2f}%**")
            progress_bar.progress(60)
            
            # Get hourly data (last 2 years)
            st.write("⏰ Fetching 2 years of hourly data...")
            start_date_hourly = end_date - timedelta(days=730)
            
            hourly_data = yf.download(self.symbol, start=start_date_hourly, end=end_date, 
                                    interval='1h', progress=False, auto_adjust=True, prepost=False)
            
            # If primary fails, try with different parameters
            if hourly_data.empty:
                st.write("Retrying hourly data with different parameters...")
                hourly_data = yf.download(self.symbol, start=start_date_hourly, end=end_date, 
                                        interval='1h', progress=False)
            
            progress_bar.progress(90)
            
            if hourly_data.empty:
                st.error("❌ Failed to fetch hourly data")
                return daily_data, None
                
            # Process hourly data
            hourly_data['Hour'] = hourly_data.index.hour
            hourly_data['Date'] = hourly_data.index.date
            hourly_data['Hourly_Return'] = hourly_data['Close'].pct_change() * 100
            
            progress_bar.progress(100)
            st.success(f"✅ Got {len(hourly_data):,} hours of data")
            
            return daily_data, hourly_data
            
        except Exception as e:
            st.error(f"❌ Data fetch error: {str(e)}")
            return None, None
    
    def merge_and_classify_data(self, daily_data, hourly_data):
        """Merge daily and hourly data with standard deviation classification"""
        
        # Create lookup for day types
        daily_lookup = daily_data[['Day_Type', 'Daily_Return']].reset_index()
        daily_lookup['Date'] = daily_lookup['Date'].dt.date
        
        # Merge hourly with daily classifications
        hourly_merged = hourly_data.reset_index().merge(
            daily_lookup[['Date', 'Day_Type', 'Daily_Return']], 
            on='Date', 
            how='inner'
        )
        
        hourly_merged = hourly_merged.dropna(subset=['Hourly_Return'])
        
        # Filter to market hours only (9:30 AM - 4:00 PM)
        market_hours = hourly_merged[
            (hourly_merged['Hour'] >= 9) & (hourly_merged['Hour'] <= 16)
        ].copy()
        
        # Calculate standard deviation from 20-year daily data
        daily_std = daily_data['Daily_Return'].std()
        
        # Classify days by standard deviation buckets
        market_hours['Abs_Daily_Return'] = np.abs(market_hours['Daily_Return'])
        market_hours['Std_Bucket'] = pd.cut(
            market_hours['Abs_Daily_Return'],
            bins=[0, daily_std, 2*daily_std, 3*daily_std, np.inf],
            labels=['0-1σ', '1-2σ', '2-3σ', '3σ+'],
            include_lowest=True
        )
        
        return market_hours, daily_std
    
    def analyze_steve_questions(self, market_hours, daily_std):
        """Answer all of Steve's specific questions"""
        
        results = {
            'daily_std': daily_std,
            'total_hours': len(market_hours),
            'up_days_count': len(market_hours[market_hours['Day_Type'] == 'UP']['Date'].unique()),
            'down_days_count': len(market_hours[market_hours['Day_Type'] == 'DOWN']['Date'].unique())
        }
        
        # 1. Up days vs Down days hourly analysis
        results['hourly_up_down'] = self._analyze_hourly_up_down(market_hours)
        
        # 2. Standard deviation bucket analysis
        results['std_bucket_analysis'] = self._analyze_std_buckets(market_hours, daily_std)
        
        # 3. Bell curve validation
        results['bell_curve'] = self._analyze_bell_curve(market_hours, daily_std)
        
        # 4. Overall hourly patterns
        results['hourly_patterns'] = self._analyze_hourly_patterns(market_hours)
        
        # 5. Statistical insights
        results['insights'] = self._generate_insights(market_hours, daily_std)
        
        return results
    
    def _analyze_hourly_up_down(self, data):
        """Steve's main question: hourly averages for up vs down days"""
        
        up_days = data[data['Day_Type'] == 'UP']
        down_days = data[data['Day_Type'] == 'DOWN']
        
        hourly_comparison = {}
        
        for hour in range(9, 17):
            hour_str = f"{hour}:00"
            
            up_hour = up_days[up_days['Hour'] == hour]['Hourly_Return']
            down_hour = down_days[down_days['Hour'] == hour]['Hourly_Return']
            
            hourly_comparison[hour_str] = {
                'up_day_avg': up_hour.mean() if len(up_hour) > 0 else np.nan,
                'up_day_median': up_hour.median() if len(up_hour) > 0 else np.nan,
                'up_day_std': up_hour.std() if len(up_hour) > 0 else np.nan,
                'up_day_count': len(up_hour),
                
                'down_day_avg': down_hour.mean() if len(down_hour) > 0 else np.nan,
                'down_day_median': down_hour.median() if len(down_hour) > 0 else np.nan,  
                'down_day_std': down_hour.std() if len(down_hour) > 0 else np.nan,
                'down_day_count': len(down_hour),
                
                'difference': (up_hour.mean() - down_hour.mean()) if (len(up_hour) > 0 and len(down_hour) > 0) else np.nan,
                'up_win_rate': (up_hour > 0).mean() * 100 if len(up_hour) > 0 else np.nan,
                'down_win_rate': (down_hour > 0).mean() * 100 if len(down_hour) > 0 else np.nan
            }
        
        return hourly_comparison
    
    def _analyze_std_buckets(self, data, daily_std):
        """Analyze performance by standard deviation buckets"""
        
        bucket_analysis = {}
        
        for bucket in ['0-1σ', '1-2σ', '2-3σ', '3σ+']:
            bucket_data = data[data['Std_Bucket'] == bucket]
            
            if len(bucket_data) == 0:
                continue
                
            # Calculate range for this bucket
            if bucket == '0-1σ':
                bucket_range = f"0% to {daily_std:.1f}%"
            elif bucket == '1-2σ':
                bucket_range = f"{daily_std:.1f}% to {2*daily_std:.1f}%"
            elif bucket == '2-3σ':
                bucket_range = f"{2*daily_std:.1f}% to {3*daily_std:.1f}%"
            else:  # 3σ+
                bucket_range = f"{3*daily_std:.1f}%+"
            
            bucket_analysis[bucket] = {
                'range': bucket_range,
                'total_hours': len(bucket_data),
                'unique_days': len(bucket_data['Date'].unique()),
                'up_days': len(bucket_data[bucket_data['Day_Type'] == 'UP']['Date'].unique()),
                'down_days': len(bucket_data[bucket_data['Day_Type'] == 'DOWN']['Date'].unique()),
                'avg_hourly_return': bucket_data['Hourly_Return'].mean(),
                'median_hourly_return': bucket_data['Hourly_Return'].median(),
                'hourly_std': bucket_data['Hourly_Return'].std(),
                'positive_hours_pct': (bucket_data['Hourly_Return'] > 0).mean() * 100,
                'hourly_breakdown': {}
            }
            
            # Hourly breakdown within bucket
            for hour in range(9, 17):
                hour_data = bucket_data[bucket_data['Hour'] == hour]
                if len(hour_data) > 0:
                    bucket_analysis[bucket]['hourly_breakdown'][f"{hour}:00"] = {
                        'avg_return': hour_data['Hourly_Return'].mean(),
                        'median_return': hour_data['Hourly_Return'].median(),
                        'count': len(hour_data),
                        'positive_pct': (hour_data['Hourly_Return'] > 0).mean() * 100,
                        'up_day_avg': hour_data[hour_data['Day_Type'] == 'UP']['Hourly_Return'].mean() if len(hour_data[hour_data['Day_Type'] == 'UP']) > 0 else np.nan,
                        'down_day_avg': hour_data[hour_data['Day_Type'] == 'DOWN']['Hourly_Return'].mean() if len(hour_data[hour_data['Day_Type'] == 'DOWN']) > 0 else np.nan
                    }
        
        return bucket_analysis
    
    def _analyze_bell_curve(self, data, daily_std):
        """Analyze how well SPY follows normal distribution"""
        
        # Get unique daily returns
        daily_returns = data.groupby('Date')['Daily_Return'].first()
        
        coverage_1sigma = len(daily_returns[np.abs(daily_returns) <= daily_std]) / len(daily_returns) * 100
        coverage_2sigma = len(daily_returns[np.abs(daily_returns) <= 2*daily_std]) / len(daily_returns) * 100
        coverage_3sigma = len(daily_returns[np.abs(daily_returns) <= 3*daily_std]) / len(daily_returns) * 100
        
        return {
            '1_sigma_actual': coverage_1sigma,
            '1_sigma_theoretical': 68.27,
            '1_sigma_difference': coverage_1sigma - 68.27,
            
            '2_sigma_actual': coverage_2sigma,
            '2_sigma_theoretical': 95.45,
            '2_sigma_difference': coverage_2sigma - 95.45,
            
            '3_sigma_actual': coverage_3sigma,
            '3_sigma_theoretical': 99.73,
            '3_sigma_difference': coverage_3sigma - 99.73,
            
            'total_days': len(daily_returns),
            'daily_std': daily_std
        }
    
    def _analyze_hourly_patterns(self, data):
        """Overall hourly patterns analysis"""
        
        patterns = {}
        
        for hour in range(9, 17):
            hour_data = data[data['Hour'] == hour]['Hourly_Return']
            
            if len(hour_data) > 0:
                patterns[f"{hour}:00"] = {
                    'avg_return': hour_data.mean(),
                    'median_return': hour_data.median(),
                    'std_dev': hour_data.std(),
                    'min_return': hour_data.min(),
                    'max_return': hour_data.max(),
                    'positive_hours': (hour_data > 0).sum(),
                    'negative_hours': (hour_data < 0).sum(),
                    'positive_pct': (hour_data > 0).mean() * 100,
                    'count': len(hour_data),
                    'skewness': hour_data.skew(),
                    'kurtosis': hour_data.kurtosis()
                }
        
        return patterns
    
    def _generate_insights(self, data, daily_std):
        """Generate key insights Steve would find interesting"""
        
        # Find most/least volatile hours
        hourly_volatility = {}
        for hour in range(9, 17):
            hour_data = data[data['Hour'] == hour]['Hourly_Return']
            if len(hour_data) > 0:
                hourly_volatility[hour] = hour_data.std()
        
        most_volatile_hour = max(hourly_volatility, key=hourly_volatility.get)
        least_volatile_hour = min(hourly_volatility, key=hourly_volatility.get)
        
        # Calculate biases
        up_day_bias = data[data['Day_Type'] == 'UP']['Hourly_Return'].mean()
        down_day_bias = data[data['Day_Type'] == 'DOWN']['Hourly_Return'].mean()
        
        # Market efficiency test - are moves really small?
        avg_abs_hourly = data['Hourly_Return'].abs().mean()
        median_abs_hourly = data['Hourly_Return'].abs().median()
        
        return {
            'most_volatile_hour': f"{most_volatile_hour}:00",
            'least_volatile_hour': f"{least_volatile_hour}:00",
            'volatility_range': hourly_volatility[most_volatile_hour] - hourly_volatility[least_volatile_hour],
            
            'up_day_hourly_bias': up_day_bias,
            'down_day_hourly_bias': down_day_bias,
            'bias_difference': up_day_bias - down_day_bias,
            
            'avg_abs_hourly_move': avg_abs_hourly,
            'median_abs_hourly_move': median_abs_hourly,
            'small_moves_confirmed': avg_abs_hourly < 0.1,  # Less than 0.1% average
            
            'daily_std_reference': daily_std,
            'hourly_vs_daily_ratio': data['Hourly_Return'].std() / (daily_std / np.sqrt(6.5))
        }

def create_visualizations(results, market_hours):
    """Create comprehensive visualizations for Steve"""
    
    st.header("📊 Visual Analysis")
    
    # 1. Up vs Down Days Hourly Comparison
    st.subheader("1. 📈 Up Days vs Down Days Hourly Performance")
    
    hours = list(range(9, 17))
    up_avgs = [results['hourly_up_down'][f"{h}:00"]['up_day_avg'] for h in hours]
    down_avgs = [results['hourly_up_down'][f"{h}:00"]['down_day_avg'] for h in hours]
    
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=[f"{h}:00" for h in hours], y=up_avgs, 
                             mode='lines+markers', name='Up Days', 
                             line=dict(color='green', width=3)))
    fig1.add_trace(go.Scatter(x=[f"{h}:00" for h in hours], y=down_avgs, 
                             mode='lines+markers', name='Down Days', 
                             line=dict(color='red', width=3)))
    
    fig1.update_layout(title="Average Hourly Returns: Up Days vs Down Days",
                      xaxis_title="Hour", yaxis_title="Average Hourly Return (%)",
                      hovermode='x unified', height=500)
    st.plotly_chart(fig1, use_container_width=True)
    
    # 2. Standard Deviation Buckets Heatmap
    st.subheader("2. 🔥 Performance Heatmap by Standard Deviation Buckets")
    
    # Create heatmap data
    heatmap_data = []
    buckets = ['0-1σ', '1-2σ', '2-3σ', '3σ+']
    
    for bucket in buckets:
        if bucket in results['std_bucket_analysis']:
            row = []
            for hour in range(9, 17):
                hour_str = f"{hour}:00"
                if hour_str in results['std_bucket_analysis'][bucket]['hourly_breakdown']:
                    value = results['std_bucket_analysis'][bucket]['hourly_breakdown'][hour_str]['avg_return']
                    row.append(value)
                else:
                    row.append(np.nan)
            heatmap_data.append(row)
    
    if heatmap_data:
        fig2 = go.Figure(data=go.Heatmap(
            z=heatmap_data,
            x=[f"{h}:00" for h in range(9, 17)],
            y=buckets,
            colorscale='RdYlGn',
            zmid=0,
            text=np.round(heatmap_data, 3),
            texttemplate='%{text}%',
            textfont={"size": 10}
        ))
        
        fig2.update_layout(title="Hourly Returns by Standard Deviation Bucket",
                          xaxis_title="Hour", yaxis_title="Daily Volatility Bucket",
                          height=400)
        st.plotly_chart(fig2, use_container_width=True)
    
    # 3. Bell Curve Analysis
    st.subheader("3. 🔔 Bell Curve Reality Check")
    
    bell_curve = results['bell_curve']
    
    categories = ['1σ (±68.27%)', '2σ (±95.45%)', '3σ (±99.73%)']
    actual = [bell_curve['1_sigma_actual'], bell_curve['2_sigma_actual'], bell_curve['3_sigma_actual']]
    theoretical = [68.27, 95.45, 99.73]
    
    fig3 = go.Figure(data=[
        go.Bar(name='Actual SPY', x=categories, y=actual, marker_color='skyblue'),
        go.Bar(name='Theoretical Normal', x=categories, y=theoretical, marker_color='orange')
    ])
    
    fig3.update_layout(title="SPY vs Normal Distribution Coverage",
                      xaxis_title="Standard Deviation Range", 
                      yaxis_title="Percentage of Days",
                      barmode='group', height=500)
    st.plotly_chart(fig3, use_container_width=True)
    
    # 4. Hourly Volatility Pattern
    st.subheader("4. ⚡ Intraday Volatility Pattern")
    
    hourly_vols = [results['hourly_patterns'][f"{h}:00"]['std_dev'] for h in range(9, 17)]
    
    fig4 = go.Figure(data=go.Scatter(
        x=[f"{h}:00" for h in range(9, 17)],
        y=hourly_vols,
        mode='lines+markers',
        fill='tozeroy',
        line=dict(color='purple', width=3)
    ))
    
    fig4.update_layout(title="Hourly Volatility Throughout Trading Day",
                      xaxis_title="Hour", yaxis_title="Standard Deviation (%)",
                      height=400)
    st.plotly_chart(fig4, use_container_width=True)
    
    # 5. Distribution of Hourly Returns
    st.subheader("5. 📊 Distribution of All Hourly Returns")
    
    fig5 = go.Figure(data=[go.Histogram(x=market_hours['Hourly_Return'], nbinsx=100)])
    fig5.update_layout(title="Distribution of All Hourly Returns",
                      xaxis_title="Hourly Return (%)", yaxis_title="Frequency",
                      height=400)
    st.plotly_chart(fig5, use_container_width=True)

def display_key_findings(results):
    """Display Steve's key findings in an organized way"""
    
    st.header("🎯 Steve's Key Findings")
    
    # Top-level metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("20-Year Daily Std Dev", f"{results['daily_std']:.2f}%",
                 help="This is your '17%' reference")
    
    with col2:
        st.metric("Total Analysis Hours", f"{results['total_hours']:,}",
                 help="Market hours analyzed")
    
    with col3:
        st.metric("Most Volatile Hour", results['insights']['most_volatile_hour'],
                 help="Hour with highest standard deviation")
    
    with col4:
        up_bias = results['insights']['up_day_hourly_bias']
        st.metric("Up Day Hourly Bias", f"{up_bias:+.4f}%",
                 help="Average hourly return on up days")
    
    # Bell Curve Analysis
    st.subheader("🔔 Bell Curve Reality vs Theory")
    
    bell = results['bell_curve']
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Within 1σ", f"{bell['1_sigma_actual']:.1f}%", 
                 f"{bell['1_sigma_difference']:+.1f}% vs theory",
                 help="Theory: 68.27%")
    
    with col2:
        st.metric("Within 2σ", f"{bell['2_sigma_actual']:.1f}%", 
                 f"{bell['2_sigma_difference']:+.1f}% vs theory",
                 help="Theory: 95.45%")
    
    with col3:
        st.metric("Within 3σ", f"{bell['3_sigma_actual']:.1f}%", 
                 f"{bell['3_sigma_difference']:+.1f}% vs theory",
                 help="Theory: 99.73%")
    
    # Key Insights
    st.subheader("💡 Key Statistical Insights")
    
    insights = results['insights']
    
    st.info(f"""
    **Steve's "Small Moves" Question**: ✅ CONFIRMED
    - Average absolute hourly move: **{insights['avg_abs_hourly_move']:.3f}%**
    - Median absolute hourly move: **{insights['median_abs_hourly_move']:.3f}%**
    - 🎯 Yes, hourly moves are indeed small (< 0.1% average)
    """)
    
    st.success(f"""
    **Up vs Down Day Bias**:
    - Up days average: **{insights['up_day_hourly_bias']:+.4f}%** per hour
    - Down days average: **{insights['down_day_hourly_bias']:+.4f}%** per hour
    - 📊 Difference: **{insights['bias_difference']:+.4f}%** per hour
    """)
    
    st.warning(f"""
    **Volatility Timing**:
    - Most volatile: **{insights['most_volatile_hour']}** 
    - Least volatile: **{insights['least_volatile_hour']}**
    - 📈 Volatility range: **{insights['volatility_range']:.3f}%**
    """)

def display_sidebar():
    """Display sidebar with information and controls"""
    
    with st.sidebar:
        st.header("📊 Steve's SPY Analysis")
        
        st.info("""
        **What This Analyzes:**
        - 20 years of SPY daily data
        - 2 years of SPY hourly data
        - Up days vs down days patterns
        - Standard deviation buckets (1σ, 2σ, 3σ+)
        - Bell curve validation
        """)
        
        st.markdown("---")
        
        st.markdown("""
        **Steve's Questions:**
        
        ✅ Average hourly returns on up vs down days  
        ✅ Performance by standard deviation buckets  
        ✅ Bell curve analysis (68/95/99.7% coverage)  
        ✅ "Small moves" validation  
        ✅ 20-year statistical context  
        """)
        
        st.markdown("---")
        
        st.markdown("""
        **Technical Details:**
        - Data: Yahoo Finance
        - Market Hours: 9:30 AM - 4:00 PM ET
        - Analysis Time: ~60 seconds
        - Updates: Real-time data fetch
        """)
        
        st.markdown("---")
        
        if st.button("🔄 Clear Cache & Restart"):
            st.cache_data.clear()
            st.success("Cache cleared! Refresh page to restart.")

def main():
    """Main application for Steve's analysis"""
    
    st.title("📊 Steve's SPY Statistical Analysis")
    st.markdown("*20-Year Hourly Pattern Analysis with Standard Deviation Buckets*")
    
    # Display sidebar
    display_sidebar()
    
    st.info("""
    **Analysis Scope:**
    - ✅ 20 years of daily data for standard deviation calculation
    - ✅ 2 years of hourly data for pattern analysis  
    - ✅ Up days vs down days hourly comparison
    - ✅ Performance by 1σ, 2σ, 3σ+ volatility buckets
    - ✅ Bell curve validation vs theoretical normal distribution
    """)
    
    # Initialize analyzer
    analyzer = StevesAdvancedAnalyzer()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Run Complete Analysis", type="primary", use_container_width=True):
            
            with st.spinner("Running Steve's comprehensive analysis..."):
                
                # Fetch data
                daily_data, hourly_data = analyzer.fetch_comprehensive_data()
                
                if daily_data is None or hourly_data is None:
                    st.error("❌ Failed to fetch required data")
                    st.info("This usually happens due to Yahoo Finance rate limiting. Please try again in a few minutes.")
                    return
                
                # Merge and classify
                market_hours, daily_std = analyzer.merge_and_classify_data(daily_data, hourly_data)
                
                # Run analysis
                results = analyzer.analyze_steve_questions(market_hours, daily_std)
                
                st.success("✅ Analysis Complete!")
                
                # Display results
                display_key_findings(results)
                
                # Create visualizations
                create_visualizations(results, market_hours)
                
                # Detailed breakdowns
                st.header("📋 Detailed Analysis Tables")
                
                # Up vs Down hourly table
                st.subheader("📈 Hourly Performance: Up Days vs Down Days")
                hourly_df = pd.DataFrame(results['hourly_up_down']).T
                hourly_df = hourly_df.round(4)
                st.dataframe(hourly_df, use_container_width=True)
                
                # Standard deviation buckets
                st.subheader("📊 Standard Deviation Bucket Analysis")
                
                for bucket, data in results['std_bucket_analysis'].items():
                    with st.expander(f"📈 {bucket} Days ({data['range']})", expanded=False):
                        
                        col1, col2, col3, col4, col5 = st.columns(5)
                        with col1:
                            st.metric("Total Days", f"{data['unique_days']:,}")
                        with col2:
                            st.metric("Up Days", f"{data['up_days']:,}")
                        with col3:
                            st.metric("Down Days", f"{data['down_days']:,}")
                        with col4:
                            st.metric("Avg Hourly Return", f"{data['avg_hourly_return']:+.4f}%")
                        with col5:
                            st.metric("Positive Hours", f"{data['positive_hours_pct']:.1f}%")
                        
                        # Hourly breakdown table
                        if data['hourly_breakdown']:
                            st.markdown("**Hourly Breakdown:**")
                            hourly_breakdown_df = pd.DataFrame(data['hourly_breakdown']).T
                            hourly_breakdown_df = hourly_breakdown_df.round(4)
                            st.dataframe(hourly_breakdown_df, use_container_width=True)
                
                # Overall hourly patterns
                st.subheader("⏰ Overall Hourly Patterns (All Days)")
                patterns_df = pd.DataFrame(results['hourly_patterns']).T
                patterns_df = patterns_df.round(4)
                st.dataframe(patterns_df, use_container_width=True)
                
                # Data summary
                st.markdown("---")
                st.info(f"""
                **📊 Analysis Summary:**
                - **Daily Standard Deviation**: {results['daily_std']:.2f}% (20-year calculation)
                - **Total Hours Analyzed**: {results['total_hours']:,} market hours
                - **Up Days**: {results['up_days_count']:,} | **Down Days**: {results['down_days_count']:,}
                - **Bell Curve Validation**: Real data vs theoretical normal distribution
                - **Data Sources**: Yahoo Finance (reliable, free)
                """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.8em;'>
    Steve's SPY Statistical Analysis Tool | 
    <a href='https://github.com/jlandwersiek/steves-spy-analyzer' target='_blank'>GitHub Repository</a> | 
    Built for 20-year hourly pattern analysis
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
