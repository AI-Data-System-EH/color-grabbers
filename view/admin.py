# 관리자 페이지

import time

import pandas as pd
import streamlit as st
import yaml
from dataclass.colors import Colors
from dataclass.game import GamePlayerStatus
from dataclass.participant import Participant
from dataclass.qrcode import QRCode, QRCodeStatus
from dataclass.supabase import Supabase
from yaml.loader import SafeLoader


def admin_page(supabase: Supabase):
    st.title("관리자 페이지")
    st.sidebar.header("관리자 기능")
    option = st.sidebar.selectbox(
        "관리자 작업 선택", ["참가자 등록 및 보기", "로그 보기", "참가자 QR 코드 조회"]
    )

    if st.sidebar.button("데이터 초기화"):
        st.session_state["participants"] = None
        st.session_state["config_temp"] = None
        st.sidebar.success("인터페이스 및 캐시 초기화 완료!")

    if option == "참가자 등록 및 보기":
        st.subheader("참가자 등록")
        participants: pd.DataFrame | None = st.session_state.get(
            "participants", supabase.get_table_dataframe("participants")
        )
        if participants is None or participants.empty:
            participants = Participant.create_empty_dataframe()

        config_temp = st.session_state.get("config_temp")
        if config_temp is None:
            config_temp = st.session_state["config"]
        # st.write(config_temp["credentials"]["usernames"])

        r1_c1, r1_c2 = st.columns(2)
        r2_c1, r2_c2 = st.columns(2)

        with r1_c1:
            username = st.text_input("참가자 이름", placeholder="예) 홍길동")
        with r1_c2:
            password = st.text_input("참가자 비밀번호", placeholder="예) 123456", type="password")

        with r2_c1:
            color = st.selectbox(
                "참가자 색깔",
                [None] + [color.value for color in Colors.__members__.values()],
            )
        with r2_c2:
            roles = st.multiselect("참가자 권한", ["admin", "editor", "viewer"])

        if st.button("참가자 추가"):
            if username == "":
                st.error("이름을 입력해주세요.")
            elif password == "":
                st.error("비밀번호를 입력해주세요.")
            elif username in participants["name"].values:
                st.error("이미 존재하는 참가자입니다.")
            else:
                config_temp["credentials"]["usernames"][username] = {
                    "password": password,
                    "email": None,
                    "first_name": None,
                    "last_name": None,
                    "roles": roles,
                }

                # 1부터 최대 ID +1까지 중 사용되지 않은 가장 작은 ID 선택
                if participants["id"].empty:
                    id = 1
                else:
                    id = min(set(range(1, max(participants["id"]) + 2)) - set(participants["id"]))

                # 참가자 DB용 dataframe 추가
                participants = pd.concat(
                    [
                        participants,
                        Participant(
                            id=id,
                            name=username,
                            color=color,
                            group_head=color,
                            group_tail=color,
                            status=GamePlayerStatus.INACTIVE.value,
                            qr_status=QRCodeStatus.HIDDEN.value,
                            penalty_time=None,
                        ).to_dataframe(),
                    ],
                    ignore_index=True,
                )

        st.subheader("팀 색깔 배정")
        if st.button("색깔 랜덤 배정"):
            participant_objects = Colors.assign_uniform_color(
                Participant.from_dataframe(participants)
            )
            participants = pd.concat(
                [participant.to_dataframe() for participant in participant_objects],
                ignore_index=True,
            )
            st.success(f"참가자 {len(participant_objects)}명의 색깔이 배정되었습니다.")

        st.session_state["participants"] = participants
        st.session_state["config_temp"] = config_temp
        st.subheader("참가자 목록")
        st.write(f"총 {len(participants)}명의 참가자가 있습니다.")
        st.data_editor(
            participants,
            use_container_width=True,
            hide_index=True,
            column_config={
                "id": "ID",
                "name": "이름",
                "color": "색깔",
                "group_head": "그룹 머리",
                "group_tail": "그룹 꼬리",
                "status": "참여상태",
                "qr_status": "QR 상태",
                "penalty_time": "패널티 종료",
            },
            column_order=[
                "id",
                "name",
                "color",
                "group_head",
                "group_tail",
                "status",
                "qr_status",
                "penalty_time",
            ],
        )

        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("원격 데이터베이스에 등록") and participants is not None:
                if participants.empty:
                    st.error("참가자 데이터가 없습니다.")
                elif any(participants["color"].isna()):
                    st.error("색깔 배정이 완료되지 않았습니다.")
                else:
                    # id 없는 데이터는 생성, id 있는 데이터는 업데이트
                    supabase.upsert_table_from_dataframe("participants", participants)

                    with open("./config.yaml", "w") as file:
                        yaml.dump(config_temp, file, default_flow_style=False)

                    st.success(f"총 {len(participants)}명의 참가자가 등록되었습니다.")
        with btn_col2:
            if st.button("원격 데이터베이스 초기화", type="primary"):
                supabase.delete_table_dataframe("participants")
                st.session_state["participants"] = None

                with open("./config_default.yaml", "r") as file:
                    st.session_state["config"] = yaml.load(file, Loader=SafeLoader)
                with open("./config.yaml", "w") as file:
                    yaml.dump(st.session_state["config"], file, default_flow_style=False)
                st.session_state["config_temp"] = None

                st.toast("참가자 데이터베이스 초기화 완료!", icon="🔄")
                time.sleep(2)
                st.rerun()

    elif option == "로그 보기":
        st.subheader("잡기 로그")
        logs = supabase.get_table_dataframe("logs")
        st.dataframe(logs, use_container_width=True, hide_index=True)

        if st.button("로그 초기화", type="primary"):
            supabase.delete_table_dataframe("logs")
            st.success("로그 초기화 완료!")

    elif option == "참가자 QR 코드 조회":
        st.subheader("참가자 QR 코드 조회")

        participants = supabase.get_table_dataframe("participants")
        if participants is None or participants.empty:
            st.error("참가자 테이블이 비어있습니다.")
            return

        selected_name = st.pills(
            "참가자 이름",
            participants["name"].unique(),
            key="qr_code_name_selectbox",
            help="참가자 이름을 선택해주세요.",
        )
        selected_user = participants[participants["name"] == selected_name]

        if selected_name is None:
            st.info("참가자 이름을 선택해주세요.")
        elif selected_user.empty:
            st.error("사용자 정보를 확인할 수 없습니다.")
        else:
            qr_image, qr_code_data = QRCode.qrcode_with_capture_param(selected_name)
            st.image(
                qr_image,
                caption=f"{selected_name}의 QR 코드",
                use_container_width=True,
            )
            st.link_button("QR 코드 링크 바로가기", qr_code_data, icon="🔗")


if "admin" in (st.session_state["roles"] or []):
    supabase = st.session_state.get("supabase")
    if supabase is None:
        st.error("Supabase 인스턴스가 없습니다.")
    else:
        admin_page(supabase)
else:
    st.error("관리자 권한이 필요합니다.")
