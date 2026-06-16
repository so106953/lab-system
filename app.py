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

# --- 3. 极致视觉定制 (水印+去痕迹) ---
st.set_page_config(page_title="UL Registry", layout="centered")

# 将本地图片转为 Base64（确保图片存在仓库中，名字为 logo.png）
def get_base64_image(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

img_base64 = get_base64_image("logo.png")

# 核心 CSS：深度抹除所有 Streamlit 痕迹 + 设置水印背景
style = f"""
    <style>
    /* --- 彻底隐藏 Streamlit 所有组件 --- */
    [data-testid="stToolbar"],             /* 顶部工具栏 */
    [data-testid="stDecoration"],          /* 顶部彩虹条 */
    [data-testid="stStatusWidget"],        /* 运行状态提示 */
    #MainMenu,                             /* 汉堡菜单 */
    header,                                /* 头部 */
    footer {{                             /* 页脚 */
        visibility: hidden;
        height: 0% !important;
        display: none !important;
    }}
    
    /* --- 全屏水印背景 --- */
    .stApp {{
        background-color: #FFFFFF;
    }}
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0; left: 0; bottom: 0; right: 0;
        background-image: url("data:image/png;base64,{img_base64}");
        background-repeat: no-repeat;
        background-position: center;
        background-size: 60%; /* 水印大小 */
        opacity: 0.05;        /* 极淡的水印透明度，保证时尚感 */
        z-index: -1;          /* 放在最底层 */
    }}

    /* --- 表单卡片美化（时尚大气） --- */
    div[data-testid="stForm"] {{
        border: 1px solid rgba(0,0,0,0.05) !important;
        border-radius: 24px !important;
        background: rgba(255, 255, 255, 0.8) !important; /* 半透明磨砂感 */
        backdrop-filter: blur(10px); /* 模糊背景 */
        padding: 40px !important;
        box-shadow: 0 20px 40px rgba(0,0,0,0.08) !important;
    }}

    /* --- UL 红色按钮样式 --- */
    .stButton>button {{
        width: 100%;
        border-radius: 12px !important;
        height: 3.5em !important;
        background-color: #B01F24 !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        letter-spacing: 1px !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(176,31,36,0.2) !important;
    }}
    
    /* --- 输入框美化 --- */
    input, .stSelectbox {{
        background-color: #FFFFFF !important;
        border: 1px solid #EEEEEE !important;
        border-radius: 10px !important;
        color: #333333 !important;
    }}
    </style>
"""
st.markdown(style, unsafe_allow_html=True)

# --- 4. 页面内容 ---

# 顶部放置一个清晰的 Logo
if img_base64:
    st.markdown(f'<div style="text-align: center;"><img src="data:image/png;base64,{img_base64}" width="200"></div>', unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; font-weight: 200; color: #333;'>设备资产登记系统</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #999; font-size: 13px; margin-bottom: 30px;'>Laboratory Asset Registration System</p>", unsafe_allow_html=True)

# --- 登记表单 ---
with st.form("lab_form", clear_on_submit=True):
    staff_id = st.text_input("工号 (Staff ID)", placeholder="请输入工号")
    action_type = st.radio("操作", ["领用 (Check-out)", "归还 (Return)"], horizontal=True)
    device_name = st.selectbox("设备名称", ["请选择"] + list(DEVICE_MAP.keys()))
    device_id = st.text_input("设备编号", placeholder="请输入唯一设备号")
    
    st.markdown("<br>", unsafe_allow_html=True)
    submit_btn = st.form_submit_button("确认提交 (SUBMIT)")

# --- 提交逻辑 ---
if submit_btn:
    if not staff_id or device_name == "请选择" or not device_id:
        st.error("请完整填写所有信息！")
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
            st.error(f"提交失败: {e}")

# --- 管理员后台 ---
st.markdown("<br><br>", unsafe_allow_html=True)
with st.expander("管理后台 (仅限授权查看)"):
    try:
        response = supabase.table("lab_records").select("*").order("created_at", desc=True).execute()
        if response.data:
            df = pd.DataFrame(response.data)
            df = df[['staff_id', 'action_type', 'device_name', 'device_id', 'created_at']]
            df.columns = ["工号", "类型", "设备", "编号", "时间"]
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode('utf_8_sig')
            st.download_button("导出 Excel", csv, "records.csv", "text/csv")
    except:
        st.write("暂无记录")