import streamlit as st
import folium
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from folium import Marker
from folium.plugins import MarkerCluster, HeatMap
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import base64

# 设置页面配置
st.set_page_config(
    page_title="智慧植保 - 农业病虫害智能防控平台",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------
# 数据生成函数（共享）
# --------------------------

# 设置随机种子以确保数据可重现
random.seed(42)
np.random.seed(42)

# 鲁山县主要乡镇及经纬度
lushan_towns = {
    "鲁阳镇": (33.74, 112.82),
    "下汤镇": (33.60, 112.75),
    "梁洼镇": (33.78, 112.93),
    "张官营镇": (33.68, 113.05),
    "尧山镇": (33.50, 112.58),
    "瓦屋镇": (33.70, 112.65),
    "赵村镇": (33.62, 112.60),
    "四棵树乡": (33.55, 112.68)
}

# 水果类型与对应常见病虫害及经济价值
fruit_diseases = {
    "桃": ["褐腐病", "蚜虫", "桃小食心虫"],
    "苹果": ["炭疽病", "红蜘蛛", "白粉病"],
    "葡萄": ["霜霉病", "灰霉病", "透翅蛾"],
    "梨": ["黑星病", "梨木虱", "蚜虫"]
}

# 水果经济价值（元/公斤）
fruit_economic_value = {
    "桃": 8.5,
    "苹果": 6.2,
    "葡萄": 12.8,
    "梨": 5.6
}

# 解决方案数据库
solution_db = {
    "褐腐病": {
        "症状": "果实出现褐色腐烂，表面有灰色霉层",
        "防治经验": "1. 冬季清园，烧毁病果；2. 花期喷50%多菌灵500倍液；3. 果实成熟期套袋（鲁阳镇果农实测有效）",
        "AI推荐方案": "基于历史数据分析，建议在3-4月花期前进行预防性施药，效果提升35%",
        "防治成本": "中等（200-300元/亩）",
        "效果评估": "85%有效率",
        "投资回报率": "3.2:1",
        "环保等级": "⭐️⭐️⭐️☆"
    },
    "蚜虫": {
        "症状": "叶片卷曲，虫体聚集在叶背",
        "防治经验": "1. 挂黄板诱杀；2. 释放天敌瓢虫；3. 蚜虫爆发期用10%吡虫啉2000倍液（下汤镇桃园推荐）",
        "AI推荐方案": "智能监测+生物防治组合，减少化学农药使用40%",
        "防治成本": "低（100-150元/亩）",
        "效果评估": "92%有效率",
        "投资回报率": "4.5:1",
        "环保等级": "⭐️⭐️⭐️⭐️"
    },
    "桃小食心虫": {
        "症状": "果实表面有针孔，果肉内有虫道",
        "防治经验": "1. 地面覆盖地膜阻止成虫出土；2. 性诱剂诱杀雄虫；3. 卵期喷20%氯虫苯甲酰胺（张官营镇经验）",
        "AI推荐方案": "性信息素迷向技术+精准施药时机预测",
        "防治成本": "中等偏高（300-400元/亩）",
        "效果评估": "88%有效率",
        "投资回报率": "2.8:1",
        "环保等级": "⭐️⭐️⭐️⭐️☆"
    },
    "炭疽病": {
        "症状": "果实出现褐色凹陷斑，有轮纹状小黑点",
        "防治经验": "1. 及时摘除病果；2. 雨季前喷70%甲基托布津800倍液；3. 增施有机肥提高抗性（尧山镇苹果园）",
        "AI推荐方案": "基于气象数据的预警系统，提前7天预警防控",
        "防治成本": "中等（180-250元/亩）",
        "效果评估": "90%有效率",
        "投资回报率": "3.5:1",
        "环保等级": "⭐️⭐️⭐️☆"
    },
    "霜霉病": {
        "症状": "叶片背面有白色霉层，正面发黄",
        "防治经验": "1. 合理修剪保证通风；2. 发病初期喷58%甲霜灵锰锌500倍液；3. 避免傍晚浇水（瓦屋镇葡萄园）",
        "AI推荐方案": "微气候监测+精准施药，降低用药量30%",
        "防治成本": "中等（220-280元/亩）",
        "效果评估": "87%有效率",
        "投资回报率": "3.0:1",
        "环保等级": "⭐️⭐️⭐️⭐️"
    },
}

@st.cache_data(ttl=3600)  # 缓存1小时
def generate_simulated_data():
    data = []
    dates = [datetime(2024, 1, 1) + timedelta(days=30*i) for i in range(12)]
    
    for town, (lat, lon) in lushan_towns.items():
        fruits = random.sample(list(fruit_diseases.keys()), k=random.randint(2, 3))
        for fruit in fruits:
            diseases = random.sample(fruit_diseases[fruit], k=random.randint(1, 2))
            for disease in diseases:
                for date in dates:
                    base_freq = random.randint(1, 10)
                    base_severity = random.randint(1, 5)
                    
                    seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * date.month / 12)
                    freq = max(1, int(base_freq * seasonal_factor))
                    severity = max(1, min(5, int(base_severity * seasonal_factor)))
                    
                    area_affected = random.uniform(0.1, 0.3)
                    yield_loss = severity * 0.05 + random.uniform(0.05, 0.15)
                    economic_loss = area_affected * yield_loss * fruit_economic_value[fruit] * 10000
                    
                    data.append({
                        "日期": date,
                        "月份": date.month,
                        "乡镇": town,
                        "纬度": lat + random.uniform(-0.03, 0.03),
                        "经度": lon + random.uniform(-0.03, 0.03),
                        "水果类型": fruit,
                        "病虫害类型": disease,
                        "月均发生频次": freq,
                        "严重程度": severity,
                        "经济损失(元)": economic_loss,
                        "防治成本(元)": economic_loss * random.uniform(0.1, 0.3)
                    })
    return pd.DataFrame(data)

