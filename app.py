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

# --- 3. 视觉定制：彻底抹除标志 + 自动配色 ---
st.set_page_config(page_title="设备领用登记表", layout="centered")

def get_base64_image(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

img_base64 = get_base64_image("IMG_4614.jpeg")

# 终极 CSS：强制物理遮屏
# 重点针对：.stAppDeployButton (红船) 和 [data-testid="stStatusWidget"] (绿圈)
style = f"""
    <style>
    /* 1. 彻底抹除顶部和右下角所有 Streamlit 注入的元素 */
    header, [data-testid="stHeader"], footer {{
        display: none !important;
        height: 0px !important;
    }}
    
    /* 针对你截图中的红色皇冠/纸船标志的深度清理 */
    .stAppDeployButton, 
    [data-testid="manage-app-button"], 
    [data-testid="stAppDeployButton"],
    div[class*="st-emotion-cache-zq59as"],
    div[class*="st-emotion-cache-1wbqy5l"],
    button[title="View menu"] {{
        display: none !important;
        visibility: hidden !important;
        width: 0px !important;
        height: 0px !important;
    }}

    /* 针对左边那个绿色状态圆点的深度清理 */
    [data-testid="stStatusWidget"], 
    #stStatusWidget,
    div[data-testid="stStatusWidget"] {{
        display: none !important;
        visibility: hidden !important;
    }}

    /* 2. 自动配色逻辑：兼容深色/浅色模式 */
    :root {{
        --text-color: #000000;
        --card-bg: #FFFFFF;
        --sub-text: #666666;
    }}

    @media (prefers-color-scheme: dark) {{
        :root {{
            --text-color: #FFFFFF;
            --card-bg: #1E1E1E;
            --sub-text: #AAAAAA;
        }}
    }}

    .stApp {{
        color: var(--text-color);
    }}

    /* 水印背景 */
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0; left: 0; bottom: 0; right: 0;
        background-image: url("data:image/jpeg;base64,{img_base64}");
        background-repeat: no-repeat;
        background-position: center;
        background-size: 55%; 
        opacity: 0.03; 
        z-index: -1;
    }}

    /* 表单卡片定制 */
    div[data-testid="stForm"] {{
        border-radius: 24px !important;
        background-color: var(--card-bg) !important;
        padding: 30px !important;
        box-shadow: 0 15px 45px rgba(0,0,0,0.15) !important;
        border: 1px solid rgba(128,128,128,0.1) !important;
    }}

    /* 文字对比度强制提升 */
    h1, h2, label, p, span, div {{
        color: var(--text-color) !important;
        font-weight: 600 !important;
    }}

    /* 3. 提交按钮美化 (UL 红色风格) */
    .stButton>button {{
        width: 100%;
        border-radius: 12px !important;
        height: 3.8em !important;
        background-color: #B01F24 !important; /* UL 红色 */
        color: #FFFFFF !important;
        font-weight: bold !important;
        font-size: 18px !important;
        border: none !important;
        margin-top: 20px !important;
        box-shadow: 0 5px 15px rgba(176,31,36,0.3) !important;
    }}
    </style>
"""
st.markdown(style, unsafe_allow_html=True)

# --- 4. 页面内容 ---

# 顶部 Logo
if img_base64:
    st.markdown(f'<div style="text-align: center;"><img src="data:image/jpeg;base64,{img_base64}" width="200"></div>', unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; margin-top: 10px;'>设备领用登记表</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; opacity: 0.7; font-size: 14px;'>UL Solutions Laboratory Asset Registry</p>", unsafe_allow_html=True)

# --- 登记表单 ---
with st.form("lab_form", clear_on_submit=True):
    staff_id = st.text_input("工号 (Staff ID)", placeholder="请输入您的工号")
    action_type = st.radio("操作类型", ["领用 (Check-out)", "归还 (Return)"], horizontal=True)
    device_name = st.selectbox("设备名称", ["请选择"] + list(DEVICE_MAP.keys()))
    device_id = st.text_input("设备编号", placeholder="请输入唯一设备号")
    
    st.markdown("<br>", unsafe_allow_html=True)
    submit_btn = st.form_submit_button("确认提交登记 (SUBMIT)")

# --- 提交逻辑 ---
if submit_btn:
    if not staff_id or device_name == "请选择" or not device_id:
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
            st.success("✅ 登记成功！已实时同步。")
            st.balloons()
        except Exception as e:
            st.error(f"提交出错: {e}")

# --- 管理员后台 ---
st.markdown("<br><br>", unsafe_allow_html=True)
with st.expander("📊 查看记录 (管理人员专用)"):
    try:
        response = supabase.table("lab_records").select("*").order("created_at", desc=True).execute()
        if response.data:
            df = pd.DataFrame(response.data)
            df = df[['staff_id', 'action_type', 'device_name', 'device_id', 'created_at']]
            df.columns = ["工号", "类型", "设备", "编号", "时间"]
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode('utf_8_sig')
            st.download_button("📥 导出 Excel", csv, "UL_Records.csv", "text/csv")
    except:
        st.write("暂无记录")