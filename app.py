import streamlit as st
from supabase import create_client, Client
import pandas as pd
import base64

# --- 1. 数据库配置 ---
URL = "https://xcrbvvlsbjsmxaepkdbl.supabase.co"
KEY = "sb_publishable_QYXt0Fs5YKpCBXxCjdb4sg_9y7rkksj"
supabase: Client = create_client(URL, KEY)

# --- 2. 设备清单 ---
DEVICE_MAP = {
    "直流电源": [],
    "万用表": [],
    "电流钳": [],
    "示波器": []
}

# --- 3. 极致视觉定制（物理级清除标志 + 自动配色） ---
st.set_page_config(page_title="设备领用登记表", layout="centered")

def get_base64_image(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

# 图片名需保持一致
img_base64 = get_base64_image("IMG_4614.jpeg")

# 终极 CSS：不仅是隐藏，而是彻底物理移除官方组件
style = f"""
    <style>
    /* --- 1. 彻底清除官方标志（红船/皇冠、绿点、菜单、页脚） --- */
    
    /* 强制隐藏头部、页脚、工具栏、状态组件 */
    header, footer, [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] {{
        display: none !important;
        visibility: hidden !important;
    }}

    /* 针对右下角“Hosted with Streamlit”及其容器的物理移除 */
    .stAppDeployButton, 
    [data-testid="stAppDeployButton"], 
    [data-testid="manage-app-button"],
    div[class*="st-emotion-cache-zq59as"],
    div[class*="st-emotion-cache-1wbqy5l"],
    div[class*="st-emotion-cache-1dp5vir"] {{
        display: none !important;
        position: absolute !important;
        left: -9999px !important;
    }}

    /* 针对左下角绿色状态圆点及其所有层级的物理移除 */
    [data-testid="stStatusWidget"], 
    #stStatusWidget,
    div[class*="stStatusWidget"] {{
        display: none !important;
        position: absolute !important;
        left: -9999px !important;
    }}

    /* --- 2. 自动配色逻辑：确保任何模式下字都清晰 --- */
    :root {{
        --main-bg: #FFFFFF;
        --card-bg: #FFFFFF;
        --text-color: #000000;
        --input-bg: #F8F9FA;
    }}

    @media (prefers-color-scheme: dark) {{
        :root {{
            --main-bg: #0E1117;
            --card-bg: #1A1C23;
            --text-color: #FFFFFF;
            --input-bg: #2D2F39;
        }}
    }}

    /* 应用自动配色 */
    .stApp {{
        background-color: var(--main-bg) !important;
        color: var(--text-color) !important;
    }}

    /* 强制所有文字标签颜色 */
    h1, h2, h3, p, label, span, div, .stMarkdown {{
        color: var(--text-color) !important;
        font-weight: 600 !important;
    }}

    /* --- 3. 全屏水印背景 --- */
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0; left: 0; bottom: 0; right: 0;
        background-image: url("data:image/jpeg;base64,{img_base64}");
        background-repeat: no-repeat;
        background-position: center;
        background-size: 55%; 
        opacity: 0.03; /* 极淡水印，增加高端感 */
        z-index: -1;
    }}

    /* --- 4. 表单卡片美化（简约时尚大气） --- */
    div[data-testid="stForm"] {{
        border: 1px solid rgba(128,128,128,0.1) !important;
        border-radius: 24px !important;
        background-color: var(--card-bg) !important;
        padding: 35px !important;
        box-shadow: 0 20px 50px rgba(0,0,0,0.1) !important;
    }}

    /* --- 5. 提交按钮 (绿色时尚感) --- */
    .stButton>button {{
        width: 100%;
        border-radius: 12px !important;
        height: 3.8em !important;
        background-color: #28A745 !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        font-size: 18px !important;
        border: none !important;
        margin-top: 20px !important;
        box-shadow: 0 8px 20px rgba(40,167,69,0.2) !important;
        transition: 0.3s;
    }}
    .stButton>button:hover {{
        background-color: #218838 !important;
        transform: translateY(-2px);
    }}

    /* 修正输入框背景 */
    input, .stSelectbox div {{
        background-color: var(--input-bg) !important;
        color: var(--text-color) !important;
    }}
    </style>
"""
st.markdown(style, unsafe_allow_html=True)

# --- 4. 页面内容布局 ---

# 顶部放置清晰 Logo
if img_base64:
    st.markdown(f'<div style="text-align: center;"><img src="data:image/jpeg;base64,{img_base64}" width="200"></div>', unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; margin-top: 10px;'>设备领用登记表</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; opacity: 0.7; font-size: 14px;'>UL Solutions Laboratory Asset Registry</p>", unsafe_allow_html=True)

# --- 登记表单 ---
with st.form("lab_form", clear_on_submit=True):
    staff_id = st.text_input("工号 (Staff ID)", placeholder="请输入您的工号")
    action_type = st.radio("操作类型", ["领用 (Check-out)", "归还 (Return)"], horizontal=True)
    device_name = st.selectbox("设备名称", ["请选择设备类型"] + list(DEVICE_MAP.keys()))
    device_id = st.text_input("设备编号", placeholder="请输入唯一设备号")
    
    st.markdown("<br>", unsafe_allow_html=True)
    submit_btn = st.form_submit_button("确认提交登记 (SUBMIT)")

# --- 提交逻辑 ---
if submit_btn:
    if not staff_id or device_name == "请选择设备类型" or not device_id:
        st.error("❌ 请完整填写所有信息！")
    else:
        try:
            entry = {
                "staff_id": staff_id,
                "action_type": "领用" if "领用" in action_type else "归还",
                "device_name": device_name,
                "device_id": device_id
            }
            supabase.table("lab_records").insert(entry).execute()
            st.success("✅ 登记成功！已存入云端系统。")
            st.balloons()
        except Exception as e:
            st.error(f"系统提交出错: {e}")

# --- 管理员后台 ---
st.markdown("<br><br>", unsafe_allow_html=True)
with st.expander("📊 查看记录 (管理人员专用)"):
    try:
        response = supabase.table("lab_records").select("*").order("created_at", desc=True).execute()
        if response.data:
            df = pd.DataFrame(response.data)
            df = df[['staff_id', 'action_type', 'device_name', 'device_id', 'created_at']]
            df.columns = ["工号", "类型", "设备名称", "编号", "登记时间"]
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode('utf_8_sig')
            st.download_button("📥 导出 Excel", csv, "Lab_Records.csv", "text/csv")
    except:
        st.write("暂无数据。")