# 生成模拟数据
df = generate_simulated_data()

# --------------------------
# 版本选择侧边栏
# --------------------------

st.sidebar.markdown("## 🌱 智慧植保平台")
version = st.sidebar.selectbox(
    "选择版本",
    ["基础版 (免费)", "专业版 (199元/月)", "企业版 (999元/月)"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 数据筛选")

# 根据版本限制筛选选项
if "基础版" in version:
    max_towns = 3
    max_fruits = 2
    max_diseases = 2
    months_options = [3, 4, 5, 6]  # 只显示春季月份
elif "专业版" in version:
    max_towns = 6
    max_fruits = 3
    max_diseases = 3
    months_options = sorted(df["月份"].unique())
else:  # 企业版
    max_towns = len(lushan_towns)
    max_fruits = len(fruit_diseases)
    max_diseases = len(solution_db)
    months_options = sorted(df["月份"].unique())

# 筛选条件
selected_months = st.sidebar.multiselect(
    "选择月份",
    options=months_options,
    default=months_options[:2] if months_options else []
)

available_towns = list(lushan_towns.keys())[:max_towns]
selected_towns = st.sidebar.multiselect(
    "选择乡镇",
    options=available_towns,
    default=available_towns[:2] if available_towns else []
)

available_fruits = list(fruit_diseases.keys())[:max_fruits]
selected_fruits = st.sidebar.multiselect(
    "选择水果类型",
    options=available_fruits,
    default=available_fruits[:1] if available_fruits else []
)

# 根据选择的水果类型确定可选的病虫害
available_diseases = []
for fruit in selected_fruits:
    available_diseases.extend(fruit_diseases.get(fruit, []))
available_diseases = list(set(available_diseases))[:max_diseases]

selected_diseases = st.sidebar.multiselect(
    "选择病虫害类型",
    options=available_diseases,
    default=available_diseases[:1] if available_diseases else []
)

# 根据筛选条件过滤数据
filtered_df = df[
    (df["月份"].isin(selected_months)) &
    (df["乡镇"].isin(selected_towns)) &
    (df["水果类型"].isin(selected_fruits)) &
    (df["病虫害类型"].isin(selected_diseases))
]

# --------------------------
# 通用函数
# --------------------------

def create_basic_map(filtered_df):
    """创建基础地图"""
    lushan_center = (33.64, 112.81)
    m = folium.Map(location=lushan_center, zoom_start=10, tiles="CartoDB positron")
    
    disease_colors = {
        "褐腐病": "red", "蚜虫": "green", "桃小食心虫": "purple",
        "炭疽病": "orange", "红蜘蛛": "blue", "白粉病": "pink",
        "霜霉病": "cadetblue", "灰霉病": "beige", "透翅蛾": "black",
        "黑星病": "darkred", "梨木虱": "darkgreen"
    }
    
    marker_cluster = MarkerCluster().add_to(m)
    for idx, row in filtered_df.iterrows():
        disease = row["病虫害类型"]
        solution = solution_db.get(disease, {
            "症状": "暂无数据", 
            "防治经验": "暂无本地经验",
            "AI推荐方案": "数据收集中",
            "防治成本": "待评估",
            "效果评估": "待评估",
            "投资回报率": "待计算",
            "环保等级": "待评估"
        })
        
        popup_content = f"""
        <div style="width: 250px;">
            <h4 style="color: #2E8B57; margin-bottom: 5px;">{row['乡镇']} - {disease}</h4>
            <p><strong>水果类型</strong>: {row['水果类型']}<br>
            <strong>严重程度</strong>: {'★'*row['严重程度']}<br>
            <strong>月均频次</strong>: {row['月均发生频次']}次</p>
        </div>
        """
        
        Marker(
            location=[row["纬度"], row["经度"]],
            popup=folium.Popup(popup_content, max_width=300),
            icon=folium.Icon(color=disease_colors.get(disease, "gray"), icon="leaf")
        ).add_to(marker_cluster)
    
    return m

def create_advanced_map(filtered_df):
    """创建高级地图（含热力图）"""
    m = create_basic_map(filtered_df)
    
    # 添加热力图
    heat_data = [[row["纬度"], row["经度"], row["严重程度"]] for idx, row in filtered_df.iterrows()]
    if heat_data:
        HeatMap(heat_data, radius=15, blur=10, gradient={0.4: 'blue', 0.65: 'lime', 1: 'red'}).add_to(m)
    
    return m

def display_kpi_metrics(filtered_df, version_level):
    """显示KPI指标"""
    if not filtered_df.empty:
        total_loss = filtered_df["经济损失(元)"].sum()
        total_cost = filtered_df["防治成本(元)"].sum()
        avg_severity = filtered_df["严重程度"].mean()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="预估总经济损失",
                value=f"¥{total_loss:,.0f}",
                delta=f"-{(total_cost/total_loss*100):.1f}% 通过防治可挽回" if total_loss > 0 else "0%"
            )
        
        with col2:
            st.metric(
                label="预估防治总成本",
                value=f"¥{total_cost:,.0f}",
                delta=f"ROI: {(total_loss/total_cost):.1f}:1" if total_cost > 0 else "N/A"
            )
        
        with col3:
            st.metric(
                label="平均病虫害严重程度",
                value=f"{avg_severity:.1f}/5.0",
                delta=f"-{(1 - avg_severity/5)*100:.1f}% 相比最严重情况"
            )
        
        with col4:
            affected_towns = filtered_df["乡镇"].nunique()
            if version_level == "basic":
                st.metric(
                    label="受影响乡镇数量",
                    value=affected_towns
                )
            else:
                st.metric(
                    label="受影响乡镇数量",
                    value=affected_towns,
                    delta=f"{len(selected_towns) - affected_towns}个乡镇未受影响"
                )

# --------------------------
# 基础版页面
# --------------------------

def render_basic_version():
    st.markdown("""
    <div style="text-align: center; background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%); padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <h1 style="color: #2E8B57; font-size: 2.2rem; margin-bottom: 0.5rem;">🌱 智慧植保 · 基础版</h1>
        <h2 style="color: #388E3C; font-size: 1.5rem; margin-top: 0;">免费基础服务 · 助力小农户</h2>
        <p style="color: #666; font-size: 1rem;">适用于个体农户和小型果园的基础病虫害监测服务</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 功能限制提示
    st.info("""
    💡 **基础版功能限制**：
    - 仅显示3个乡镇数据
    - 仅支持2种水果类型
    - 仅显示春季月份数据
    - 基础地图查看功能
    - 如需更多功能，请升级到专业版或企业版
    """)
    
    # KPI指标
    st.subheader("📊 基础数据概览")
    display_kpi_metrics(filtered_df, "basic")
    
    # 地图展示
    st.subheader("🗺️ 病虫害分布地图")
    if not filtered_df.empty:
        m = create_basic_map(filtered_df)
        st_folium(m, width=800, height=400, returned_objects=[])
    else:
        st.warning("请选择筛选条件查看数据")
    
    # 基础数据表格
    st.subheader("📋 病虫害数据明细")
    if not filtered_df.empty:
        display_cols = ["乡镇", "水果类型", "病虫害类型", "月均发生频次", "严重程度"]
        st.dataframe(filtered_df[display_cols].head(50), use_container_width=True)
    else:
        st.warning("当前筛选条件下没有数据")
    
    # 升级提示
    st.markdown("---")
    st.markdown("""
    <div style="background-color: #fff3cd; padding: 15px; border-radius: 10px; border-left: 5px solid #ffc107;">
        <h4 style="color: #856404; margin-top: 0;">🚀 想要更多功能？</h4>
        <p style="color: #856404; margin-bottom: 0;">
            升级到<strong>专业版</strong>可获得AI智能推荐、趋势分析、经济分析等高级功能！
            或选择<strong>企业版</strong>获得完整数据访问权限和定制化服务。
        </p>
    </div>
    """, unsafe_allow_html=True)

# --------------------------
# 专业版页面
# --------------------------

def render_pro_version():
    st.markdown("""
    <div style="text-align: center; background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <h1 style="color: #1976D2; font-size: 2.2rem; margin-bottom: 0.5rem;">🔬 智慧植保 · 专业版</h1>
        <h2 style="color: #1565C0; font-size: 1.5rem; margin-top: 0;">AI智能分析 · 精准防控决策</h2>
        <p style="color: #666; font-size: 1rem;">适用于中型农场和专业合作社的智能决策支持系统</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 专业版功能特色
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("AI智能推荐", "✓ 已启用", "精准防控方案")
    with col2:
        st.metric("趋势分析", "✓ 已启用", "历史数据预测")
    with col3:
        st.metric("经济分析", "✓ 已启用", "成本效益评估")
    
    # KPI指标
    st.subheader("📊 核心业务指标")
    display_kpi_metrics(filtered_df, "pro")
    
    # 创建选项卡
    tab1, tab2, tab3 = st.tabs(["🗺️ 智能地图", "📈 趋势分析", "🤖 AI推荐"])
    
    with tab1:
        st.subheader("病虫害分布热力图")
        if not filtered_df.empty:
            m = create_advanced_map(filtered_df)
            st_folium(m, width=800, height=400, returned_objects=[])
        else:
            st.warning("请选择筛选条件查看数据")
    
    with tab2:
        st.subheader("病虫害趋势分析")
        if not filtered_df.empty:
            # 月度趋势分析
            monthly_trend = filtered_df.groupby("月份").agg({
                "月均发生频次": "mean",
                "严重程度": "mean",
                "经济损失(元)": "sum"
            }).reset_index()
            
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('病虫害发生趋势', '经济损失趋势'),
                vertical_spacing=0.1
            )
            
            fig.add_trace(
                go.Scatter(x=monthly_trend["月份"], y=monthly_trend["月均发生频次"], 
                          name="发生频次", line=dict(color='red'), mode='lines+markers'),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(x=monthly_trend["月份"], y=monthly_trend["严重程度"], 
                          name="严重程度", line=dict(color='orange'), mode='lines+markers'),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Bar(x=monthly_trend["月份"], y=monthly_trend["经济损失(元)"], 
                       name="经济损失", marker_color='green'),
                row=2, col=1
            )
            
            fig.update_layout(height=500, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("请选择筛选条件查看数据")
    
    with tab3:
        st.subheader("AI智能防治推荐")
        if not filtered_df.empty:
            # 找出最严重的病虫害问题
            top_issues = filtered_df.groupby("病虫害类型").agg({
                "严重程度": "mean",
                "月均发生频次": "mean",
                "经济损失(元)": "sum"
            }).reset_index()
            
            top_issues["综合指数"] = (
                top_issues["严重程度"] * 0.4 + 
                top_issues["月均发生频次"] * 0.3 + 
                (top_issues["经济损失(元)"] / top_issues["经济损失(元)"].max()) * 0.3
            )
            
            top_issues = top_issues.sort_values("综合指数", ascending=False).head(2)
            
            for idx, row in top_issues.iterrows():
                disease = row["病虫害类型"]
                solution = solution_db.get(disease, {})
                
                with st.expander(f"🔴 {disease} - 综合威胁指数: {row['综合指数']:.2f}", expanded=True):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"""
                        **📊 问题严重性分析:**
                        - 平均严重程度: {row['严重程度']:.1f}/5.0
                        - 月均发生频次: {row['月均发生频次']:.1f}次
                        - 预估经济损失: ¥{row['经济损失(元)']:,.0f}
                        
                        **🤖 AI智能推荐方案:**
                        {solution.get('AI推荐方案', '数据收集中')}
                        """)
                    
                    with col2:
                        st.markdown(f"""
                        **💰 经济指标:**
                        - 防治成本: {solution.get('防治成本', '待评估')}
                        - 投资回报率: {solution.get('投资回报率', '待计算')}
                        - 防治效果: {solution.get('效果评估', '待评估')}
                        """)
        else:
            st.warning("请选择筛选条件查看数据")
    
    # 升级到企业版提示
    st.markdown("---")
    st.markdown("""
    <div style="background-color: #e8f5e8; padding: 15px; border-radius: 10px; border-left: 5px solid #4caf50;">
        <h4 style="color: #2e7d32; margin-top: 0;">🏢 需要更强大的功能？</h4>
        <p style="color: #2e7d32; margin-bottom: 0;">
            升级到<strong>企业版</strong>可获得完整数据访问、定制报告、数据导出、API接口等高级功能！
            适合大型农业企业和政府机构使用。
        </p>
    </div>
    """, unsafe_allow_html=True)

# --------------------------
# 企业版页面
# --------------------------

def render_enterprise_version():
    st.markdown("""
    <div style="text-align: center; background: linear-gradient(135deg, #fce4ec 0%, #f8bbd9 100%); padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <h1 style="color: #C2185B; font-size: 2.2rem; margin-bottom: 0.5rem;">🏢 智慧植保 · 企业版</h1>
        <h2 style="color: #AD1457; font-size: 1.5rem; margin-top: 0;">全方位解决方案 · 定制化服务</h2>
        <p style="color: #666; font-size: 1rem;">适用于大型农业企业、政府机构和科研单位的全方位解决方案</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 企业版功能特色
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("完整数据访问", "✓ 已启用", "无限制访问")
    with col2:
        st.metric("定制报告", "✓ 已启用", "个性化分析")
    with col3:
        st.metric("数据导出", "✓ 已启用", "多种格式")
    with col4:
        st.metric("API接口", "✓ 已启用", "系统集成")
    
    # 高级KPI指标
    st.subheader("📊 高级业务指标")
    if not filtered_df.empty:
        total_loss = filtered_df["经济损失(元)"].sum()
        total_cost = filtered_df["防治成本(元)"].sum()
        roi = total_loss / total_cost if total_cost > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "总经济损失",
                f"¥{total_loss:,.0f}",
                "需重点防控"
            )
        
        with col2:
            st.metric(
                "防治总成本",
                f"¥{total_cost:,.0f}",
                f"ROI: {roi:.1f}:1"
            )
        
        with col3:
            prevention_potential = total_loss - total_cost
            st.metric(
                "防治潜在收益",
                f"¥{prevention_potential:,.0f}",
                "通过有效防治"
            )
        
        with col4:
            efficiency_ratio = (total_loss - total_cost) / total_loss * 100 if total_loss > 0 else 0
            st.metric(
                "防治效率",
                f"{efficiency_ratio:.1f}%",
                "投入产出比"
            )
    
    # 企业版专属功能选项卡
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🗺️ 高级地图", "📈 深度分析", "🤖 智能决策", "📊 数据管理", "📋 定制报告"])
    
    with tab1:
        st.subheader("高级可视化分析")
        if not filtered_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # 热力图
                m = create_advanced_map(filtered_df)
                st_folium(m, width=400, height=400, returned_objects=[])
            
            with col2:
                # 乡镇对比分析
                town_analysis = filtered_df.groupby("乡镇").agg({
                    "严重程度": "mean",
                    "经济损失(元)": "sum"
                }).reset_index()
                
                fig = px.bar(town_analysis, x="乡镇", y="经济损失(元)", 
                            title="各乡镇经济损失对比",
                            color="严重程度", color_continuous_scale="RdYlGn_r")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("请选择筛选条件查看数据")
    
    with tab2:
        st.subheader("深度数据分析")
        if not filtered_df.empty:
            # 多维度分析
            col1, col2 = st.columns(2)
            
            with col1:
                # 成本效益分析
                cost_benefit_data = []
                for disease in filtered_df["病虫害类型"].unique():
                    disease_data = filtered_df[filtered_df["病虫害类型"] == disease]
                    total_loss = disease_data["经济损失(元)"].sum()
                    total_cost = disease_data["防治成本(元)"].sum()
                    solution = solution_db.get(disease, {})
                    
                    cost_benefit_data.append({
                        "病虫害类型": disease,
                        "经济损失": total_loss,
                        "防治成本": total_cost,
                        "投资回报率": total_loss / total_cost if total_cost > 0 else 0,
                        "防治效果": solution.get("效果评估", "待评估")
                    })
                
                cost_benefit_df = pd.DataFrame(cost_benefit_data)
                fig = px.scatter(cost_benefit_df, x="防治成本", y="经济损失", 
                               size="投资回报率", color="病虫害类型",
                               title="成本效益分析气泡图",
                               hover_data=["防治效果"])
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # 时间序列预测
                monthly_data = filtered_df.groupby("月份").agg({
                    "严重程度": "mean",
                    "经济损失(元)": "sum"
                }).reset_index()
                
                # 简单线性预测（模拟）
                if len(monthly_data) > 1:
                    future_months = list(range(1, 13))
                    severity_trend = np.poly1d(np.polyfit(monthly_data["月份"], monthly_data["严重程度"], 1))
                    predicted_severity = severity_trend(future_months)
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=monthly_data["月份"], y=monthly_data["严重程度"], 
                                           mode='markers', name='历史数据', line=dict(color='blue')))
                    fig.add_trace(go.Scatter(x=future_months, y=predicted_severity, 
                                           mode='lines', name='预测趋势', line=dict(color='red', dash='dash')))
                    fig.update_layout(title="病虫害严重程度趋势预测", xaxis_title="月份", yaxis_title="严重程度")
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("请选择筛选条件查看数据")
    
    with tab3:
        st.subheader("AI智能决策支持")
        if not filtered_df.empty:
            # 高级AI推荐
            top_issues = filtered_df.groupby("病虫害类型").agg({
                "严重程度": "mean",
                "月均发生频次": "mean",
                "经济损失(元)": "sum",
                "防治成本(元)": "sum"
            }).reset_index()
            
            top_issues["综合威胁指数"] = (
                top_issues["严重程度"] * 0.3 + 
                top_issues["月均发生频次"] * 0.2 + 
                (top_issues["经济损失(元)"] / top_issues["经济损失(元)"].max()) * 0.3 +
                (top_issues["防治成本(元)"] / top_issues["防治成本(元)"].max()) * 0.2
            )
            
            top_issues = top_issues.sort_values("综合威胁指数", ascending=False)
            
            for idx, row in top_issues.iterrows():
                disease = row["病虫害类型"]
                solution = solution_db.get(disease, {})
                
                with st.expander(f"🔴 {disease} - 威胁等级: {'高危' if row['综合威胁指数'] > 0.7 else '中危' if row['综合威胁指数'] > 0.4 else '低危'}", expanded=idx==0):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown("""
                        **📈 威胁分析**
                        """)
                        st.metric("严重程度", f"{row['严重程度']:.1f}/5.0")
                        st.metric("发生频次", f"{row['月均发生频次']:.1f}次/月")
                    
                    with col2:
                        st.markdown("""
                        **💰 经济影响**
                        """)
                        st.metric("经济损失", f"¥{row['经济损失(元)']:,.0f}")
                        st.metric("防治成本", f"¥{row['防治成本(元)']:,.0f}")
                    
                    with col3:
                        st.markdown("""
                        **🎯 AI推荐**
                        """)
                        st.info(solution.get('AI推荐方案', '数据收集中'))
                        st.metric("投资回报率", solution.get('投资回报率', '待计算'))
                    
                    # 行动建议
                    st.markdown("**💡 行动建议:**")
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        if st.button(f"📞 紧急专家会诊", key=f"expert_{disease}"):
                            st.success(f"已启动{disease}紧急专家会诊流程!")
                    with col_b:
                        if st.button(f"🛒 批量采购物资", key=f"bulk_{disease}"):
                            st.info(f"跳转到{disease}防治物资批量采购页面")
                    with col_c:
                        if st.button(f"📋 生成防治方案", key=f"plan_{disease}"):
                            st.info(f"生成{disease}定制化综合防治方案")
        else:
            st.warning("请选择筛选条件查看数据")
    
    with tab4:
        st.subheader("数据管理功能")
        if not filtered_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📥 数据导出**")
                export_format = st.selectbox("选择导出格式", ["CSV", "Excel", "JSON"])
                
                if st.button("生成导出文件"):
                    if export_format == "CSV":
                        csv = filtered_df.to_csv(index=False)
                        st.download_button(
                            label="下载CSV文件",
                            data=csv,
                            file_name=f"病虫害数据_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
                    elif export_format == "Excel":
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            filtered_df.to_excel(writer, index=False, sheet_name='病虫害数据')
                        st.download_button(
                            label="下载Excel文件",
                            data=output.getvalue(),
                            file_name=f"病虫害数据_{datetime.now().strftime('%Y%m%d')}.xlsx",
                            mime="application/vnd.ms-excel"
                        )
            
            with col2:
                st.markdown("**🔗 API接口**")
                st.code("""
# 企业版API接口示例
import requests

api_key = "your_enterprise_api_key"
url = "https://api.smartplantcare.com/v1/diseases"

headers = {"Authorization": f"Bearer {api_key}"}
params = {
    "town": "鲁阳镇",
    "fruit": "桃",
    "start_date": "2024-01-01",
    "end_date": "2024-06-30"
}

response = requests.get(url, headers=headers, params=params)
data = response.json()
                """)
                
                if st.button("生成API密钥"):
                    st.success("API密钥已生成: sk_ent_xxxxxxxxxxxxxxxx")
        else:
            st.warning("请选择筛选条件查看数据")
    
    with tab5:
        st.subheader("定制报告生成")
        if not filtered_df.empty:
            report_type = st.selectbox("选择报告类型", 
                                     ["月度分析报告", "季度总结报告", "年度综合报告", "专项防治报告"])
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**报告内容定制**")
                include_trend = st.checkbox("包含趋势分析", value=True)
                include_economic = st.checkbox("包含经济分析", value=True)
                include_recommendations = st.checkbox("包含防治建议", value=True)
                include_comparison = st.checkbox("包含区域对比", value=True)
            
            with col2:
                st.markdown("**报告格式设置**")
                report_style = st.selectbox("报告风格", ["简洁版", "详细版", "学术版", "商业版"])
                include_charts = st.checkbox("包含图表", value=True)
                include_data = st.checkbox("包含原始数据", value=False)
            
            if st.button("🖨️ 生成定制报告"):
                with st.spinner("正在生成定制报告..."):
                    # 模拟报告生成过程
                    progress_bar = st.progress(0)
                    for i in range(100):
                        progress_bar.progress(i + 1)
                    
                    st.success("✅ 定制报告生成完成！")
                    
                    # 模拟报告内容预览
                    st.markdown(f"""
                    ### 📋 {report_type} - 预览
                    
                    **报告摘要**:
                    - 分析时段: {selected_months}月
                    - 覆盖区域: {', '.join(selected_towns)}
                    - 主要作物: {', '.join(selected_fruits)}
                    - 重点关注病虫害: {', '.join(selected_diseases)}
                    
                    **核心发现**:
                    1. 预计总经济损失: ¥{filtered_df['经济损失(元)'].sum():,.0f}
                    2. 平均病虫害严重程度: {filtered_df['严重程度'].mean():.1f}/5.0
                    3. 防治投资回报率: {(filtered_df['经济损失(元)'].sum() / filtered_df['防治成本(元)'].sum()):.1f}:1
                    
                    **主要建议**:
                    - 优先防治: {selected_diseases[0] if selected_diseases else 'N/A'}
                    - 重点区域: {selected_towns[0] if selected_towns else 'N/A'}
                    - 最佳防治时机: 建议在{min(selected_months) if selected_months else 'N/A'}月前完成防治准备
                    """)
                    
                    # 创建模拟PDF下载
                    report_content = f"""
                    {report_type}
                    生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    
                    报告摘要:
                    - 分析时段: {selected_months}月
                    - 覆盖区域: {', '.join(selected_towns)}
                    - 主要作物: {', '.join(selected_fruits)}
                    - 重点关注病虫害: {', '.join(selected_diseases)}
                    
                    核心发现:
                    1. 预计总经济损失: ¥{filtered_df['经济损失(元)'].sum():,.0f}
                    2. 平均病虫害严重程度: {filtered_df['严重程度'].mean():.1f}/5.0
                    3. 防治投资回报率: {(filtered_df['经济损失(元)'].sum() / filtered_df['防治成本(元)'].sum()):.1f}:1
                    """
                    
                    b64 = base64.b64encode(report_content.encode()).decode()
                    st.download_button(
                        label="📥 下载完整报告 (PDF)",
                        data=f"data:application/pdf;base64,{b64}",
                        file_name=f"{report_type}_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf"
                    )
        else:
            st.warning("请选择筛选条件查看数据")
    
    # 企业版专属服务
    st.markdown("---")
    st.markdown("""
    <div style="background-color: #f3e5f5; padding: 20px; border-radius: 10px;">
        <h4 style="color: #7b1fa2; margin-top: 0;">🏆 企业版专属服务</h4>
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px;">
            <div>
                <h5 style="color: #7b1fa2;">🔧 技术支持</h5>
                <ul style="color: #7b1fa2;">
                    <li>专属客户经理</li>
                    <li>7×24小时技术支持</li>
                    <li>定期系统优化</li>
                </ul>
            </div>
            <div>
                <h5 style="color: #7b1fa2;">📈 增值服务</h5>
                <ul style="color: #7b1fa2;">
                    <li>定制化算法开发</li>
                    <li>深度数据挖掘</li>
                    <li>竞争对手分析</li>
                </ul>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --------------------------
# 主程序逻辑
# --------------------------

def main():
    # 根据选择的版本渲染对应页面
    if "基础版" in version:
        render_basic_version()
    elif "专业版" in version:
        render_pro_version()
    else:  # 企业版
        render_enterprise_version()
    
    # 底部信息
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>🌱 智慧植保平台 · 助力农业现代化发展 · 联系电话: 400-123-4567</p>
        <p>© 2024 智慧植保团队 · 挑战杯大学生创新创业大赛参赛项目</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
[file content end]
