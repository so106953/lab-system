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

# --- 3. 极致视觉定制（强力清除标志 + 增强对比度） ---
st.set_page_config(page_title="设备领用登记表", layout="centered")

def get_base64_image(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

img_base64 = get_base64_image("IMG_4614.jpeg")

# 核心 CSS：强制配色 + 深度抹除标志
style = f"""
    <style>
    /* --- 1. 强力抹除右下角标志、顶部条、菜单 --- */
    [data-testid="stToolbar"], 
    [data-testid="stDecoration"], 
    [data-testid="stStatusWidget"], 
    [data-testid="manage-app-button"],
    #MainMenu, header, footer {{
        display: none !important;
        visibility: hidden !important;
    }}
    
    /* --- 2. 强制全局配色（解决看不清问题） --- */
    .stApp {{
        background-color: #F8F9FA !important;
    }}
    
    /* 水印设置 */
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0; left: 0; bottom: 0; right: 0;
        background-image: url("data:image/jpeg;base64,{img_base64}");
        background-repeat: no-repeat;
        background-position: center;
        background-size: 60%; 
        opacity: 0.03; /* 极淡水印，不干扰视线 */
        z-index: -1;
    }}

    /* 强制所有文字为深黑色 */
    h1, h2, h3, p, label, .stMarkdown, span, div {{
        color: #333333 !important;
        font-weight: 500 !important;
    }}

    /* --- 3. 表单卡片定制 --- */
    div[data-testid="stForm"] {{
        border: none !important;
        border-radius: 20px !important;
        background-color: #FFFFFF !important; /* 纯白背景，确保文字清晰 */
        padding: 35px !important;
        box-shadow: 0 12px 40px rgba(0,0,0,0.12) !important;
    }}

    /* --- 4. 按钮定制 (UL红) --- */
    .stButton>button {{
        width: 100%;
        border-radius: 10px !important;
        height: 3.5em !important;
        background-color: #B01F24 !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        border: none !important;
        margin-top: 15px !important;
    }}
    
    /* 修正输入框背景 */
    input, .stSelectbox div {{
        background-color: #FDFDFD !important;
        color: #333333 !important;
    }}
    </style>
"""
st.markdown(style, unsafe_allow_html=True)

# --- 4. 页面内容 ---

# 顶部 Logo
if img_base64:
    st.markdown(f'<div style="text-align: center;"><img src="data:image/jpeg;base64,{img_base64}" width="200"></div>', unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; margin-top: 10px;'>设备领用登记表</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666 !important;'>UL Solutions Laboratory Registry</p>", unsafe_allow_html=True)

# --- 登记表单 ---
with st.form("lab_form", clear_on_submit=True):
    staff_id = st.text_input("工号 (Staff ID)", placeholder="请输入您的工号")
    
    action_type = st.radio("操作类型", ["领用 (Check-out)", "归还 (Return)"], horizontal=True)
    
    device_name = st.selectbox("设备名称", ["请选择设备类型"] + list(DEVICE_MAP.keys()))
    
    device_id = st.text_input("设备编号", placeholder="请输入唯一设备号")
    
    st.markdown("<br>", unsafe_allow_html=True)
    submit_btn = st.form_submit_button("确认提交登记")

# --- 提交逻辑 ---
if submit_btn:
    if not staff_id or device_name == "请选择设备类型" or not device_id:
        st.warning("⚠️ 请完整填写所有信息！")
    else:
        try:
            entry = {{
                "staff_id": staff_id,
                "action_type": "领用" if "领用" in action_type else "归还",
                "device_name": device_name,
                "device_id": device_id
            }}
            supabase.table("lab_records").insert(entry).execute()
            st.success("✅ 登记成功！数据已实时备份。")
            st.balloons()
        except Exception as e:
            st.error(f"提交出错: {{e}}")

# --- 管理员后台 ---
st.markdown("<br><br>", unsafe_allow_html=True)
with st.expander("📊 查看历史记录 (仅限管理人员)"):
    try:
        response = supabase.table("lab_records").select("*").order("created_at", desc=True).execute()
        if response.data:
            df = pd.DataFrame(response.data)
            df = df[['staff_id', 'action_type', 'device_name', 'device_id', 'created_at']]
            df.columns = ["工号", "类型", "设备", "编号", "时间"]
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode('utf_8_sig')
            st.download_button("📥 导出 Excel", csv, "UL_Registry.csv", "text/csv")
    except:
        st.write("暂无记录")