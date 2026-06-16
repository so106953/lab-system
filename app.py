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

# --- 3. 极致视觉定制（强制白底黑字 + 深度清除标志） ---
st.set_page_config(page_title="设备领用登记表", layout="centered")

def get_base64_image(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

# 请确认 GitHub 仓库中图片名为 IMG_4614.jpeg
img_base64 = get_base64_image("IMG_4614.jpeg")

# CSS 深度美化方案
style = f"""
    <style>
    /* --- A. 彻底抹除官方标志（红色纸船、绿色圆点、所有菜单） --- */
    /* 隐藏所有可能的 Streamlit 官方注入组件 */
    [data-testid="stHeader"], 
    [data-testid="stToolbar"], 
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    [data-testid="manage-app-button"],
    .stDeployButton,
    .stAppDeployButton,
    #MainMenu, 
    header, 
    footer {{
        visibility: hidden !important;
        display: none !important;
    }}

    /* --- B. 强制锁定视觉配色 (无视手机深色模式) --- */
    html, body, .stApp, [data-testid="stAppViewContainer"] {{
        background-color: #F9F9F9 !important; /* 网页大背景：极浅灰 */
        color: #000000 !important;
    }}

    /* 强制所有文本为纯黑色，确保清晰度 */
    h1, h2, h3, p, label, span, div, li, input {{
        color: #000000 !important;
        font-weight: 600 !important; /* 加粗文字增强阅读 */
    }}

    /* --- C. 全屏水印背景 --- */
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0; left: 0; bottom: 0; right: 0;
        background-image: url("data:image/jpeg;base64,{img_base64}");
        background-repeat: no-repeat;
        background-position: center;
        background-size: 55%; 
        opacity: 0.02; /* 极淡水印，增加大气感 */
        z-index: -1;
    }}

    /* --- D. 表单卡片定制（简约时尚大气） --- */
    div[data-testid="stForm"] {{
        border: none !important;
        border-radius: 24px !important;
        background-color: #FFFFFF !important; /* 卡片纯白 */
        padding: 40px !important;
        box-shadow: 0 20px 60px rgba(0,0,0,0.1) !important;
    }}

    /* --- E. 绿色确认按钮 --- */
    .stButton>button {{
        width: 100%;
        border-radius: 12px !important;
        height: 3.8em !important;
        background-color: #28A745 !important; /* 确认绿 */
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
        box-shadow: 0 10px 25px rgba(40,167,69,0.3) !important;
    }}

    /* 输入框边框微调 */
    input, .stSelectbox div {{
        border: 1px solid #EEEEEE !important;
        border-radius: 10px !important;
    }}
    </style>
"""
st.markdown(style, unsafe_allow_html=True)

# --- 4. 页面内容布局 ---

# 顶部放置清晰 Logo
if img_base64:
    st.markdown(f'<div style="text-align: center;"><img src="data:image/jpeg;base64,{img_base64}" width="200"></div>', unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; margin-top: 10px; margin-bottom: 0px;'>设备领用登记表</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666666 !important; font-size: 14px;'>UL Solutions Laboratory Asset Registry</p>", unsafe_allow_html=True)

# --- 登记表单 ---
with st.form("lab_form", clear_on_submit=True):
    staff_id = st.text_input("👤 工号 (Staff ID)", placeholder="请输入您的工号")
    
    action_type = st.radio("📝 操作类型", ["领用 (Check-out)", "归还 (Return)"], horizontal=True)
    
    device_name = st.selectbox("📦 设备名称", ["请选择设备类型"] + list(DEVICE_MAP.keys()))
    
    device_id = st.text_input("🔢 设备编号", placeholder="请输入唯一设备号")
    
    st.markdown("<br>", unsafe_allow_html=True)
    submit_btn = st.form_submit_button("确认提交登记")

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
            st.success("✅ 登记成功！已实时备份至云端。")
            st.balloons()
        except Exception as e:
            st.error(f"提交出错: {e}")

# --- 管理员后台 ---
st.markdown("<br><br>", unsafe_allow_html=True)
with st.expander("📊 查看历史记录 (管理人员专用)"):
    try:
        response = supabase.table("lab_records").select("*").order("created_at", desc=True).execute()
        if response.data:
            df = pd.DataFrame(response.data)
            df = df[['staff_id', 'action_type', 'device_name', 'device_id', 'created_at']]
            df.columns = ["工号", "类型", "设备名称", "编号", "登记时间"]
            st.dataframe(df, use_container_width=True)
            
            # 导出 Excel
            csv = df.to_csv(index=False).encode('utf_8_sig')
            st.download_button("📥 导出完整电子档 (Excel)", csv, "UL_Records.csv", "text/csv")
    except:
        st.write("暂无记录")