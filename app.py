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

# --- 3. 极致视觉定制 ---
st.set_page_config(page_title="UL设备登记", layout="centered")

def get_base64_image(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

# 获取 Logo 的 Base64 以保证原画质无损加载
img_base64 = get_base64_image("IMG_4614.jpeg")

# 全面屏与 PWA 支持
pwa_meta = """
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
"""
st.markdown(pwa_meta, unsafe_allow_html=True)

# 核心 CSS：原画居中 + 自动色调 + 彻底去标
style = f"""
    <style>
    /* 彻底抹除官方标志 */
    header, footer, [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] {{
        display: none !important;
    }}
    [data-testid="stStatusWidget"], [data-testid="manage-app-button"], .viewerBadge_container__1QSob {{
        display: none !important;
        position: fixed !important;
        left: -9999px !important;
    }}

    /* 自动配色：深浅模式感知 */
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

    /* 消除四周白边，背景融合 */
    html, body, [data-testid="stAppViewContainer"], .stApp {{
        background-color: var(--bg-color) !important;
        color: var(--text-color) !important;
        margin: 0 !important;
        padding: 0 !important;
    }}

    /* 文字对比度增强 */
    h1, h2, h3, p, label, span, div, .stMarkdown {{
        color: var(--text-color) !important;
        font-weight: 600 !important;
    }}

    /* Logo 绝对居中容器 */
    .logo-box {{
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 20px 0;
        width: 100%;
    }}
    .logo-box img {{
        max-width: 200px; /* 电脑端大小 */
        height: auto;
    }}
    @media (max-width: 768px) {{
        .logo-box img {{
            max-width: 160px; /* 手机端稍小一点，更协调 */
        }}
    }}

    /* 全屏背景水印 */
    .stApp::before {{
        content: ""; position: fixed; top: 0; left: 0; bottom: 0; right: 0;
        background-image: url("data:image/jpeg;base64,{img_base64}");
        background-repeat: no-repeat; background-position: center;
        background-size: 60%; opacity: 0.02; z-index: -1;
    }}

    /* 表单自适应：手机铺满，电脑居中卡片 */
    div[data-testid="stForm"] {{
        border: none !important;
        background-color: var(--card-bg) !important;
        padding: 20px !important;
    }}
    @media (min-width: 768px) {{
        div[data-testid="stForm"] {{
            max-width: 500px !important;
            margin: 20px auto !important;
            border-radius: 24px !important;
            box-shadow: 0 15px 50px rgba(0,0,0,0.1) !important;
            border: 1px solid rgba(128,128,128,0.1) !important;
        }}
    }}

    /* 绿色按钮 */
    .stButton>button {{
        width: 100%; border-radius: 12px !important; height: 3.8em !important;
        background-color: #28A745 !important; color: #FFFFFF !important;
        font-weight: bold !important; font-size: 1.1em !important; border: none !important;
    }}
    
    /* 隐藏滚动条 */
    ::-webkit-scrollbar {{ display: none; }}
    </style>
"""
st.markdown(style, unsafe_allow_html=True)

# --- 4. 页面内容渲染 ---

# 使用 HTML 确保 Logo 绝对居中并保持原画质
if img_base64:
    st.markdown(f'''
        <div class="logo-box">
            <img src="data:image/jpeg;base64,{img_base64}">
        </div>
    ''', unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; margin-top: 0px;'>设备领用登记表</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; opacity: 0.6; font-size: 13px; margin-bottom: 20px;'>UL Solutions Laboratory Asset Registry</p>", unsafe_allow_html=True)

# 登记表单
with st.form("lab_form", clear_on_submit=True):
    staff_id = st.text_input("工号 (Staff ID)", placeholder="请输入您的工号")
    action_type = st.radio("操作类型", ["领用 (Check-out)", "归还 (Return)"], horizontal=True)
    device_name = st.selectbox("设备名称", ["请选择设备类型"] + list(DEVICE_MAP.keys()))
    device_id = st.text_input("设备编号 (SN)", placeholder="手动输入设备唯一编号")
    
    st.markdown("<div style='padding-top:10px;'></div>", unsafe_allow_html=True)
    submit_btn = st.form_submit_button("确认提交登记 (SUBMIT)")

if submit_btn:
    if not staff_id or device_name == "请选择设备类型" or not device_id:
        st.warning("⚠️ 请完整填写所有信息后再提交")
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
        except:
            st.error("❌ 提交失败，请检查网络后重试")

# --- 5. 管理员后台（数据导出） ---
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("📊 查看记录 (管理人员专用)"):
    try:
        res = supabase.table("lab_records").select("*").order("created_at", desc=True).execute()
        if res.data:
            df = pd.DataFrame(res.data)
            # 转换北京时间
            df['created_at'] = pd.to_datetime(df['created_at']).dt.tz_convert('Asia/Shanghai').dt.strftime('%Y-%m-%d %H:%M:%S')
            df_display = df[['staff_id', 'action_type', 'device_name', 'device_id', 'created_at']]
            df_display.columns = ["工号", "类型", "设备", "编号", "登记时间"]
            st.dataframe(df_display, use_container_width=True)
            
            # 生成真正的 Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_display.to_excel(writer, index=False, sheet_name='Records')
            excel_data = output.getvalue()
            
            st.download_button(
                label="📥 导出为 Excel (.xlsx) 文档",
                data=excel_data,
                file_name=f"UL_Device_Records.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except:
        st.write("暂无记录。")