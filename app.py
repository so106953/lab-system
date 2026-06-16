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

# --- 3. 极致视觉定制（自动色彩适配 + 彻底抹除标志） ---
st.set_page_config(page_title="设备领用登记表", layout="centered")

def get_base64_image(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

img_base64 = get_base64_image("IMG_4614.jpeg")

# 终极 CSS：智能感应深浅模式 + 物理清除官方标志
style = f"""
    <style>
    /* --- A. 彻底抹除 Streamlit 标志 --- */
    header, footer, [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] {{
        display: none !important;
        height: 0 !important;
    }}
    .stAppDeployButton, [data-testid="stAppDeployButton"], [data-testid="manage-app-button"],
    #stStatusWidget, [data-testid="stStatusWidget"], .viewerBadge_container__1QSob,
    div[class*="viewerBadge"] {{
        display: none !important;
        position: fixed !important;
        left: -9999px !important;
    }}

    /* --- B. 自动配色逻辑：感应深色/浅色模式 --- */
    /* 默认：浅色模式（白底黑字） */
    :root {{
        --bg-color: #FFFFFF;
        --text-color: #000000;
        --card-bg: #FFFFFF;
        --input-bg: #F8F9FA;
        --border-color: #F0F0F0;
    }}

    /* 深色模式：系统设为黑色时自动触发 */
    @media (prefers-color-scheme: dark) {{
        :root {{
            --bg-color: #0E1117;
            --text-color: #FFFFFF;
            --card-bg: #1A1C23;
            --input-bg: #262730;
            --border-color: #31333F;
        }}
    }}

    .stApp {{
        background-color: var(--bg-color) !important;
        color: var(--text-color) !important;
    }}

    /* 强制所有文字颜色跟随系统模式 */
    h1, h2, h3, p, label, span, div, .stMarkdown {{
        color: var(--text-color) !important;
        font-weight: 600 !important;
    }}

    /* --- C. 水印背景 --- */
    .stApp::before {{
        content: ""; position: fixed; top: 0; left: 0; bottom: 0; right: 0;
        background-image: url("data:image/jpeg;base64,{img_base64}");
        background-repeat: no-repeat; background-position: center;
        background-size: 55%; opacity: 0.03; z-index: -1;
    }}

    /* --- D. 表单卡片自适应 --- */
    div[data-testid="stForm"] {{
        border: 1px solid var(--border-color) !important;
        border-radius: 24px !important;
        background-color: var(--card-bg) !important;
        padding: 30px !important;
        box-shadow: 0 15px 50px rgba(0,0,0,0.1) !important;
    }}
    
    @media (min-width: 768px) {{
        [data-testid="stForm"] {{ max-width: 550px !important; margin: 0 auto !important; }}
    }}

    /* --- E. 按钮定制 (成功绿) --- */
    .stButton>button {{
        width: 100%; border-radius: 12px !important; height: 3.8em !important;
        background-color: #28A745 !important; color: #FFFFFF !important;
        font-weight: bold !important; font-size: 18px !important;
        border: none !important; margin-top: 15px !important;
        box-shadow: 0 8px 20px rgba(40,167,69,0.2) !important;
    }}

    /* 修正输入框在不同模式下的背景 */
    input, .stSelectbox div {{
        background-color: var(--input-bg) !important;
        color: var(--text-color) !important;
        border-radius: 10px !important;
    }}
    </style>
"""
st.markdown(style, unsafe_allow_html=True)

# --- 4. 页面内容 ---
if img_base64:
    st.markdown(f'<div style="text-align: center;"><img src="data:image/jpeg;base64,{img_base64}" width="200"></div>', unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; margin-top: 5px; margin-bottom: 0px;'>设备领用登记表</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; opacity: 0.6; font-size: 13px;'>UL Solutions Laboratory Asset Registry</p>", unsafe_allow_html=True)

with st.form("lab_form", clear_on_submit=True):
    staff_id = st.text_input("工号 (Staff ID)", placeholder="请输入您的工号")
    action_type = st.radio("操作类型", ["领用 (Check-out)", "归还 (Return)"], horizontal=True)
    device_name = st.selectbox("设备名称", ["请选择设备类型"] + list(DEVICE_MAP.keys()))
    device_id = st.text_input("设备编号 (SN)", placeholder="请输入唯一编号")
    st.markdown("<br>", unsafe_allow_html=True)
    submit_btn = st.form_submit_button("确认提交登记 (SUBMIT)")

if submit_btn:
    if not staff_id or device_name == "请选择设备类型" or not device_id:
        st.error("❌ 请完整填写所有信息！")
    else:
        try:
            entry = {"staff_id": staff_id, "action_type": "领用" if "领用" in action_type else "归还", "device_name": device_name, "device_id": device_id}
            supabase.table("lab_records").insert(entry).execute()
            st.success("✅ 登记成功！数据已实时备份。")
            st.balloons()
        except Exception as e:
            st.error(f"提交出错: {e}")

# --- 5. 管理员后台 - 导出 Excel ---
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
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_display.to_excel(writer, index=False, sheet_name='登记记录')
            excel_data = output.getvalue()

            st.download_button(
                label="📥 导出为标准 Excel 文档 (.xlsx)",
                data=excel_data,
                file_name=f"UL_Records_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except:
        st.write("暂无记录")