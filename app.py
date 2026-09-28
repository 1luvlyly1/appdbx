import os
import time
import importlib

import requests
import streamlit as st
from databricks.sdk import WorkspaceClient

SERVING_ENDPOINT = os.getenv("SERVING_ENDPOINT", "databricks-claude-sonnet-4-5")

st.set_page_config(page_title="Test Sonnet", layout="centered")


@st.cache_resource
def get_client():
    return WorkspaceClient()


def _parse_response(body):
    if "choices" in body:
        return body["choices"][0]["message"]["content"]
    if "content" in body:
        c = body["content"]
        if isinstance(c, list):
            for block in c:
                if isinstance(block, dict) and block.get("type") == "text":
                    return block.get("text", "")
        return str(c)
    raise KeyError(f"Khong nhan dang duoc response. Keys: {list(body.keys())}")


def hoi_sonnet(cau_hoi, max_tokens):
    w = get_client()
    host = w.config.host.rstrip("/")
    headers = w.config.authenticate()
    headers["Content-Type"] = "application/json"
    url = f"{host}/serving-endpoints/{SERVING_ENDPOINT}/invocations"
    payload = {
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": cau_hoi}],
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=180)
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:1000]}")
    return _parse_response(resp.json())


st.title("Test Sonnet trên Databricks App")
st.caption(f"Endpoint: `{SERVING_ENDPOINT}`")

cau_hoi = st.text_area("Câu hỏi", value="Xin chào, hãy giới thiệu ngắn về bạn bằng tiếng Việt.", height=120)
max_tokens = st.slider("max_tokens", 100, 8000, 1000, step=100)

if st.button("Hỏi Sonnet", type="primary"):
    if not cau_hoi.strip():
        st.warning("Nhập câu hỏi trước")
    else:
        with st.spinner("Đang gọi model..."):
            t0 = time.time()
            try:
                tra_loi = hoi_sonnet(cau_hoi, max_tokens)
                st.success(f"Xong sau {time.time() - t0:.1f}s")
                st.markdown(tra_loi)
            except Exception as e:
                st.error(f"Lỗi: {e}")

st.divider()

with st.expander("Kiểm tra môi trường"):
    try:
        headers = st.context.headers
        st.write("Người dùng:", headers.get("X-Forwarded-Email", "(không có header)"))
    except Exception as e:
        st.write("Không đọc được header người dùng:", e)

    st.write("DATABRICKS_HOST:", os.getenv("DATABRICKS_HOST", "(không có)"))
    st.write("DATABRICKS_CLIENT_ID:", "có" if os.getenv("DATABRICKS_CLIENT_ID") else "không có")
    st.write("SERVING_ENDPOINT:", SERVING_ENDPOINT)

    if st.button("Kiểm tra xác thực + thư viện"):
        try:
            me = get_client().current_user.me()
            st.write("Service principal:", me.user_name)
        except Exception as e:
            st.error(f"Xác thực lỗi: {e}")

        for ten in ["yaml", "PIL", "pypdfium2", "bs4", "fpdf", "weasyprint"]:
            try:
                mod = importlib.import_module(ten)
                st.write(f"{ten}: OK ({getattr(mod, '__version__', '')})")
            except Exception as e:
                st.write(f"{ten}: LỖI - {type(e).__name__}: {str(e)[:200]}")
