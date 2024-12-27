# 공지사항 페이지

from datetime import datetime

import streamlit as st

from dataclass.qrcode import QRCode, QRCodeStatus
from dataclass.supabase import Supabase


# 패널티로 노출된 사용자의 QR 코드 버튼
def revealed_user_qr_code_button(supabase: Supabase, login_user: dict):
    if not st.session_state.get("authentication_status"):
        return

    participants = supabase.get_table_dataframe("participants")
    if participants is None:
        st.error("참가자 정보를 확인할 수 없습니다.")
        return

    # login_user = st.session_state.get("login_user")
    # if login_user is None:
    #     st.error("로그인 정보를 확인할 수 없습니다.")
    #     return

    user = participants.loc[participants["name"] == login_user["name"]].iloc[0]

    if user["qr_status"] == QRCodeStatus.REVEALED.value:
        # 마지막 실패한 사용자의 QR 코드 버튼

        # penalty_time 기준 내림차순 정렬, 값이 비어있지 않은 첫 번째 행
        last_fail_user = participants.sort_values(
            by="penalty_time", ascending=False
        ).dropna(subset=["penalty_time"])

        if not last_fail_user.empty:
            last_fail_user = last_fail_user.iloc[0]

            qr_image, qr_code_data = QRCode.qrcode_with_capture_param(
                last_fail_user["name"], no_penalty=True
            )

            # 버튼 클릭 시 qr_code_data 링크로 이동
            st.link_button(
                f"마지막 실패한 **{last_fail_user['name']}** : 잡으려면 여기를 누르세요! (기회는 한 번 뿐이에요.)",
                url=qr_code_data,
                icon="😀",
                help="자신있나요?",
                use_container_width=True,
            )


# 메인 페이지: 공지사항
def notice_page(supabase: Supabase):
    st.title("📣 잡기 기록")

    if st.button("새로고침"):
        st.rerun()

    def log_to_itemcard(log_df):
        for _, row in log_df.iterrows():
            timestamp = row["created_at"]
            message = row["message"]
            result = row["result"]

            # 2024-12-22T21:04:13.482979+00:00
            # -> 2024-12-22 21:04:13
            timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f+00:00")
            timestamp = timestamp.strftime("%Y-%m-%d %H:%M")

            st.markdown(f":gray[[{timestamp}]] {result} {message}")

    log_df = supabase.get_table_dataframe("logs")

    with st.container(key="log_container"):
        if log_df is None or log_df.empty:
            st.write("아직 기록된 것이 없습니다. 😂")
        else:
            log_to_itemcard(log_df)


supabase = st.session_state.get("supabase")
login_user = st.session_state.get("login_user")
if supabase is None:
    st.error("Supabase 인스턴스가 없습니다.")
else:
    if login_user is not None:
        revealed_user_qr_code_button(supabase, login_user)
    notice_page(supabase)
