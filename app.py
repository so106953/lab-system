import streamlit as st
from supabase import create_client, Client
import pandas as pd
import base64
import io

# --- 1. 数据库配置 ---
URL = "https://xcrbvvlsbjsmxaepkdbl.supabase.co"
KEY = "sb_publishable_QYXt0Fs5YKpCBXxCjdb4sg_9y7rkksj"
supabase: Client = create_client(URL, KEY)

# --- 2. 详细的分组设备清单 (你可以随时在 [] 里增加各组特定的设备) ---
GROUP_CONFIG = {
    "components": ["示波器", "万用表", "直流电源", "LCR表"],
    "PV": ["光伏测试仪", "万用表", "直流电源", "电子负载"],
    "tools": ["游标卡尺", "扭力计", "示波器", "万用表"],
    "HVAC": ["环境箱", "温度记录仪", "压力计", "流量计"],
    "Lingting": ["功率计", "积分球", "光谱仪", "万用表"],
    "PC组": ["示波器", "万用表", "电子负载", "Datalogger"],
    "小家电": ["功率计", "安规测试仪", "温升仪", "示波器"],
    "洗衣机": ["环境箱", "流量计", "转速表", "温升仪"],
    "材料": ["拉力计", "硬度计", "烤箱", "游标卡尺"],
    "电缆": ["弯曲试验机", "耐压仪", "电阻测试仪", "卡尺"],
    "默认": ["直流电源", "万用表", "电流钳", "示波器", "电子负载", "游标卡尺", "烤箱", "环境箱", "Datalogger", "电压探头", "高压探棒"]
}

# --- 3. 获取网址里的组别参数 ---
query_params = st.query_params
target_group = query_params.get("group", "默认")

# --- 4. 极致视觉定制 ---
st.set_page_config(page_title=f"{target_group}登记表", layout="centered")

def get_base64_image(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except: return ""

img_base64 = get_base64_image("IMG_4614.jpeg")

style = f"""
    <style>
    /* 彻底抹除官方标志 */
    header, footer, [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] {{display: none !important;}}
    [data-testid="stStatusWidget"], [data-testid="manage-app-button"], .viewerBadge_container__1QSob,
    div[class*="viewerBadge"], div[class*="StyledStatusWidget"] {{
        display: none !important; position: fixed !important; left: -9999px !important;
    }}

    /* 自动配色：深浅模式感知 */
    :root {{ --bg-color: #FFFFFF; --text-color: #000000; --card-bg: #FFFFFF; --input-bg: #F8F9FA; }}
    @media (prefers-color-scheme: dark) {{
        :root {{ --bg-color: #0E1117; --text-color: #FFFFFF; --card-bg: #1A1C23; --input-bg: #2D2F39; }}
    }}

    html, body, [data-testid="stAppViewContainer"], .stApp {{
        background-color: var(--bg-color) !important; color: var(--text-color) !important;
        margin: 0 !important; padding: 0 !important;
    }}

    h1, h2, label, span, div {{ color: var(--text-color) !important; font-weight: 600 !important; }}

    /* Logo 绝对居中 */
    .logo-box {{ display: flex; justify-content: center; padding: 20px 0; }}
    .logo-box img {{ max-width: 180px; height: auto; }}

    /* 水印 */
    .stApp::before {{
        content: ""; position: fixed; top: 0; left: 0; bottom: 0; right: 0;
        background-image: url("data:image/jpeg;base64,{img_base64}");
        background-repeat: no-repeat; background-position: center; background-size: 50%; opacity: 0.02; z-index: -1;
    }}

    /* 表单全屏适配 */
    div[data-testid="stForm"] {{
        border: none !important; background-color: var(--card-bg) !important; padding: 20px !important;
    }}
    @media (min-width: 768px) {{
        div[data-testid="stForm"] {{ max-width: 500px !important; margin: 20px auto !important; border-radius: 24px !important; border: 1px solid rgba(128,128,128,0.1) !important; box-shadow: 0 15px 50px rgba(0,0,0,0.1) !important; }}
    }}

    /* 绿色按钮 */
    .stButton>button {{
        width: 100%; border-radius: 12px !important; height: 3.8em !important;
        background-color: #28A745 !important; color: #FFFFFF !important; font-weight: bold !important; border: none !important;
    }}
    ::-webkit-scrollbar {{ display: none; }}
    </style>
"""
st.markdown(style, unsafe_allow_html=True)

# --- 5. 页面内容 ---
if img_base64:
    st.markdown(f'<div class="logo-box"><img src="data:image/jpeg;base64,{img_base64}"></div>', unsafe_allow_html=True)

st.markdown(f"<h2 style='text-align: center; margin-top: 0px;'>{target_group} 设备领用登记</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; opacity: 0.6; font-size: 13px;'>UL Solutions Asset Registry System</p>", unsafe_allow_html=True)

with st.form("lab_form", clear_on_submit=True):
    staff_id = st.text_input("工号 (Staff ID)", placeholder="请输入您的工号")
    action_type = st.radio("操作类型", ["领用 (Check-out)", "归还 (Return)"], horizontal=True)
    
    # 核心：根据参数识别显示对应组别的设备
    group_devices = GROUP_CONFIG.get(target_group, GROUP_CONFIG["默认"])
    device_name = st.selectbox("设备名称", ["请选择设备类型"] + group_devices)
    
    device_id = st.text_input("设备编号 (SN)", placeholder="请输入设备唯一编号")
    submit_btn = st.form_submit_button("确认提交登记 (SUBMIT)")

if submit_btn:
    if not staff_id or device_name == "请选择设备类型" or not device_id:
        st.error("❌ 请完整填写所有信息后再提交")
    else:
        try:
            entry = {
                "staff_id": staff_id,
                "action_type": "领用" if "领用" in action_type else "归还",
                "device_name": device_name,
                "device_id": device_id,
                "lab_group": target_group
            }
            supabase.table("lab_records").insert(entry).execute()
            st.success(f"✅ {target_group} 登记成功！")
            st.balloons()
        except Exception as e:
            st.error(f"提交出错: {e}")

# --- 6. 管理员后台（按组筛选） ---
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("📊 查看记录 (管理人员专用)"):
    try:
        res = supabase.table("lab_records").select("*").order("created_at", desc=True).execute()
        if res.data:
            df = pd.DataFrame(res.data)
            df['created_at'] = pd.to_datetime(df['created_at']).dt.tz_convert('Asia/Shanghai').dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # 后台按组别筛选
            view_group = st.selectbox("筛选查看组别", ["全部"] + list(GROUP_CONFIG.keys()))
            if view_group != "全部":
                df = df[df['lab_group'] == view_group]
                
            df_display = df[['staff_id', 'action_type', 'device_name', 'device_id', 'lab_group', 'created_at']]
            df_display.columns = ["工号", "类型", "设备", "编号", "所属组", "时间"]
            st.dataframe(df_display, use_container_width=True)
            
            # 导出 Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_display.to_excel(writer, index=False, sheet_name='Records')
            st.download_button(f"📥 导出 {view_group} Excel (.xlsx)", output.getvalue(), f"UL_{view_group}_Records.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except:
        st.write("暂无记录。")