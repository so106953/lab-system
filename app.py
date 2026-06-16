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

# --- 3. 极致视觉定制（绿色按钮 + 彻底去标志） ---
st.set_page_config(page_title="设备领用登记表", layout="centered")

def get_base64_image(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

# 请确保你的图片名依然是这个，如果改了名字请在这里修改
img_base64 = get_base64_image("IMG_4614.jpeg")

# 核心 CSS：强制配色 + 深度抹除标志
style = f"""
    <style>
    /* --- 1. 彻底抹除所有官方标志（包括右下角红绿图标） --- */
    #MainMenu, footer, header {{visibility: hidden !important; display: none !important;}}
    [data-testid="stToolbar"], [data-testid="stDecoration"] {{display: none !important;}}
    
    /* 强力隐藏右下角管理按钮和状态图标 */
    [data-testid="manage-app-button"], 
    [data-testid="stStatusWidget"],
    .stDeployButton,
    .stAppDeployButton,
    #stStatusWidget {{
        display: none !important;
        visibility: hidden !important;
    }}
    
    /* --- 2. 强制全局配色（白底黑字，对比度最高） --- */
    .stApp {{
        background-color: #F0F2F5 !important;
    }}
    
    /* 水印：位置居中，极淡，不干扰文字 */
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

    /* 强制所有文字颜色为纯黑色 */
    h1, h2, h3, p, label, span, div {{
        color: #000000 !important;
        font-weight: 600 !important;
    }}
    
    /* 输入框内的文字也强制黑色 */
    input {{
        color: #000000 !important;
    }}

    /* --- 3. 表单卡片定制 --- */
    div[data-testid="stForm"] {{
        border: none !important;
        border-radius: 20px !important;
        background-color: #FFFFFF !important;
        padding: 30px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15) !important;
    }}

    /* --- 4. 按钮定制 (改为绿色) --- */
    .stButton>button {{
        width: 100%;
        border-radius: 12px !important;
        height: 3.5em !important;
        background-color: #28A745 !important; /* 绿色 */
        color: #FFFFFF !important;
        font-weight: bold !important;
        font-size: 18px !important;
        border: none !important;
        margin-top: 20px !important;
        box-shadow: 0 4px 12px rgba(40,167,69,0.3) !important;
    }}
    .stButton>button:hover {{
        background-color: #218838 !important;
        box-shadow: 0 6px 15px rgba(40,167,69,0.4) !important;
    }}
    </style>
"""
st.markdown(style, unsafe_allow_html=True)

# --- 4. 页面内容 ---

# 顶部 Logo
if img_base64:
    st.markdown(f'<div style="text-align: center;"><img src="data:image/jpeg;base64,{img_base64}" width="220"></div>', unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; margin-bottom:0;'>设备领用登记表</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #333 !important; font-size: 14px;'>UL Solutions Laboratory Asset Registry</p>", unsafe_allow_html=True)

# --- 登记表单 ---
with st.form("lab_form", clear_on_submit=True):
    staff_id = st.text_input("工号 (Staff ID)", placeholder="请输入工号")
    
    action_type = st.radio("操作类型", ["领用 (Check-out)", "归还 (Return)"], horizontal=True)
    
    device_name = st.selectbox("设备名称", ["请选择"] + list(DEVICE_MAP.keys()))
    
    device_id = st.text_input("设备编号", placeholder="请输入唯一编号")
    
    st.markdown("<br>", unsafe_allow_html=True)
    submit_btn = st.form_submit_button("确认提交登记")

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
            st.success("✅ 登记成功！已存入数据库。")
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
            st.download_button("📥 导出 Excel (CSV)", csv, "UL_Records.csv", "text/csv")
    except:
        st.write("暂无记录")