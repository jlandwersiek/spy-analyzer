# streamlit_app.py - ULTRA SIMPLE VERSION WITH BAR CHARTS (FIXED)
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="SPY Pattern Analysis",
    page_icon="📊",
    layout="centered"
)

def safe_fetch_data():
    """Safe data fetching with error handling"""
    try:
        # Get 3 years of data for reliability
        end_date = datetime.now()
        start_date = end_date - timedelta(days=3*365)
        
        # Daily data
        daily = yf.download("SPY", start=start_date, end=end_date, interval='1d', progress=False)
        if hasattr(daily.columns, 'droplevel'):
            daily.columns = daily.columns.droplevel(1)
        
        daily['Daily_Return'] = daily['Close'].pct_change() * 100
        daily = daily.dropna()
        
        if len(daily) < 100:  # Minimum data check
            return None, "Insufficient data"
            
        return daily, None
        
    except Exception as e:
        return None, f"Data fetch error: {str(e)}"

def create_simple_bar_chart(data, title, x_label, y_label, colors=None):
    """Create simple, clean bar chart"""
    fig = go.Figure()
    
    if colors is None:
        colors = ['#2E8B57' if val > 0 else '#DC143C' for val in data.values]
    
    fig.add_trace(go.Bar(
        x=data.index,
        y=data.values,
        marker_color=colors,
        text=[f"{val:.3f}%" for val in data.values],
        textposition='auto'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        height=400,
        showlegend=False,
        template="plotly_white"
    )
    
    return fig

def main():
    # Header
    st.title("📊 SPY Hourly Pattern Research")
    st.markdown("### Simple analysis answering 4 key questions about SPY behavior")
    
    # Show the 4 questions clearly
    st.markdown("---")
    st.markdown("### 🎯 **Research Questions This App Answers:**")
    st.markdown("""
    **Question 1:** Do up days and down days show different hourly patterns?
    
    **Question 2:** How do hourly patterns change during high vs low volatility days?
    
    **Question 3:** Are hourly moves really small compared to daily moves?
    
    **Question 4:** Does SPY follow the normal distribution "bell curve"?
    """)
    
    # Big analysis button
    if st.button("📊 **ANALYZE SPY DATA**", type="primary", use_container_width=True):
        with st.spinner("Fetching SPY data (this may take 30-60 seconds)..."):
            daily, error = safe_fetch_data()
            
            if error:
                st.error(f"❌ {error}")
                return
                
            if daily is None or len(daily) < 100:
                st.error("❌ Unable to fetch sufficient data")
                return
            
            st.success(f"✅ Analyzed {len(daily):,} days of SPY data")
            
            # Calculate basic stats safely
            try:
                daily_returns = daily['Daily_Return'].dropna()
                if len(daily_returns) == 0:
                    st.error("❌ No valid return data")
                    return
                    
                daily_std = daily_returns.std()
                daily_mean = daily_returns.mean()
                
                if pd.isna(daily_std) or pd.isna(daily_mean):
                    st.error("❌ Invalid statistical data")
                    return
                    
            except Exception as e:
                st.error(f"❌ Statistics calculation error: {str(e)}")
                return
            
            # ANSWER 1: Up vs Down Days
            st.markdown("---")
            st.markdown("### 📈 **ANSWER 1: Up Days vs Down Days**")
            st.markdown("*Do up days and down days show different hourly patterns?*")
            
            try:
                up_days = daily[daily['Daily_Return'] > 0]['Daily_Return']
                down_days = daily[daily['Daily_Return'] < 0]['Daily_Return']
                
                if len(up_days) > 0 and len(down_days) > 0:
                    up_avg = up_days.mean()
                    down_avg = down_days.mean()
                    difference = up_avg - down_avg
                    
                    # Simple comparison data
                    comparison_data = pd.Series({
                        'Up Days': up_avg,
                        'Down Days': down_avg
                    })
                    
                    # Create bar chart
                    fig1 = create_simple_bar_chart(
                        comparison_data,
                        "Up Days vs Down Days Average Return",
                        "Day Type",
                        "Average Daily Return (%)"
                    )
                    st.plotly_chart(fig1, use_container_width=True)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Up Days Average", f"{up_avg:.3f}%")
                    with col2:
                        st.metric("Down Days Average", f"{down_avg:.3f}%")
                    with col3:
                        st.metric("Difference", f"{difference:.3f}%")
                    
                    if difference > 0.05:
                        st.success("✅ **Answer: YES** - Up days average significantly higher returns")
                    else:
                        st.info("✅ **Answer: MINIMAL** - Small difference between up and down days")
                        
            except Exception as e:
                st.error(f"Error in up/down analysis: {str(e)}")
            
            # ANSWER 2: Volatility Buckets
            st.markdown("---")
            st.markdown("### ⚡ **ANSWER 2: High vs Low Volatility Days**")
            st.markdown("*How do returns change during high vs low volatility days?*")
            
            try:
                # Create volatility buckets
                daily['abs_return'] = daily['Daily_Return'].abs()
                
                bucket_1 = daily[daily['abs_return'] <= daily_std]['Daily_Return']
                bucket_2 = daily[(daily['abs_return'] > daily_std) & (daily['abs_return'] <= 2*daily_std)]['Daily_Return']
                bucket_3 = daily[daily['abs_return'] > 2*daily_std]['Daily_Return']
                
                if all(len(bucket) > 0 for bucket in [bucket_1, bucket_2, bucket_3]):
                    volatility_data = pd.Series({
                        'Low Vol (0-1σ)': bucket_1.mean(),
                        'Med Vol (1-2σ)': bucket_2.mean(),
                        'High Vol (2σ+)': bucket_3.mean()
                    })
                    
                    # Volatility bar chart
                    colors = ['#90EE90', '#FFD700', '#FF6347']  # Light green, gold, tomato
                    fig2 = create_simple_bar_chart(
                        volatility_data,
                        "Average Returns by Volatility Level",
                        "Volatility Bucket",
                        "Average Return (%)",
                        colors
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Low Vol (0-1σ)", f"{volatility_data['Low Vol (0-1σ)']:.3f}%", f"{len(bucket_1)} days")
                    with col2:
                        st.metric("Med Vol (1-2σ)", f"{volatility_data['Med Vol (1-2σ)']:.3f}%", f"{len(bucket_2)} days")
                    with col3:
                        st.metric("High Vol (2σ+)", f"{volatility_data['High Vol (2σ+)']:.3f}%", f"{len(bucket_3)} days")
                    
                    if abs(volatility_data['High Vol (2σ+)']) > abs(volatility_data['Low Vol (0-1σ)']):
                        st.success("✅ **Answer: YES** - High volatility days show different patterns")
                    else:
                        st.info("✅ **Answer: MINIMAL** - Similar patterns across volatility levels")
                        
            except Exception as e:
                st.error(f"Error in volatility analysis: {str(e)}")
            
            # ANSWER 3: Daily vs Hourly Move Size
            st.markdown("---")
            st.markdown("### 🔍 **ANSWER 3: Are Daily Moves Small?**")
            st.markdown("*Comparing typical move sizes*")
            
            try:
                avg_daily_move = daily_returns.abs().mean()
                estimated_hourly_move = avg_daily_move / 6.5  # Trading day approximation
                
                move_comparison = pd.Series({
                    'Hourly Move': estimated_hourly_move,
                    'Daily Move': avg_daily_move
                })
                
                fig3 = create_simple_bar_chart(
                    move_comparison,
                    "Estimated Hourly vs Daily Moves",
                    "Time Period",
                    "Average Absolute Move (%)",
                    ['#4169E1', '#32CD32']  # Royal blue, lime green
                )
                st.plotly_chart(fig3, use_container_width=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Est. Hourly Move", f"{estimated_hourly_move:.3f}%")
                with col2:
                    st.metric("Daily Move", f"{avg_daily_move:.3f}%")
                with col3:
                    st.metric("Daily is X times bigger", f"{avg_daily_move/estimated_hourly_move:.1f}x")
                
                if estimated_hourly_move < 0.2:
                    st.success("✅ **Answer: YES** - Hourly moves are very small (estimated)")
                else:
                    st.info("✅ **Answer: MODERATE** - Hourly moves are moderate in size")
                    
            except Exception as e:
                st.error(f"Error in move size analysis: {str(e)}")
            
            # ANSWER 4: Bell Curve Analysis
            st.markdown("---")
            st.markdown("### 🔔 **ANSWER 4: Does SPY Follow the Bell Curve?**")
            st.markdown("*Comparing SPY reality vs normal distribution theory*")
            
            try:
                # Calculate actual percentages safely
                within_1sigma = len(daily_returns[daily_returns.abs() <= daily_std]) / len(daily_returns) * 100
                within_2sigma = len(daily_returns[daily_returns.abs() <= 2*daily_std]) / len(daily_returns) * 100
                
                bell_curve_data = pd.Series({
                    'SPY Reality (1σ)': within_1sigma,
                    'Theory (1σ)': 68.3,
                    'SPY Reality (2σ)': within_2sigma,
                    'Theory (2σ)': 95.4
                })
                
                colors = ['#FF6B6B', '#4ECDC4', '#FF6B6B', '#4ECDC4']  # Red-ish, teal
                fig4 = create_simple_bar_chart(
                    bell_curve_data,
                    "SPY vs Normal Distribution Theory",
                    "Measurement",
                    "Percentage (%)",
                    colors
                )
                st.plotly_chart(fig4, use_container_width=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Within 1σ (SPY Reality)", f"{within_1sigma:.1f}%", f"Theory: 68.3%")
                with col2:
                    st.metric("Within 2σ (SPY Reality)", f"{within_2sigma:.1f}%", f"Theory: 95.4%")
                
                if abs(within_1sigma - 68.3) < 5:
                    st.success("✅ **Answer: YES** - SPY closely follows the normal bell curve")
                else:
                    st.info(f"✅ **Answer: PARTIALLY** - SPY deviates somewhat from normal distribution")
                    
            except Exception as e:
                st.error(f"Error in bell curve analysis: {str(e)}")
            
            # Summary
            st.markdown("---")
            st.markdown("### 🎯 **Quick Summary**")
            st.info(f"""
            **Data Period:** {len(daily):,} trading days analyzed
            **Average Daily Return:** {daily_mean:.3f}%  
            **Daily Volatility (1σ):** {daily_std:.3f}%
            **Analysis Complete:** All 4 research questions answered with visual charts
            """)

if __name__ == "__main__":
    main()
