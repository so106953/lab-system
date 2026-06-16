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

# --- 3. 极致视觉定制 ---
st.set_page_config(page_title="设备领用登记表", layout="centered")

def get_base64_image(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

img_base64 = get_base64_image("IMG_4614.jpeg")

style = f"""
    <style>
    /* --- A. 彻底抹除官方标志 --- */
    header, footer, [data-testid="stHeader"], [data-testid="stToolbar"] {{
        display: none !important;
        height: 0 !important;
    }}

    [data-testid="manage-app-button"],
    [data-testid="stStatusWidget"],
    [data-testid="stAppDeployButton"],
    .stDeployButton,
    .stAppDeployButton {{
        display: none !important;
        visibility: hidden !important;
    }}

    div[class*="StatusWidget"],
    div[class*="deployButton"],
    div[class*="toolbarActions"] {{
        display: none !important;
        visibility: hidden !important;
        pointer-events: none !important;
    }}

    /* 终极覆盖：用背景色色块遮盖右下角区域 */
    .stApp::after {{
        content: "";
        position: fixed;
        bottom: 0;
        right: 0;
        width: 320px;
        height: 80px;
        background-color: var(--main-bg);
        z-index: 999999;
    }}

    /* --- B. 自动配色逻辑 --- */
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

    .stApp {{
        background-color: var(--main-bg) !important;
        color: var(--text-color) !important;
    }}

    h1, h2, h3, p, label, span, div, .stMarkdown {{
        color: var(--text-color) !important;
        font-weight: 600 !important;
    }}

    /* --- C. 水印背景 --- */
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0; left: 0; bottom: 0; right: 0;
        background-image: url("data:image/jpeg;base64,{img_base64}");
        background-repeat: no-repeat;
        background-position: center;
        background-size: 50%; 
        opacity: 0.02; 
        z-index: -1;
    }}

    /* --- D. 表单卡片定制 --- */
    div[data-testid="stForm"] {{
        border: 1px solid rgba(128,128,128,0.1) !important;
        border-radius: 24px !important;
        background-color: var(--card-bg) !important;
        padding: 30px !important;
        box-shadow: 0 20px 50px rgba(0,0,0,0.1) !important;
    }}

    /* --- E. 按钮定制 (绿色确认) --- */
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
    }}
    </style>
"""
st.markdown(style, unsafe_allow_html=True)

# --- 4. 页面内容布局 ---

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
            st.success("✅ 登记成功！数据已实时备份。")
            st.balloons()
        except Exception as e:
            st.error(f"系统报错: {e}")

# --- 管理员后台 ---
st.markdown("<br><br>", unsafe_allow_html=True)
with st.expander("📊 查看记录 (管理人员专用)"):
    try:
        response = supabase.table("lab_records").select("*").order("created_at", desc=True).execute()
        if response.data:
            df = pd.DataFrame(response.data)
            df['created_at'] = pd.to_datetime(df['created_at']).dt.tz_convert('Asia/Shanghai').dt.strftime('%Y-%m-%d %H:%M:%S')
            df_display = df[['staff_id', 'action_type', 'device_name', 'device_id', 'created_at']]
            df_display.columns = ["工号", "类型", "设备名称", "编号", "登记时间"]
            st.dataframe(df_display, use_container_width=True)
            csv = df_display.to_csv(index=False).encode('utf_8_sig')
            st.download_button("📥 导出 Excel", csv, "UL_Records.csv", "text/csv")
    except Exception as e:
        st.write(f"暂无记录或解析出错: {e}")
