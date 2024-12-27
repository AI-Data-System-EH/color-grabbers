# 내 정보 페이지

import streamlit as st

from dataclass.qrcode import QRCode


def my_info():
    name = st.session_state["username"]
    if name is None:
        st.error("로그인 후 이용해주세요.")
        return

    st.title(f"{name}의 QR 코드")

    # QR 코드 조회
    qr_image, qr_code_data = QRCode.qrcode_with_capture_param(name)
    st.image(qr_image, use_container_width=True, caption=qr_code_data)


my_info()
