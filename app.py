import streamlit as st
from supabase import create_client, Client
import pandas as pd

# --- 数据库连接配置 (已根据你提供的信息填入) ---
URL = "https://xcrbvvlsbjsmxaepkdbl.supabase.co"
KEY = "sb_publishable_QYXt0Fs5YKpCBXxCjdb4sg_9y7rkksj"
supabase: Client = create_client(URL, KEY)

# --- 实验室设备清单 (你可以随时在下面修改名称和编号) ---
DEVICE_MAP = {
    "直流电源": [],
    "万用表": [],
    "电流钳": [],
    "示波器": []
}

# 页面设置
st.set_page_config(page_title="实验室设备管理系统", layout="centered")
st.title("🔬 设备领用与归还登记")
st.markdown("人员扫码后，请如实填写以下信息进行登记")

# --- 填写表单 ---
with st.form("lab_form", clear_on_submit=True):
    staff_id = st.text_input("工号 (Staff ID)", placeholder="请输入您的工号")
    
    action_type = st.radio("操作类型", ["领用", "归还"], horizontal=True)
    
    # 级联选择：选了名称才会出现对应的编号
    device_name = st.selectbox("设备名称", ["请选择"] + list(DEVICE_MAP.keys()))
    
    device_ids = DEVICE_MAP.get(device_name, [])
    device_id = st.selectbox("设备编号", device_ids)
    
    submit_btn = st.form_submit_button("确认提交登记", use_container_width=True)

# --- 提交逻辑 ---
if submit_btn:
    if not staff_id or device_name == "请选择":
        st.error("❌ 请完整填写工号并选择设备！")
    else:
        try:
            # 将数据插入到刚才你在 Supabase 建好的 lab_records 表中
            entry = {
                "staff_id": staff_id,
                "action_type": action_type,
                "device_name": device_name,
                "device_id": device_id
            }
            supabase.table("lab_records").insert(entry).execute()
            st.success(f"✅ 登记成功！{device_name} ({device_id}) 已记录。")
            st.balloons()
        except Exception as e:
            st.error(f"提交出错，请联系管理员: {e}")

# --- 管理员后台 (导出 Excel) ---
st.markdown("---")
with st.expander("📊 管理员后台 (查看记录与导出电子档)"):
    try:
        # 从数据库抓取所有数据，按时间倒序排列
        response = supabase.table("lab_records").select("*").order("created_at", desc=True).execute()
        if response.data:
            df = pd.DataFrame(response.data)
            # 整理表格列名
            df = df[['id', 'staff_id', 'action_type', 'device_name', 'device_id', 'created_at']]
            df.columns = ["序号", "工号", "操作类型", "设备名称", "设备编号", "登记时间"]
            
            st.write("最近登记记录：")
            st.dataframe(df)
            
            # 导出 Excel (CSV格式，带BOM头防止Excel中文乱码)
            csv = df.to_csv(index=False).encode('utf_8_sig')
            st.download_button(
                label="📥 导出完整电子档 (Excel)",
                data=csv,
                file_name="实验室设备领用记录表.csv",
                mime="text/csv"
            )
        else:
            st.info("目前还没有登记记录。")
    except:
        st.write("等待首次数据提交...")
