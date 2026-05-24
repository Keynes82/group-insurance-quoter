"""Streamlit 前端主程序"""
import streamlit as st
import requests
import json
from datetime import datetime

# API 基础 URL
API_BASE = "http://localhost:8000"

# 页面配置
st.set_page_config(
    page_title="团险报价助手",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .result-box {
        background-color: #f0f8ff;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #1f77b4;
        margin: 1rem 0;
    }
    .risk-high { color: #d62728; font-weight: bold; }
    .risk-medium { color: #ff7f0e; font-weight: bold; }
    .risk-low { color: #2ca02c; font-weight: bold; }
</style>
""", unsafe_allow_html=True)


def check_api():
    """检查 API 是否可用"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


# 侧边栏
with st.sidebar:
    st.title("🏢 团险报价助手")
    st.markdown("---")
    
    # API 状态
    api_ok = check_api()
    if api_ok:
        st.success("✅ API 连接正常")
    else:
        st.error("❌ API 未连接")
        st.info("请运行: `uvicorn src.api.main:app --reload`")
    
    st.markdown("---")
    st.markdown("### 导航")
    page = st.radio(
        "选择功能",
        ["🧮 保费计算", "📋 方案模板", "📜 报价历史", "⚙️ 系统设置"]
    )


# 主内容区
st.markdown('<div class="main-header">团险报价助手</div>', unsafe_allow_html=True)

if page == "🧮 保费计算":
    st.subheader("企业客户信息")
    
    col1, col2 = st.columns(2)
    
    with col1:
        company_name = st.text_input("企业名称", placeholder="请输入企业全称")
        industry = st.selectbox(
            "所属行业",
            ["制造业", "IT互联网", "零售贸易", "建筑工程", "物流运输", 
             "金融服务", "教育培训", "医疗健康"]
        )
    
    with col2:
        employee_count = st.number_input("员工人数", min_value=1, max_value=10000, value=50)
        average_age = st.slider("平均年龄", min_value=18, max_value=65, value=35)
    
    st.markdown("---")
    st.subheader("投保信息")
    
    col3, col4 = st.columns(2)
    
    with col3:
        insurance_type = st.selectbox(
            "投保险种",
            ["团体意外险", "团体定期寿险", "团体健康险", "雇主责任险", "团体年金险"]
        )
    
    with col4:
        coverage_amount = st.number_input(
            "保额（万元）", 
            min_value=1, 
            max_value=1000, 
            value=50
        )
    
    # 加载模板
    if api_ok:
        try:
            templates_resp = requests.get(f"{API_BASE}/templates/")
            if templates_resp.status_code == 200:
                templates = templates_resp.json()
                industry_templates = [t for t in templates if t["industry"] == industry]
                if industry_templates:
                    st.markdown("---")
                    st.subheader("📋 推荐方案模板")
                    for t in industry_templates[:2]:
                        with st.expander(f"{t['name']} - {t['default_coverage']}万元"):
                            st.write(t.get("description", ""))
                            if st.button(f"应用模板: {t['name']}", key=f"tpl_{t['id']}"):
                                st.session_state["template_coverage"] = t["default_coverage"]
                                st.session_state["template_type"] = t["default_insurance_type"]
                                st.rerun()
        except Exception as e:
            pass
    
    st.markdown("---")
    
    col5, col6 = st.columns([1, 1])
    
    with col5:
        calculate_btn = st.button("🧮 计算保费", type="primary", use_container_width=True)
    
    with col6:
        save_btn = st.button("💾 保存报价", type="secondary", use_container_width=True)
    
    if calculate_btn or save_btn:
        if not company_name:
            st.warning("请输入企业名称")
        elif not api_ok:
            st.error("API 服务未启动，无法计算保费")
        else:
            # 准备请求数据
            payload = {
                "client": {
                    "company_name": company_name,
                    "industry": industry,
                    "employee_count": employee_count,
                    "average_age": average_age,
                },
                "insurance_type": insurance_type,
                "coverage_amount": coverage_amount,
            }
            
            try:
                if calculate_btn:
                    response = requests.post(f"{API_BASE}/quotations/calculate", json=payload)
                else:
                    response = requests.post(f"{API_BASE}/quotations/save", json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # 显示结果
                    st.markdown("---")
                    st.subheader("📊 报价结果")
                    
                    result_col1, result_col2, result_col3 = st.columns(3)
                    
                    with result_col1:
                        st.metric("人均保费", f"¥{result['per_capita_premium']:,.2f}")
                    
                    with result_col2:
                        st.metric("总保费", f"¥{result['total_premium']:,.2f}")
                    
                    with result_col3:
                        risk_level = result["risk_level"]
                        risk_color = {
                            "low": "🟢 低风险",
                            "medium": "🟡 中风险",
                            "high": "🔴 高风险",
                        }.get(risk_level, risk_level)
                        st.metric("风控评级", risk_color)
                    
                    # 风控建议
                    st.markdown("---")
                    st.subheader("⚠️ 风控建议")
                    st.info(result["risk_notes"])
                    
                    # 保费明细
                    with st.expander("查看保费计算明细"):
                        breakdown = result["breakdown"]
                        st.write(f"- 基础费率: {breakdown['base_rate']}元/万元保额")
                        st.write(f"- 行业系数: {breakdown['industry_factor']}")
                        st.write(f"- 年龄系数: {breakdown['age_factor']}")
                        st.write(f"- 人数折扣: {breakdown['count_discount']}")
                        st.write(f"- 保额: {breakdown['coverage_amount']}万元")
                        st.write(f"- 员工人数: {breakdown['employee_count']}人")
                    
                    if save_btn and "id" in result:
                        st.success(f"✅ 报价已保存（ID: {result['id']}）")
                    
                else:
                    st.error(f"计算失败: {response.text}")
            
            except Exception as e:
                st.error(f"请求出错: {str(e)}")


elif page == "📋 方案模板":
    st.subheader("📋 方案模板库")
    
    if api_ok:
        try:
            response = requests.get(f"{API_BASE}/templates/")
            if response.status_code == 200:
                templates = response.json()
                
                # 按行业分组
                industries = sorted(set(t["industry"] for t in templates))
                
                for ind in industries:
                    with st.expander(f"🏭 {ind}"):
                        ind_templates = [t for t in templates if t["industry"] == ind]
                        for t in ind_templates:
                            st.markdown(f"**{t['name']}**")
                            st.write(f"描述: {t.get('description', '无')}")
                            st.write(f"默认保额: {t['default_coverage']}万元")
                            st.write(f"默认险种: {t['default_insurance_type']}")
                            st.write(f"基础费率: {t['base_rate']}元/万元")
                            st.markdown("---")
            else:
                st.error("获取模板失败")
        except Exception as e:
            st.error(f"请求出错: {str(e)}")
    else:
        st.warning("API 未连接，无法获取模板")


elif page == "📜 报价历史":
    st.subheader("📜 报价历史记录")
    
    if api_ok:
        try:
            response = requests.get(f"{API_BASE}/quotations/history")
            if response.status_code == 200:
                quotations = response.json()
                
                if not quotations:
                    st.info("暂无报价记录")
                else:
                    st.write(f"共 {len(quotations)} 条记录")
                    
                    for q in quotations[:20]:  # 显示最近20条
                        with st.expander(
                            f"{q['company_name']} - {q['insurance_type']} "
                            f"(¥{q['premium']:,.2f})"
                        ):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"行业: {q['industry']}")
                                st.write(f"员工: {q['employee_count']}人")
                                st.write(f"平均年龄: {q['average_age']}岁")
                            with col2:
                                st.write(f"保额: {q['coverage_amount']}万元")
                                st.write(f"保费: ¥{q['premium']:,.2f}")
                                st.write(f"风控: {q['risk_level']}")
                            if q.get('risk_notes'):
                                st.info(q['risk_notes'])
            else:
                st.error("获取历史记录失败")
        except Exception as e:
            st.error(f"请求出错: {str(e)}")
    else:
        st.warning("API 未连接，无法获取历史记录")


elif page == "⚙️ 系统设置":
    st.subheader("⚙️ 系统设置")
    
    st.markdown("### API 配置")
    api_url = st.text_input("API 地址", value=API_BASE)
    
    st.markdown("### 关于")
    st.write("团险报价助手 v1.0")
    st.write("为企业客户提供快速保费计算、方案模板和风控建议")
    st.write("---")
    st.write("© 2026 团险报价助手")
