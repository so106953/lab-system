import streamlit as st
from supabase import create_client, Client
import pandas as pd
import base64
import io

# --- 1. 数据库配置 ---
URL = "https://xcrbvvlsbjsmxaepkdbl.supabase.co"
KEY = "sb_publishable_QYXt0Fs5YKpCBXxCjdb4sg_9y7rkksj"
supabase: Client = create_client(URL, KEY)

# --- 2. 实验室所有组别清单 ---
ALL_GROUPS = ["components", "PV", "tools", "HVAC", "Lingting", "PC组", "小家电", "洗衣机", "材料", "电缆"]

# --- 3. 设备资产所属清单 ---
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

# --- 4. 极致视觉定制 ---
st.set_page_config(page_title="UL设备登记系统", layout="centered")

def get_base64_image(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except: return ""

img_base64 = get_base64_image("IMG_4614.jpeg")

style = f"""
    <style>
    header, footer, [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] {{display: none !important;}}
    [data-testid="stStatusWidget"], [data-testid="manage-app-button"], .viewerBadge_container__1QSob {{display: none !important; position: fixed !important; left: -9999px !important;}}
    :root {{ --bg-color: #FFFFFF; --text-color: #000000; --card-bg: #FFFFFF; }}
    @media (prefers-color-scheme: dark) {{
        :root {{ --bg-color: #0E1117; --text-color: #FFFFFF; --card-bg: #1A1C23; }}
        input, .stSelectbox div {{ background-color: #2D2F39 !important; color: white !important; }}
    }}
    html, body, .stApp {{ background-color: var(--bg-color) !important; color: var(--text-color) !important; }}
    h1, h2, label, span, div {{ color: var(--text-color) !important; font-weight: 600 !important; }}
    .logo-box {{ display: flex; justify-content: center; padding: 20px 0; }}
    .logo-box img {{ max-width: 180px; height: auto; }}
    .stApp::before {{
        content: ""; position: fixed; top: 0; left: 0; bottom: 0; right: 0;
        background-image: url("data:image/jpeg;base64,{img_base64}");
        background-repeat: no-repeat; background-position: center;
        background-size: 50%; opacity: 0.02; z-index: -1;
    }}
    div[data-testid="stForm"] {{ border-radius: 24px !important; background-color: var(--card-bg) !important; padding: 30px !important; box-shadow: 0 15px 50px rgba(0,0,0,0.1) !important; border: 1px solid rgba(128,128,128,0.1) !important; }}
    .stButton>button {{ width: 100%; border-radius: 12px !important; height: 3.8em !important; background-color: #28A745 !important; color: #FFFFFF !important; font-weight: bold !important; }}
    </style>
"""
st.markdown(style, unsafe_allow_html=True)

# --- 5. 获取 URL 参数（确定设备归属） ---
query_params = st.query_params
owning_group = query_params.get("group", "默认")

if img_base64:
    st.markdown(f'<div class="logo-box"><img src="data:image/jpeg;base64,{img_base64}"></div>', unsafe_allow_html=True)

st.markdown(f"<h2 style='text-align: center; margin-top: 0px;'>{owning_group} 资产登记表</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; opacity: 0.6; font-size: 13px;'>设备所有权: {owning_group} | 请填写领用信息</p>", unsafe_allow_html=True)

# --- 6. 登记表单 ---
with st.form("lab_form", clear_on_submit=True):
    # 领用人信息
    staff_id = st.text_input("👤 领用人工号 (Staff ID)", placeholder="请输入您的工号")
    staff_group = st.selectbox("🏢 领用人所属组别", ["请选择您的组别"] + ALL_GROUPS)
    
    st.markdown("---")
    
    # 动作与设备
    action_type = st.radio("📝 操作类型", ["领用 (Check-out)", "归还 (Return)"], horizontal=True)
    
    # 设备名称只显示本组资产
    available_devices = GROUP_CONFIG.get(owning_group, GROUP_CONFIG["默认"])
    device_name = st.selectbox("📦 资产名称", ["请选择资产名称"] + available_devices)
    device_id = st.text_input("🔢 资产编号 (SN)", placeholder="请输入设备上的唯一编号")
    
    st.markdown("<br>", unsafe_allow_html=True)
    submit_btn = st.form_submit_button("确认提交登记 (SUBMIT)")

if submit_btn:
    if not staff_id or staff_group == "请选择您的组别" or device_name == "请选择资产名称" or not device_id:
        st.error("❌ 请完整填写所有信息（包括您的组别）")
    else:
        try:
            entry = {
                "staff_id": staff_id,
                "staff_group": staff_group,    # 领用人的组
                "lab_group": owning_group,      # 设备所属的组 (从码里识别)
                "action_type": "领用" if "领用" in action_type else "归还",
                "device_name": device_name,
                "device_id": device_id
            }
            supabase.table("lab_records").insert(entry).execute()
            st.success(f"✅ 登记成功！{staff_group} 组 {staff_id} 已登记。")
            st.balloons()
        except Exception as e:
            st.error(f"系统报错: {e}")

# --- 7. 专属管理员后台 (隔离管理) ---
st.markdown("<br><br>", unsafe_allow_html=True)
with st.expander(f"📊 {owning_group} 组设备台账 (查看与导出)"):
    try:
        res = supabase.table("lab_records").select("*").order("created_at", desc=True).execute()
        if res.data:
            df = pd.DataFrame(res.data)
            df['created_at'] = pd.to_datetime(df['created_at']).dt.tz_convert('Asia/Shanghai').dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # --- 核心：只显示本组资产的借还记录 ---
            if owning_group != "默认":
                df = df[df['lab_group'] == owning_group]
            
            # 整理 Excel 导出的列
            df_display = df[['staff_id', 'staff_group', 'action_type', 'device_name', 'device_id', 'created_at']]
            df_display.columns = ["领用人工号", "领用人组别", "类型", "借出资产", "资产编号", "登记时间"]
            
            st.write(f"以下为 {owning_group} 资产的所有借还记录：")
            st.dataframe(df_display, use_container_width=True)
            
            # 导出 Excel (.xlsx)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_display.to_excel(writer, index=False, sheet_name='登记记录')
            
            st.download_button(
                label=f"📥 导出 {owning_group} 资产报表",
                data=output.getvalue(),
                file_name=f"UL_{owning_group}_Records.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except:
        st.write("暂无登记记录。")