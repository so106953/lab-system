import streamlit as st
from supabase import create_client, Client
import pandas as pd
import base64
import io

# --- 1. 数据库配置 ---
URL = "https://xcrbvvlsbjsmxaepkdbl.supabase.co"
KEY = "sb_publishable_QYXt0Fs5YKpCBXxCjdb4sg_9y7rkksj"
supabase: Client = create_client(URL, KEY)

# --- 2. 设备清单 ---
DEVICE_MAP = {
    "直流电源": [], "万用表": [], "电流钳": [], "示波器": [],
    "电子负载": [], "游标卡尺": [], "烤箱": [], "环境箱": [],
    "Datalogger": [], "电压探头": [], "高压探棒": []
}

# --- 3. 极致全面屏定制 ---
st.set_page_config(page_title="UL设备登记", layout="centered")

def get_base64_image(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

img_base64 = get_base64_image("IMG_4614.jpeg")

# 全面屏 Meta 标签：让手机浏览器将其识别为独立 App
pwa_meta = """
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
"""
st.markdown(pwa_meta, unsafe_allow_html=True)

# 核心 CSS：锁定配色 + 消除边框 + 全屏适配
style = f"""
    <style>
    /* --- A. 彻底消除官方标志 --- */
    header, footer, [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] {{
        display: none !important;
    }}
    [data-testid="stStatusWidget"], [data-testid="manage-app-button"], .viewerBadge_container__1QSob {{
        display: none !important;
        position: fixed !important;
        left: -9999px !important;
    }}

    /* --- B. 自动配色逻辑：消除深色模式白边 --- */
    :root {{
        --bg-color: #FFFFFF;
        --text-color: #000000;
        --card-bg: #FFFFFF;
        --input-bg: #F8F9FA;
    }}

    @media (prefers-color-scheme: dark) {{
        :root {{
            --bg-color: #0E1117;
            --text-color: #FFFFFF;
            --card-bg: #1A1C23;
            --input-bg: #262730;
        }}
    }}

    /* 关键：将背景色应用到最外层 HTML，消除白边 */
    html, body, [data-testid="stAppViewContainer"], .stApp {{
        background-color: var(--bg-color) !important;
        color: var(--text-color) !important;
        margin: 0 !important;
        padding: 0 !important;
    }}

    /* 强制文字颜色 */
    h1, h2, h3, p, label, span, div {{
        color: var(--text-color) !important;
        font-weight: 600 !important;
    }}

    /* --- C. 全屏水印 --- */
    .stApp::before {{
        content: ""; position: fixed; top: 0; left: 0; bottom: 0; right: 0;
        background-image: url("data:image/jpeg;base64,{img_base64}");
        background-repeat: no-repeat; background-position: center;
        background-size: 55%; opacity: 0.03; z-index: -1;
    }}

    /* --- D. 表单自适应（全面屏感） --- */
    div[data-testid="stForm"] {{
        border: none !important;
        border-radius: 0px !important; /* 手机端取消圆角实现全屏感 */
        background-color: var(--card-bg) !important;
        padding: 20px !important;
        box-shadow: none !important;
    }}
    
    /* 电脑端显示为卡片，手机端铺满 */
    @media (min-width: 768px) {{
        div[data-testid="stForm"] {{
            max-width: 500px !important;
            margin: 20px auto !important;
            border-radius: 24px !important;
            box-shadow: 0 15px 50px rgba(0,0,0,0.1) !important;
        }}
    }}

    /* 隐藏滚动条 */
    ::-webkit-scrollbar {{ display: none; }}

    /* 确认按钮 (亮绿色) */
    .stButton>button {{
        width: 100%; border-radius: 12px !important; height: 3.8em !important;
        background-color: #28A745 !important; color: #FFFFFF !important;
        font-weight: bold !important; font-size: 18px !important; border: none !important;
    }}
    </style>
"""
st.markdown(style, unsafe_allow_html=True)

# --- 4. 页面内容 ---
st.markdown("<div style='text-align: center; padding-top: 20px;'>", unsafe_allow_html=True)
if img_base64:
    st.image("IMG_4614.jpeg", width=180)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; margin-bottom: 0px;'>设备领用登记表</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; opacity: 0.6; font-size: 12px;'>UL Solutions Asset Registry</p>", unsafe_allow_html=True)

with st.form("lab_form", clear_on_submit=True):
    staff_id = st.text_input("工号 (Staff ID)", placeholder="请输入工号")
    action_type = st.radio("操作类型", ["领用 (Check-out)", "归还 (Return)"], horizontal=True)
    device_name = st.selectbox("设备名称", ["请选择类型"] + list(DEVICE_MAP.keys()))
    device_id = st.text_input("设备编号 (SN)", placeholder="手动输入编号")
    st.markdown("<br>", unsafe_allow_html=True)
    submit_btn = st.form_submit_button("确认提交登记 (SUBMIT)")

if submit_btn:
    if not staff_id or device_name == "请选择类型" or not device_id:
        st.warning("⚠️ 请填完所有项再提交")
    else:
        try:
            entry = {"staff_id": staff_id, "action_type": "领用" if "领用" in action_type else "归还", "device_name": device_name, "device_id": device_id}
            supabase.table("lab_records").insert(entry).execute()
            st.success("✅ 登记成功！")
            st.balloons()
        except:
            st.error("提交失败，请重试")

# --- 5. 后台管理 ---
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("📊 历史记录"):
    try:
        res = supabase.table("lab_records").select("*").order("created_at", desc=True).execute()
        if res.data:
            df = pd.DataFrame(res.data)
            df['created_at'] = pd.to_datetime(df['created_at']).dt.tz_convert('Asia/Shanghai').dt.strftime('%Y-%m-%d %H:%M:%S')
            df_display = df[['staff_id', 'action_type', 'device_name', 'device_id', 'created_at']]
            df_display.columns = ["工号", "类型", "设备", "编号", "时间"]
            st.dataframe(df_display, use_container_width=True)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_display.to_excel(writer, index=False, sheet_name='Records')
            excel_data = output.getvalue()
            st.download_button("📥 导出 Excel (.xlsx)", excel_data, f"UL_Records.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except:
        st.write("无数据")