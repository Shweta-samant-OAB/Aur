import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Fashion Product Analytics Dashboard",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-container {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .stSelectbox > div > div > select {
        background-color: white;
    }
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

def load_and_process_data(uploaded_file):
    """Load and preprocess the uploaded CSV data"""
    try:
        df = pd.read_csv(uploaded_file)
        
        # Clean and process the data
        # Convert price_amount to numeric
        if 'price_amount' in df.columns:
            df['price_amount'] = pd.to_numeric(df['price_amount'], errors='coerce')
        
        # Handle missing values for key columns
        categorical_cols = ['brand_name', 'category_main', 'category_sub', 'color', 'price_point', 'availability']
        for col in categorical_cols:
            if col in df.columns:
                df[col] = df[col].fillna('Unknown')
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def create_filters(df):
    """Create sidebar filters"""
    st.sidebar.header("🔍 Filters")
    
    filters = {}
    
    # Brand filter
    if 'brand_name' in df.columns:
        brands = ['All'] + sorted(df['brand_name'].unique().tolist())
        filters['brand'] = st.sidebar.selectbox("Brand", brands)
    
    # Category filters
    if 'category_main' in df.columns:
        categories = ['All'] + sorted(df['category_main'].unique().tolist())
        filters['category_main'] = st.sidebar.selectbox("Main Category", categories)
    
    if 'category_sub' in df.columns:
        sub_categories = ['All'] + sorted(df['category_sub'].unique().tolist())
        filters['category_sub'] = st.sidebar.selectbox("Sub Category", sub_categories)
    
    # Price range filter
    if 'price_amount' in df.columns:
        price_min = float(df['price_amount'].min()) if not df['price_amount'].isna().all() else 0
        price_max = float(df['price_amount'].max()) if not df['price_amount'].isna().all() else 1000
        filters['price_range'] = st.sidebar.slider(
            "Price Range ($)", 
            min_value=price_min, 
            max_value=price_max, 
            value=(price_min, price_max),
            step=10.0
        )
    
    # Price point filter
    if 'price_point' in df.columns:
        price_points = ['All'] + sorted(df['price_point'].unique().tolist())
        filters['price_point'] = st.sidebar.selectbox("Price Point", price_points)
    
    # Color filter
    if 'color' in df.columns:
        colors = ['All'] + sorted(df['color'].unique().tolist())
        filters['color'] = st.sidebar.multiselect("Colors", colors, default=['All'])
    
    # Availability filter
    if 'availability' in df.columns:
        availability_options = ['All'] + sorted(df['availability'].unique().tolist())
        filters['availability'] = st.sidebar.selectbox("Availability", availability_options)
    
    return filters

def apply_filters(df, filters):
    """Apply selected filters to the dataframe"""
    filtered_df = df.copy()
    
    # Apply brand filter
    if filters.get('brand') and filters['brand'] != 'All':
        filtered_df = filtered_df[filtered_df['brand_name'] == filters['brand']]
    
    # Apply category filters
    if filters.get('category_main') and filters['category_main'] != 'All':
        filtered_df = filtered_df[filtered_df['category_main'] == filters['category_main']]
    
    if filters.get('category_sub') and filters['category_sub'] != 'All':
        filtered_df = filtered_df[filtered_df['category_sub'] == filters['category_sub']]
    
    # Apply price range filter
    if filters.get('price_range') and 'price_amount' in filtered_df.columns:
        min_price, max_price = filters['price_range']
        filtered_df = filtered_df[
            (filtered_df['price_amount'] >= min_price) & 
            (filtered_df['price_amount'] <= max_price)
        ]
    
    # Apply price point filter
    if filters.get('price_point') and filters['price_point'] != 'All':
        filtered_df = filtered_df[filtered_df['price_point'] == filters['price_point']]
    
    # Apply color filter
    if filters.get('color') and 'All' not in filters['color']:
        filtered_df = filtered_df[filtered_df['color'].isin(filters['color'])]
    
    # Apply availability filter
    if filters.get('availability') and filters['availability'] != 'All':
        filtered_df = filtered_df[filtered_df['availability'] == filters['availability']]
    
    return filtered_df

