import streamlit as st
from supabase import create_client, Client
import pandas as pd

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

# --- 3. 深度视觉定制 (UL 品牌风格) ---
st.set_page_config(page_title="UL 实验室管理系统", layout="centered")

# CSS 注入：打造简约时尚大气的 UI
style = """
    <style>
    /* 隐藏多余组件 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 全局背景：极简淡雅灰 */
    .stApp {
        background: #FDFDFD;
    }
    
    /* 品牌 Logo 区域 */
    .logo-container {
        display: flex;
        justify-content: center;
        padding: 20px 0;
    }

    /* 表单卡片定制 */
    div[data-testid="stForm"] {
        border: none !important;
        border-radius: 20px !important;
        background-color: #FFFFFF !important;
        padding: 40px !important;
        box-shadow: 0 15px 35px rgba(0,0,0,0.05) !important;
    }

    /* 标题美化 */
    .main-title {
        text-align: center;
        color: #333333;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-weight: 300;
        letter-spacing: 1px;
        margin-bottom: 30px;
    }

    /* UL 品牌红色按钮 */
    .stButton>button {
        width: 100%;
        border-radius: 50px; /* 胶囊型按钮，更时尚 */
        height: 3.5em;
        background-color: #B01F24 !important; /* UL 红色 */
        color: white !important;
        border: none !important;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #8C181D !important; /* 悬停深红色 */
        box-shadow: 0 5px 15px rgba(176,31,36,0.3);
    }

    /* 输入框圆角 */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        border-radius: 10px !important;
    }
    </style>
"""
st.markdown(style, unsafe_allow_html=True)

# --- 4. 页面内容 ---

# 顶部 Logo 品牌区 (这里建议将图片放在 GitHub 仓库并使用链接，暂时先用文字占位)
st.markdown('<div class="logo-container">', unsafe_allow_html=True)
# 注意：你需要把刚才那张 Logo 上传到 GitHub 或图床，替换下面的 URL
st.image("https://www.ul.com/themes/custom/ul_theme/logo.svg", width=220) 
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<h1 class="main-title">实验室设备登记系统</h1>', unsafe_allow_html=True)

# --- 登记表单 ---
with st.form("lab_form", clear_on_submit=True):
    staff_id = st.text_input("👤 工号 (Staff ID)", placeholder="Enter your ID")
    
    action_type = st.radio("📝 操作类型", ["领用 (Check-out)", "归还 (Return)"], horizontal=True)
    
    device_name = st.selectbox("📦 设备名称", ["请选择设备"] + list(DEVICE_MAP.keys()))
    
    device_id = st.text_input("🔢 设备编号", placeholder="Input Device Number")
    
    st.markdown("<br>", unsafe_allow_html=True)
    submit_btn = st.form_submit_button("确认提交 (SUBMIT)")

# --- 提交逻辑 ---
if submit_btn:
    if not staff_id or device_name == "请选择设备" or not device_id:
        st.warning("请完整填写所有信息 (Please complete all fields)")
    else:
        try:
            entry = {
                "staff_id": staff_id,
                "action_type": action_type.split(" ")[0], # 只存中文部分
                "device_name": device_name,
                "device_id": device_id
            }
            supabase.table("lab_records").insert(entry).execute()
            st.success(f"✅ 提交成功 (Success)! {device_name} - {device_id}")
            st.balloons()
        except Exception as e:
            st.error(f"Error: {e}")

# --- 管理员后台 (极简设计) ---
st.markdown("<br><br>", unsafe_allow_html=True)
with st.expander("📊 历史记录查询 (History Logs)"):
    try:
        response = supabase.table("lab_records").select("*").order("created_at", desc=True).execute()
        if response.data:
            df = pd.DataFrame(response.data)
            df = df[['staff_id', 'action_type', 'device_name', 'device_id', 'created_at']]
            df.columns = ["工号", "操作", "设备", "编号", "时间"]
            st.dataframe(df, use_container_width=True)
            
            csv = df.to_csv(index=False).encode('utf_8_sig')
            st.download_button("📥 导出 Excel", csv, "UL_Lab_Records.csv", "text/csv")
    except:
        st.write("Wait for data...")