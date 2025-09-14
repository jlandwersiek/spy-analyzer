# streamlit_app.py - COMPLETE ENHANCED VERSION WITH ALL VISUALS
"""
SPY Hourly Pattern Analysis - Enhanced with Comprehensive Visualizations
Answers specific research questions about intraday trading patterns
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
import streamlit as st
import plotly.graph_objects as go
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Set up the page
st.set_page_config(
    page_title="SPY Pattern Analysis",
    page_icon="📊",
    layout="centered"
)

def fetch_data():
    """Simple data fetching"""
    try:
        # Get 3 years of data for reliability
        end_date = datetime.now()
        start_date = end_date - timedelta(days=3*365)
        
        # Daily data
        daily = yf.download("SPY", start=start_date, end=end_date, interval='1d', progress=False)
        if hasattr(daily.columns, 'droplevel'):
            daily.columns = daily.columns.droplevel(1)
        
        daily['Daily_Return'] = daily['Close'].pct_change() * 100
        daily['Day_Type'] = np.where(daily['Daily_Return'] >= 0, 'UP', 'DOWN')
        daily = daily.dropna()
        
        # Hourly data (6 months)
        hourly_start = end_date - timedelta(days=180)
        hourly = yf.download("SPY", start=hourly_start, end=end_date, interval='1h', progress=False)
        if hasattr(hourly.columns, 'droplevel'):
            hourly.columns = hourly.columns.droplevel(1)
        
        return daily, hourly
    except:
        return None, None

def process_data(daily, hourly):
    """Simple data processing"""
    try:
        daily_std = daily['Daily_Return'].std()
        
        # Process hourly data simply
        results = []
        prev_close = None
        
        for idx, row in hourly.iterrows():
            hour = idx.hour
            date = idx.date()
            
            # Only market hours
            if hour < 9 or hour > 16:
                continue
            
            # Calculate hourly return
            if prev_close is not None:
                hourly_return = ((row['Close'] - prev_close) / prev_close) * 100
            else:
                hourly_return = 0
            
            # Find matching daily data
            daily_match = daily[daily.index.date == date]
            if len(daily_match) > 0:
                daily_info = daily_match.iloc[0]
                
                # Standard deviation bucket
                abs_daily_return = abs(daily_info['Daily_Return'])
                if abs_daily_return <= daily_std:
                    bucket = '0-1σ (Normal)'
                elif abs_daily_return <= 2 * daily_std:
                    bucket = '1-2σ (Moderate)'
                elif abs_daily_return <= 3 * daily_std:
                    bucket = '2-3σ (High Vol)'
                else:
                    bucket = '3σ+ (Extreme)'
                
                results.append({
                    'hour': hour,
                    'hourly_return': hourly_return,
                    'day_type': daily_info['Day_Type'],
                    'daily_return': daily_info['Daily_Return'],
                    'volatility_bucket': bucket
                })
            
            prev_close = row['Close']
        
        return pd.DataFrame(results), daily_std
    except:
        return None, None

def main():
    st.title("📊 SPY Hourly Pattern Research")
    st.markdown("**Professional analysis answering 4 key questions about SPY intraday behavior**")
    
    # Show exactly what questions we answer
    st.markdown("---")
    st.markdown("### 🎯 **Research Questions This Answers:**")
    
    st.markdown("""
    **Question 1:** Do up days and down days show different hourly patterns?
    
    **Question 2:** How do hourly patterns change during high vs low volatility days?
    
    **Question 3:** Are hourly moves really small compared to daily moves?
    
    **Question 4:** Does SPY follow the normal distribution "bell curve"?
    """)
    
    st.markdown("---")
    
    # Simple run button
    if st.button("📊 **ANALYZE SPY DATA**", type="primary"):
        
        with st.spinner("Getting SPY data and analyzing patterns..."):
            
            # Get data
            daily, hourly = fetch_data()
            if daily is None:
                st.error("❌ Could not get data. Try again later.")
                return
            
            # Process data
            data, daily_std = process_data(daily, hourly)
            if data is None:
                st.error("❌ Could not process data. Try again later.")
                return
            
            st.success("✅ Analysis complete! Here are the answers:")
            
            # ANSWER 1: Up vs Down Days
            st.markdown("---")
            st.markdown("### 📈 **ANSWER 1: Up Days vs Down Days**")
            st.markdown("*Do up days and down days show different hourly patterns?*")
            
            # Simple comparison
            up_data = data[data['day_type'] == 'UP']
            down_data = data[data['day_type'] == 'DOWN']
            
            up_avg = up_data['hourly_return'].mean()
            down_avg = down_data['hourly_return'].mean()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Up Days Average", f"{up_avg:+.3f}%", help="Average hourly return on up days")
            with col2:
                st.metric("Down Days Average", f"{down_avg:+.3f}%", help="Average hourly return on down days")
            with col3:
                difference = up_avg - down_avg
                st.metric("Difference", f"{difference:+.3f}%", help="How much better up days perform")
            
            # Simple bar chart
            fig1 = go.Figure(data=[
                go.Bar(x=['Up Days', 'Down Days'], 
                       y=[up_avg, down_avg],
                       marker_color=['green' if up_avg > 0 else 'red', 
                                   'green' if down_avg > 0 else 'red'])
            ])
            fig1.update_layout(
                title="Average Hourly Returns: Up Days vs Down Days",
                yaxis_title="Average Hourly Return (%)",
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig1, use_container_width=True)
            
            # Hour-by-hour breakdown chart
            hourly_patterns = []
            hours = []
            up_hourly = []
            down_hourly = []
            
            for hour in range(9, 17):
                hour_up = up_data[up_data['hour'] == hour]['hourly_return'].mean()
                hour_down = down_data[down_data['hour'] == hour]['hourly_return'].mean()
                if not pd.isna(hour_up) and not pd.isna(hour_down):
                    hours.append(f"{hour}:00")
                    up_hourly.append(hour_up)
                    down_hourly.append(hour_down)
            
            if len(hours) > 3:  # Only show if we have enough data
                fig1b = go.Figure()
                fig1b.add_trace(go.Scatter(x=hours, y=up_hourly, mode='lines+markers', 
                                          name='Up Days', line=dict(color='green', width=3)))
                fig1b.add_trace(go.Scatter(x=hours, y=down_hourly, mode='lines+markers', 
                                          name='Down Days', line=dict(color='red', width=3)))
                fig1b.update_layout(
                    title="Hourly Pattern Throughout the Trading Day",
                    xaxis_title="Hour of Day", 
                    yaxis_title="Average Return (%)",
                    height=400
                )
                st.plotly_chart(fig1b, use_container_width=True)
            
            if abs(difference) > 0.01:
                st.info(f"✅ **Answer:** YES - Up days average {difference:+.3f}% better per hour than down days")
            else:
                st.info("✅ **Answer:** NO significant difference - both types of days show similar hourly patterns")
            
            # ANSWER 2: Volatility Buckets
            st.markdown("---")
            st.markdown("### ⚡ **ANSWER 2: High vs Low Volatility Days**")
            st.markdown("*How do hourly patterns change during high vs low volatility days?*")
            
            # Show volatility bucket performance
            bucket_stats = data.groupby('volatility_bucket')['hourly_return'].agg(['mean', 'count']).round(3)
            
            # Ensure all buckets are included, even with small data
            chart_buckets = []
            chart_values = []
            chart_colors = []
            
            st.markdown("**Average hourly returns by volatility level:**")
            
            # Process all buckets, including 3σ+
            bucket_order = ['0-1σ (Normal)', '1-2σ (Moderate)', '2-3σ (High Vol)', '3σ+ (Extreme)']
            
            for bucket in bucket_order:
                if bucket in bucket_stats.index:
                    stats = bucket_stats.loc[bucket]
                    if stats['count'] > 5:  # Lower threshold to show 3σ+
                        st.write(f"• **{bucket}**: {stats['mean']:+.3f}% per hour ({int(stats['count'])} hours)")
                        chart_buckets.append(bucket.replace(' (', '\n('))  # Line break for cleaner chart
                        chart_values.append(stats['mean'])
                        # Color coding: green for positive, red for negative, more intense for extreme
                        if '3σ+' in bucket:
                            chart_colors.append('darkgreen' if stats['mean'] > 0 else 'darkred')
                        elif '2-3σ' in bucket:
                            chart_colors.append('orange' if stats['mean'] > 0 else 'coral')
                        else:
                            chart_colors.append('green' if stats['mean'] > 0 else 'red')
            
            # Volatility performance bar chart
            if len(chart_buckets) > 1:
                fig2 = go.Figure(data=[
                    go.Bar(x=chart_buckets, 
                           y=chart_values,
                           marker_color=chart_colors,
                           text=[f"{v:+.3f}%" for v in chart_values],
                           textposition='outside')
                ])
                fig2.update_layout(
                    title="Hourly Performance by Volatility Level",
                    yaxis_title="Average Hourly Return (%)",
                    showlegend=False,
                    height=450
                )
                st.plotly_chart(fig2, use_container_width=True)
            
            # Show how many days fall into each bucket
            bucket_counts = data.groupby('volatility_bucket')['daily_return'].nunique()
            if len(bucket_counts) > 1:
                fig2b = go.Figure(data=[
                    go.Pie(labels=bucket_counts.index, 
                           values=bucket_counts.values,
                           hole=0.3)
                ])
                fig2b.update_layout(
                    title="Distribution of Days by Volatility Level",
                    height=400
                )
                st.plotly_chart(fig2b, use_container_width=True)
            
            normal_avg = bucket_stats.loc['0-1σ (Normal)', 'mean'] if '0-1σ (Normal)' in bucket_stats.index else 0
            high_vol_buckets = [b for b in bucket_stats.index if '2-3σ' in b or '3σ+' in b]
            
            if high_vol_buckets:
                high_vol_avg = bucket_stats.loc[high_vol_buckets[0], 'mean']
                if abs(high_vol_avg - normal_avg) > 0.02:
                    st.info(f"✅ **Answer:** YES - High volatility days show different patterns ({high_vol_avg:+.3f}% vs {normal_avg:+.3f}%)")
                else:
                    st.info("✅ **Answer:** NO major difference - volatility level doesn't significantly change hourly patterns")
            
            # ANSWER 3: Small Moves
            st.markdown("---")
            st.markdown("### 🔍 **ANSWER 3: Are Hourly Moves Small?**")
            st.markdown("*Are hourly moves really small compared to daily moves?*")
            
            avg_hourly_move = data['hourly_return'].abs().mean()
            avg_daily_move = daily['Daily_Return'].abs().mean()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Average Hourly Move", f"{avg_hourly_move:.3f}%")
            with col2:
                st.metric("Average Daily Move", f"{avg_daily_move:.2f}%")
            with col3:
                ratio = avg_daily_move / avg_hourly_move if avg_hourly_move > 0 else 0
                st.metric("Daily is X times bigger", f"{ratio:.1f}x")
            
            # Simple comparison bar chart
            fig3 = go.Figure(data=[
                go.Bar(x=['Hourly Moves', 'Daily Moves'], 
                       y=[avg_hourly_move, avg_daily_move],
                       marker_color=['lightblue', 'darkblue'])
            ])
            fig3.update_layout(
                title="Average Move Size: Hourly vs Daily",
                yaxis_title="Average Move Size (%)",
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig3, use_container_width=True)
            
            # Distribution of hourly moves histogram
            fig3b = go.Figure(data=[
                go.Histogram(x=data['hourly_return'].abs(), nbinsx=50, 
                            marker_color='lightblue', opacity=0.7)
            ])
            fig3b.update_layout(
                title="Distribution of Hourly Move Sizes (Shows How Small They Are)",
                xaxis_title="Hourly Move Size (%)",
                yaxis_title="Number of Hours",
                height=400
            )
            # Add vertical line for average
            fig3b.add_vline(x=avg_hourly_move, line_dash="dash", line_color="red",
                           annotation_text=f"Average: {avg_hourly_move:.3f}%")
            st.plotly_chart(fig3b, use_container_width=True)
            
            if avg_hourly_move < 0.2:
                st.info(f"✅ **Answer:** YES - Hourly moves are very small ({avg_hourly_move:.3f}% average)")
            else:
                st.info(f"✅ **Answer:** NO - Hourly moves are not that small ({avg_hourly_move:.3f}% average)")
            
            # ANSWER 4: Bell Curve
            st.markdown("---")
            st.markdown("### 🔔 **ANSWER 4: Does SPY Follow the Bell Curve?**")
            st.markdown("*Does SPY follow the normal distribution theory?*")
            
            # Calculate bell curve coverage
            daily_returns = daily['Daily_Return']
            
            within_1sigma = len(daily_returns[abs(daily_returns) <= daily_std]) / len(daily_returns) * 100
            within_2sigma = len(daily_returns[abs(daily_returns) <= 2*daily_std]) / len(daily_returns) * 100
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Within 1σ (Normal range)", f"{within_1sigma:.1f}%", f"Theory: 68.3%")
            with col2:
                st.metric("Within 2σ (Wider range)", f"{within_2sigma:.1f}%", f"Theory: 95.4%")
            
            # Bell curve comparison chart
            categories = ['Within 1σ\n(68% should be here)', 'Within 2σ\n(95% should be here)']
            actual_values = [within_1sigma, within_2sigma]
            theoretical_values = [68.3, 95.4]
            
            fig4 = go.Figure(data=[
                go.Bar(name='SPY Reality', x=categories, y=actual_values, marker_color='skyblue'),
                go.Bar(name='Theory', x=categories, y=theoretical_values, marker_color='orange')
            ])
            fig4.update_layout(
                title="SPY vs Bell Curve Theory",
                yaxis_title="Percentage of Days (%)",
                barmode='group',
                height=400
            )
            st.plotly_chart(fig4, use_container_width=True)
            
            # Actual distribution histogram with normal overlay
            fig4b = go.Figure()
            
            # Histogram of actual returns
            fig4b.add_trace(go.Histogram(
                x=daily_returns, 
                nbinsx=50,
                name='Actual SPY Returns',
                marker_color='lightblue',
                opacity=0.7,
                yaxis='y',
                histnorm='probability density'
            ))
            
            # Theoretical normal curve
            x_range = np.linspace(daily_returns.min(), daily_returns.max(), 100)
            normal_curve = stats.norm.pdf(x_range, daily_returns.mean(), daily_std)
            
            fig4b.add_trace(go.Scatter(
                x=x_range,
                y=normal_curve,
                mode='lines',
                name='Theoretical Bell Curve',
                line=dict(color='red', width=3)
            ))
            
            # Add vertical lines for standard deviations
            mean_return = daily_returns.mean()
            fig4b.add_vline(x=mean_return + daily_std, line_dash="dash", line_color="green",
                           annotation_text="1σ")
            fig4b.add_vline(x=mean_return - daily_std, line_dash="dash", line_color="green",
                           annotation_text="-1σ")
            fig4b.add_vline(x=mean_return + 2*daily_std, line_dash="dash", line_color="orange",
                           annotation_text="2σ")
            fig4b.add_vline(x=mean_return - 2*daily_std, line_dash="dash", line_color="orange",
                           annotation_text="-2σ")
            
            fig4b.update_layout(
                title="SPY Return Distribution vs Perfect Bell Curve",
                xaxis_title="Daily Return (%)",
                yaxis_title="Probability Density",
                height=450
            )
            st.plotly_chart(fig4b, use_container_width=True)
            
            if abs(within_1sigma - 68.3) < 5:
                st.info("✅ **Answer:** YES - SPY closely follows the normal bell curve distribution")
            else:
                st.info(f"✅ **Answer:** NO - SPY deviates from normal distribution ({within_1sigma:.1f}% vs expected 68.3%)")
            
            # Simple summary
            st.markdown("---")
            st.markdown("### 📋 **SUMMARY**")
            
            st.info(f"""
            **Data analyzed:** {len(data):,} hours across {len(daily):,} days
            
            **Daily standard deviation:** {daily_std:.2f}% (this is what we use for volatility buckets)
            
            **Key insight:** Average hourly move is {avg_hourly_move:.3f}% vs {avg_daily_move:.2f}% daily
            """)
    
    # Footer
    st.markdown("---")
    st.markdown("<div style='text-align: center; color: #666; font-size: 0.8em;'>Professional SPY Pattern Analysis | Data from Yahoo Finance</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