def create_overview_metrics(df):
    """Create overview metrics"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Products", len(df))
    
    with col2:
        if 'brand_name' in df.columns:
            st.metric("Unique Brands", df['brand_name'].nunique())
    
    with col3:
        if 'price_amount' in df.columns:
            avg_price = df['price_amount'].mean()
            st.metric("Average Price", f"${avg_price:.2f}" if not pd.isna(avg_price) else "N/A")
    
    with col4:
        if 'availability' in df.columns:
            in_stock = len(df[df['availability'].str.contains('in stock', case=False, na=False)])
            st.metric("In Stock", in_stock)

def create_visualizations(df):
    """Create various visualizations"""
    
    # Price Distribution
    if 'price_amount' in df.columns and not df['price_amount'].isna().all():
        st.subheader("💰 Price Distribution")
        col1, col2 = st.columns(2)
        
        with col1:
            fig_hist = px.histogram(
                df, 
                x='price_amount', 
                nbins=20, 
                title="Price Distribution",
                color_discrete_sequence=['#667eea']
            )
            fig_hist.update_layout(showlegend=False)
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            if 'price_point' in df.columns:
                price_point_counts = df['price_point'].value_counts()
                fig_pie = px.pie(
                    values=price_point_counts.values,
                    names=price_point_counts.index,
                    title="Price Point Distribution"
                )
                st.plotly_chart(fig_pie, use_container_width=True)
    
    # Brand Analysis
    if 'brand_name' in df.columns:
        st.subheader("🏷️ Brand Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            brand_counts = df['brand_name'].value_counts().head(10)
            fig_brand = px.bar(
                x=brand_counts.values,
                y=brand_counts.index,
                orientation='h',
                title="Top 10 Brands by Product Count",
                color_discrete_sequence=['#764ba2']
            )
            fig_brand.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_brand, use_container_width=True)
        
        with col2:
            if 'price_amount' in df.columns:
                brand_avg_price = df.groupby('brand_name')['price_amount'].mean().sort_values(ascending=False).head(10)
                fig_brand_price = px.bar(
                    x=brand_avg_price.index,
                    y=brand_avg_price.values,
                    title="Average Price by Brand (Top 10)",
                    color_discrete_sequence=['#667eea']
                )
                fig_brand_price.update_xaxes(tickangle=45)
                st.plotly_chart(fig_brand_price, use_container_width=True)
    
    # Category Analysis
    if 'category_main' in df.columns:
        st.subheader("📂 Category Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            category_counts = df['category_main'].value_counts()
            fig_category = px.pie(
                values=category_counts.values,
                names=category_counts.index,
                title="Product Distribution by Main Category"
            )
            st.plotly_chart(fig_category, use_container_width=True)
        
        with col2:
            if 'category_sub' in df.columns:
                sub_category_counts = df['category_sub'].value_counts().head(10)
                fig_sub_category = px.bar(
                    x=sub_category_counts.values,
                    y=sub_category_counts.index,
                    orientation='h',
                    title="Top 10 Sub-Categories",
                    color_discrete_sequence=['#f093fb']
                )
                st.plotly_chart(fig_sub_category, use_container_width=True)
    
    # Color Analysis
    if 'color' in df.columns:
        st.subheader("🎨 Color Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            color_counts = df['color'].value_counts().head(10)
            fig_color = px.bar(
                x=color_counts.index,
                y=color_counts.values,
                title="Top 10 Colors",
                color_discrete_sequence=['#fa709a']
            )
            fig_color.update_xaxes(tickangle=45)
            st.plotly_chart(fig_color, use_container_width=True)
        
        with col2:
            if 'price_amount' in df.columns:
                color_price = df.groupby('color')['price_amount'].mean().sort_values(ascending=False).head(10)
                fig_color_price = px.bar(
                    x=color_price.index,
                    y=color_price.values,
                    title="Average Price by Color (Top 10)",
                    color_discrete_sequence=['#fee140']
                )
                fig_color_price.update_xaxes(tickangle=45)
                st.plotly_chart(fig_color_price, use_container_width=True)
    
    # Availability Analysis
    if 'availability' in df.columns:
        st.subheader("📦 Availability Analysis")
        availability_counts = df['availability'].value_counts()
        fig_availability = px.bar(
            x=availability_counts.index,
            y=availability_counts.values,
            title="Product Availability Status",
            color_discrete_sequence=['#667eea']
        )
        st.plotly_chart(fig_availability, use_container_width=True)
    
    # Price vs Category Analysis - Multiple Chart Options
    if 'category_main' in df.columns and 'price_point' in df.columns:
        st.subheader("🔥 Category vs Price Point Analysis")
        
        # Let user choose visualization type
        viz_type = st.selectbox(
            "Choose visualization style:",
            ["Grouped Bar Chart", "Stacked Bar Chart", "Sunburst Chart", "Treemap", "Bubble Chart"]
        )
        
        # Prepare data
        category_price_data = pd.crosstab(df['category_main'], df['price_point'])
        
        if viz_type == "Grouped Bar Chart":
            # Grouped bar chart - much clearer than heatmap
            fig = go.Figure()
            colors = ['#667eea', '#764ba2', '#f093fb', '#fa709a', '#fee140']
            
            for i, price_point in enumerate(category_price_data.columns):
                fig.add_trace(go.Bar(
                    name=price_point,
                    x=category_price_data.index,
                    y=category_price_data[price_point],
                    marker_color=colors[i % len(colors)]
                ))
            
            fig.update_layout(
                title="Product Count by Category and Price Point",
                xaxis_title="Category",
                yaxis_title="Number of Products",
                barmode='group',
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
            
        elif viz_type == "Stacked Bar Chart":
            # Stacked bar chart showing proportions
            fig = go.Figure()
            colors = ['#667eea', '#764ba2', '#f093fb', '#fa709a', '#fee140']
            
            for i, price_point in enumerate(category_price_data.columns):
                fig.add_trace(go.Bar(
                    name=price_point,
                    x=category_price_data.index,
                    y=category_price_data[price_point],
                    marker_color=colors[i % len(colors)]
                ))
            
            fig.update_layout(
                title="Product Distribution by Category and Price Point (Stacked)",
                xaxis_title="Category",
                yaxis_title="Number of Products",
                barmode='stack',
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
            
        elif viz_type == "Sunburst Chart":
            # Sunburst chart for hierarchical view
            # Prepare data for sunburst
            sunburst_data = []
            for category in df['category_main'].unique():
                if pd.notna(category):
                    cat_data = df[df['category_main'] == category]
                    for price_point in cat_data['price_point'].unique():
                        if pd.notna(price_point):
                            count = len(cat_data[cat_data['price_point'] == price_point])
                            sunburst_data.append({
                                'ids': f"{category}-{price_point}",
                                'labels': price_point,
                                'parents': category,
                                'values': count
                            })
                    # Add parent category
                    sunburst_data.append({
                        'ids': category,
                        'labels': category,
                        'parents': "",
                        'values': len(cat_data)
                    })
            
            if sunburst_data:
                sunburst_df = pd.DataFrame(sunburst_data)
                fig = go.Figure(go.Sunburst(
                    ids=sunburst_df['ids'],
                    labels=sunburst_df['labels'],
                    parents=sunburst_df['parents'],
                    values=sunburst_df['values'],
                    branchvalues="total",
                ))
                fig.update_layout(
                    title="Category and Price Point Hierarchy",
                    height=600
                )
                st.plotly_chart(fig, use_container_width=True)
                
        elif viz_type == "Treemap":
            # Treemap for proportional visualization
            treemap_data = []
            for category in df['category_main'].unique():
                if pd.notna(category):
                    cat_data = df[df['category_main'] == category]
                    for price_point in cat_data['price_point'].unique():
                        if pd.notna(price_point):
                            count = len(cat_data[cat_data['price_point'] == price_point])
                            treemap_data.append({
                                'category': category,
                                'price_point': price_point,
                                'count': count,
                                'label': f"{category}<br>{price_point}<br>({count} items)"
                            })
            
            if treemap_data:
                treemap_df = pd.DataFrame(treemap_data)
                fig = px.treemap(
                    treemap_df,
                    path=['category', 'price_point'],
                    values='count',
                    title='Category vs Price Point Distribution (Treemap)',
                    color='count',
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(height=600)
                st.plotly_chart(fig, use_container_width=True)
                
        elif viz_type == "Bubble Chart":
            # Bubble chart with category on x-axis, price_point on y-axis, size as count
            bubble_data = []
            for category in df['category_main'].unique():
                if pd.notna(category):
                    cat_data = df[df['category_main'] == category]
                    for price_point in cat_data['price_point'].unique():
                        if pd.notna(price_point):
                            count = len(cat_data[cat_data['price_point'] == price_point])
                            if 'price_amount' in df.columns:
                                avg_price = cat_data[cat_data['price_point'] == price_point]['price_amount'].mean()
                            else:
                                avg_price = 0
                            bubble_data.append({
                                'category': category,
                                'price_point': price_point,
                                'count': count,
                                'avg_price': avg_price
                            })
            
            if bubble_data:
                bubble_df = pd.DataFrame(bubble_data)
                fig = px.scatter(
                    bubble_df,
                    x='category',
                    y='price_point',
                    size='count',
                    color='avg_price' if 'price_amount' in df.columns else 'count',
                    hover_data=['count'],
                    title='Category vs Price Point (Bubble Chart)',
                    color_continuous_scale='Plasma',
                    size_max=60
                )
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)

def create_data_table(df):
    """Create an interactive data table"""
    st.subheader("📊 Detailed Product Data")
    
    # Select columns to display
    display_columns = st.multiselect(
        "Select columns to display:",
        df.columns.tolist(),
        default=['name', 'brand_name', 'category_main', 'price_amount', 'color', 'availability'][:min(6, len(df.columns))]
    )
    
    if display_columns:
        st.dataframe(
            df[display_columns].reset_index(drop=True),
            use_container_width=True,
            height=400
        )
        
        # Download button
        csv = df[display_columns].to_csv(index=False)
        st.download_button(
            label="Download filtered data as CSV",
            data=csv,
            file_name="filtered_fashion_data.csv",
            mime="text/csv"
        )

def main():
    """Main application"""
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>👗 Fashion Product Analytics Dashboard</h1>
        <p>Comprehensive analysis of your fashion product data</p>
    </div>
    """, unsafe_allow_html=True)
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload your CSV file", 
        type=['csv'],
        help="Upload the fashion product CSV file to begin analysis"
    )
    
    if uploaded_file is not None:
        # Load data
        df = load_and_process_data(uploaded_file)
        
        if df is not None:
            st.success(f"Successfully loaded {len(df)} products!")
            
            # Create filters
            filters = create_filters(df)
            
            # Apply filters
            filtered_df = apply_filters(df, filters)
            
            # Show filtered results count
            if len(filtered_df) != len(df):
                st.info(f"Showing {len(filtered_df)} products after applying filters")
            
            # Overview metrics
            st.header("📈 Overview")
            create_overview_metrics(filtered_df)
            
            # Visualizations
            st.header("📊 Analytics")
            if len(filtered_df) > 0:
                create_visualizations(filtered_df)
            else:
                st.warning("No data available with current filters. Please adjust your filters.")
            
            # Data table
            create_data_table(filtered_df)
            
    else:
        st.info("👆 Please upload your fashion product CSV file to start the analysis")
        
        # Show expected data structure
        st.subheader("📋 Expected Data Structure")
        st.write("Your CSV should contain columns like:")
        expected_columns = [
            "name", "brand_name", "category_main", "category_sub", 
            "price_amount", "color", "availability", "price_point"
        ]
        st.write(", ".join(expected_columns))

if __name__ == "__main__":
    main()