import streamlit as st
from supabase import create_client, Client
import pandas as pd
import base64
import io

# --- 1. 数据库配置 ---
URL = "https://xcrbvvlsbjsmxaepkdbl.supabase.co"
KEY = "sb_publishable_QYXt0Fs5YKpCBXxCjdb4sg_9y7rkksj"
supabase: Client = create_client(URL, KEY)

# --- 2. 设备清单配置 ---
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
    "默认": ["请联系管理员配置设备"]
}

# --- 3. 页面基础设置 ---
st.set_page_config(page_title="UL设备管理系统", layout="centered")

def get_base64_image(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except: return ""

img_base64 = get_base64_image("IMG_4614.jpeg")

# 终极 CSS：自动配色 + 彻底去标志 + 全面屏适配
style = f"""
    <style>
    header, footer, [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] {{display: none !important;}}
    [data-testid="stStatusWidget"], [data-testid="manage-app-button"], .viewerBadge_container__1QSob,
    div[class*="viewerBadge"], div[class*="StyledStatusWidget"] {{
        display: none !important; position: fixed !important; left: -9999px !important;
    }}
    :root {{ --bg-color: #FFFFFF; --text-color: #000000; --card-bg: #FFFFFF; }}
    @media (prefers-color-scheme: dark) {{
        :root {{ --bg-color: #0E1117; --text-color: #FFFFFF; --card-bg: #1A1C23; }}
        input, .stSelectbox div {{ background-color: #2D2F39 !important; color: white !important; }}
    }}
    html, body, [data-testid="stAppViewContainer"], .stApp {{
        background-color: var(--bg-color) !important; color: var(--text-color) !important;
    }}
    h1, h2, label, span, div {{ color: var(--text-color) !important; font-weight: 600 !important; }}
    .logo-box {{ display: flex; justify-content: center; padding: 20px 0; }}
    .logo-box img {{ max-width: 180px; height: auto; }}
    .stApp::before {{
        content: ""; position: fixed; top: 0; left: 0; bottom: 0; right: 0;
        background-image: url("data:image/jpeg;base64,{img_base64}");
        background-repeat: no-repeat; background-position: center;
        background-size: 50%; opacity: 0.02; z-index: -1;
    }}
    div[data-testid="stForm"] {{
        border: none !important; background-color: var(--card-bg) !important; padding: 20px !important;
    }}
    @media (min-width: 768px) {{
        div[data-testid="stForm"] {{ 
            max-width: 500px !important; margin: 20px auto !important; 
            border-radius: 24px !important; border: 1px solid rgba(128,128,128,0.1) !important; 
            box-shadow: 0 15px 50px rgba(0,0,0,0.1) !important; 
        }}
    }}
    .stButton>button {{
        width: 100%; border-radius: 12px !important; height: 3.8em !important;
        background-color: #28A745 !important; color: #FFFFFF !important; font-weight: bold !important;
    }}
    ::-webkit-scrollbar {{ display: none; }}
    </style>
"""
st.markdown(style, unsafe_allow_html=True)

# --- 4. 识别当前组别 (核心逻辑) ---
query_params = st.query_params
# 如果扫的是通用码，默认为“默认”；如果扫的是专用码，自动锁定组别
current_group = query_params.get("group", "默认")

# --- 5. 页面内容渲染 ---
if img_base64:
    st.markdown(f'<div class="logo-box"><img src="data:image/jpeg;base64,{img_base64}"></div>', unsafe_allow_html=True)

# 动态标题：让用户知道他正在登记哪个组的设备
st.markdown(f"<h2 style='text-align: center; margin-top: 0px;'>{current_group} 组设备登记表</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; opacity: 0.6; font-size: 13px;'>UL Solutions Laboratory Asset Portal</p>", unsafe_allow_html=True)

# --- 登记表单 ---
with st.form("lab_form", clear_on_submit=True):
    staff_id = st.text_input("👤 领用工号 (Staff ID)", placeholder="请输入工号")
    
    # 组别选择：如果扫的是特定组的码，该项会自动选好
    group_list = list(GROUP_CONFIG.keys())
    default_idx = group_list.index(current_group) if current_group in group_list else group_list.index("默认")
    selected_group = st.selectbox("🏢 确认所属组别", group_list, index=default_idx)
    
    action_type = st.radio("📝 操作类型", ["领用 (Check-out)", "归还 (Return)"], horizontal=True)
    
    # 设备名称：只显示该组的设备，绝对不会混
    available_devices = GROUP_CONFIG.get(selected_group, GROUP_CONFIG["默认"])
    device_name = st.selectbox("📦 设备名称", ["请选择设备类型"] + available_devices)
    
    device_id = st.text_input("🔢 设备编号 (SN)", placeholder="请输入唯一设备号")
    
    st.markdown("<br>", unsafe_allow_html=True)
    submit_btn = st.form_submit_button("确认提交登记 (SUBMIT)")

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
                "device_id": device_id,
                "lab_group": selected_group
            }
            supabase.table("lab_records").insert(entry).execute()
            st.success(f"✅ 登记成功！已记入 {selected_group} 台账。")
            st.balloons()
        except Exception as e:
            st.error(f"提交出错: {e}")

# --- 6. 专属管理员后台 (只显示当前页面的组别数据) ---
st.markdown("<br><br>", unsafe_allow_html=True)
with st.expander(f"📊 {current_group} 组专属历史记录 (查看与导出)"):
    try:
        # 从数据库抓取数据
        res = supabase.table("lab_records").select("*").order("created_at", desc=True).execute()
        if res.data:
            df = pd.DataFrame(res.data)
            df['created_at'] = pd.to_datetime(df['created_at']).dt.tz_convert('Asia/Shanghai').dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # --- 核心：在这里强制过滤，只显示当前二维码对应的组别数据 ---
            # 如果是默认页面，显示全部；如果是特定组页面，只显示该组
            if current_group != "默认":
                df = df[df['lab_group'] == current_group]
            
            df_display = df[['staff_id', 'action_type', 'device_name', 'device_id', 'created_at']]
            df_display.columns = ["工号", "类型", "设备名称", "设备编号", "登记时间"]
            
            st.write(f"以下为 {current_group} 组的最近记录：")
            st.dataframe(df_display, use_container_width=True)
            
            # 导出专属 Excel (.xlsx)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_display.to_excel(writer, index=False, sheet_name=f'{current_group}组记录')
            
            st.download_button(
                label=f"📥 导出 {current_group} 组 Excel 文档",
                data=output.getvalue(),
                file_name=f"UL_{current_group}_Records.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except:
        st.write("暂无此组登记记录。")