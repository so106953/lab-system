import streamlit as st
from supabase import create_client, Client
import pandas as pd
import base64

# --- 1. 数据库配置 (保持不变) ---
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

# --- 3. 极致视觉定制 (已适配你的图片 IMG_4614.jpeg) ---
st.set_page_config(page_title="UL Registry", layout="centered")

def get_base64_image(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

# 重点：这里已经改成了你的图片名
img_base64 = get_base64_image("IMG_4614.jpeg")

# CSS：深度隐藏所有第三方标志 + 磨砂玻璃感 + 全屏水印
style = f"""
    <style>
    /* 彻底隐藏所有 Streamlit 官方标志和菜单 */
    [data-testid="stToolbar"], 
    [data-testid="stDecoration"], 
    [data-testid="stStatusWidget"], 
    #MainMenu, header, footer {{
        visibility: hidden;
        display: none !important;
    }}
    
    /* 全局背景色 */
    .stApp {{
        background-color: #FFFFFF;
    }}

    /* 全屏 LOGO 水印层 */
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0; left: 0; bottom: 0; right: 0;
        background-image: url("data:image/jpeg;base64,{img_base64}");
        background-repeat: no-repeat;
        background-position: center;
        background-size: 70%; 
        opacity: 0.05; /* 水印透明度 */
        z-index: -1;
    }}

    /* 高端磨砂感卡片 */
    div[data-testid="stForm"] {{
        border: 1px solid rgba(0,0,0,0.05) !important;
        border-radius: 24px !important;
        background: rgba(255, 255, 255, 0.9) !important;
        backdrop-filter: blur(10px);
        padding: 40px !important;
        box-shadow: 0 20px 50px rgba(0,0,0,0.1) !important;
    }}

    /* UL 风格红色按钮 */
    .stButton>button {{
        width: 100%;
        border-radius: 12px !important;
        height: 3.8em !important;
        background-color: #B01F24 !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(176,31,36,0.2) !important;
        transition: 0.3s;
    }}
    .stButton>button:hover {{
        background-color: #8C181D !important;
        box-shadow: 0 6px 20px rgba(176,31,36,0.4) !important;
    }}

    /* 输入框优化 */
    input, .stSelectbox {{
        border-radius: 10px !important;
    }}
    </style>
"""
st.markdown(style, unsafe_allow_html=True)

# --- 4. 页面内容 ---

# 顶部放置清晰 Logo
if img_base64:
    st.markdown(f'<div style="text-align: center; margin-bottom: 20px;"><img src="data:image/jpeg;base64,{img_base64}" width="220"></div>', unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; font-weight: 300; color: #333;'>设备资产登记系统</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #999; font-size: 13px;'>Laboratory Asset Management System</p><br>", unsafe_allow_html=True)

# --- 登记表单 ---
with st.form("lab_form", clear_on_submit=True):
    staff_id = st.text_input("👤 工号 (Staff ID)", placeholder="请输入您的工号")
    action_type = st.radio("📝 操作类型", ["领用 (Check-out)", "归还 (Return)"], horizontal=True)
    device_name = st.selectbox("📦 设备名称", ["请选择"] + list(DEVICE_MAP.keys()))
    device_id = st.text_input("🔢 设备编号", placeholder="请输入唯一设备号")
    
    st.markdown("<br>", unsafe_allow_html=True)
    submit_btn = st.form_submit_button("确认提交 (SUBMIT)")

# --- 提交逻辑 ---
if submit_btn:
    if not staff_id or device_name == "请选择" or not device_id:
        st.warning("⚠️ 请完整填写所有信息！")
    else:
        try:
            entry = {
                "staff_id": staff_id,
                "action_type": "领用" if "领用" in action_type else "归还",
                "device_name": device_name,
                "device_id": device_id
            }
            supabase.table("lab_records").insert(entry).execute()
            st.success("✅ 登记成功！数据已实时同步至后台。")
            st.balloons()
        except Exception as e:
            st.error(f"提交出错: {e}")

# --- 管理员后台 (隐藏在折叠栏) ---
st.markdown("<br><br>", unsafe_allow_html=True)
with st.expander("📊 管理后台 (仅限管理员查看)"):
    try:
        response = supabase.table("lab_records").select("*").order("created_at", desc=True).execute()
        if response.data:
            df = pd.DataFrame(response.data)
            df = df[['staff_id', 'action_type', 'device_name', 'device_id', 'created_at']]
            df.columns = ["工号", "类型", "设备", "编号", "时间"]
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode('utf_8_sig')
            st.download_button("📥 导出 Excel (CSV)", csv, "UL_Records.csv", "text/csv")
    except:
        st.write("暂无数据。")