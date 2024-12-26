import urllib.parse
from datetime import datetime

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from dataclass.action import Action
from dataclass.colors import Colors
from dataclass.game import GameConfiguration, GamePlayerStatus
from dataclass.qrcode import QRCodeStatus
from dataclass.supabase import Supabase
from streamlit_theme import st_theme
from yaml.loader import SafeLoader


# 사이드바
def sidebar():
    with open("./config.yaml") as file:
        config = yaml.load(file, Loader=SafeLoader)

    st.sidebar.header("❤️ 참가자 정보")
    with st.empty():
        authenticator = stauth.Authenticate(
            config["credentials"],
            config["cookie"]["name"],
            config["cookie"]["key"],
            config["cookie"]["expiry_days"],
        )
        st.session_state["authenticator"] = authenticator
        st.session_state["config"] = config

    def logout_callback(_):
        st.session_state["authentication_status"] = None
        st.session_state["login_user"] = None
        st.session_state["roles"] = []
        st.cache_data.clear()
        authenticator.cookie_controller.delete_cookie()
        st.rerun()

    try:
        authenticator.login(
            location="sidebar",
            fields={
                "Form name": "사용자 로그인",
                "Username": "이름",
                "Password": "비밀번호",
                "Login": "로그인 🚀",
            },
        )
    except Exception as e:
        st.sidebar.error(e)
        # logout_callback(None)
        return

    if st.session_state["authentication_status"] is False:
        st.sidebar.error("로그인 실패!")
        return
    elif st.session_state["authentication_status"] is None:
        return

    username = st.session_state["username"]  # username value filled by login widget

    user_list = supabase.get_table_dataframe("participants")
    # config.yaml에 등록된 username과 DB에 등록된 name 컬럼이 일치하는 사용자 정보 조회
    if user_list is not None and not user_list.empty:
        login_user = user_list[user_list["name"] == username]
        if username != "admin":
            if login_user.empty:
                st.sidebar.error("사용자 정보를 확인할 수 없습니다.")
            else:
                st.session_state["login_user"] = login_user.iloc[0]

    st.sidebar.write(f"### **{username}**")

    authenticator.logout(location="sidebar", callback=logout_callback)

    st.sidebar.divider()

    if user_list is not None and not user_list.empty and username in user_list["name"].values:
        with st.sidebar.status("내 색깔 확인"):
            login_user = st.session_state["login_user"]

            # 참가자 정보
            with st.container(border=True):
                col1, col2 = st.columns([1, 2])

                # 이름
                with col1:
                    st.write("이름")
                with col2:
                    st.write(f"**{st.session_state['username']}**")

                # 참여상태
                with col1:
                    st.write("참여상태")
                with col2:
                    status = GamePlayerStatus(login_user["status"])
                    st.write(f":{status.get_status_color(status.value)}[{status.value}]")

                # QR 코드 상태
                with col1:
                    st.write("QR 상태")
                with col2:
                    st.write(
                        f":{QRCodeStatus.get_status_color(login_user['qr_status'])}[{login_user['qr_status']}]"
                    )

            with st.container(border=True):
                col1, col2 = st.columns([1, 2])

                # 색깔
                with col1:
                    st.write("색깔")
                with col2:
                    color = Colors(login_user["color"])
                    st.write(f"{color.color_text(color.value)}", unsafe_allow_html=True)

                # 그룹 머리
                with col1:
                    st.write("그룹 머리")
                with col2:
                    group = (
                        Colors(login_user["group_head"])
                        if login_user["group_head"] is not None
                        else None
                    )
                    st.write(
                        f"{"" if group is None else group.color_text(group.value)}",
                        unsafe_allow_html=True,
                    )

                # 그룹 꼬리
                with col1:
                    st.write("그룹 꼬리")
                with col2:
                    group = (
                        Colors(login_user["group_tail"])
                        if login_user["group_tail"] is not None
                        else None
                    )
                    st.write(
                        f"{"" if group is None else group.color_text(group.value)}",
                        unsafe_allow_html=True,
                    )

            with st.container(border=True):
                col1, col2 = st.columns([1, 2])

                # 패널티 시간
                with col1:
                    st.write("패널티 종료")
                with col2:
                    penalty_time = login_user["penalty_time"]  # str
                    if penalty_time is not None:
                        penalty_time = penalty_time.split(".")[0]
                        penalty_time = datetime.strptime(penalty_time, "%Y-%m-%dT%H:%M:%S")
                        penalty_time = penalty_time.strftime("%Y-%m-%d %H:%M")
                        st.write(f"{penalty_time}")
                    else:
                        st.write(":gray[현재 패널티가 없습니다.]")


# Streamlit 메인 페이지
if __name__ == "__main__":
    st.set_page_config(page_title="색깔꼬리잡기", page_icon=":material/color_lens:")
    st.markdown(
        """
        <style>
        @import url("https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css");
        body {
            font-family: Pretendard, sans-serif;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # region 글로벌 변수 설정

    supabase = Supabase()
    st.session_state["supabase"] = supabase

    game_config = GameConfiguration()
    game_config.Penalty_Duration = 10  # 실패 패널티 시간 (분)
    # game_config.Inactive_Duration = 60  # 비활성 패널티 시간 (분)
    game_config.Game_Start_Time = None
    game_config.Game_End_Time = None
    game_config.Game_Status = "초기화"  # 초기화 | 시작 | 종료
    st.session_state["game_config"] = game_config

    theme = st_theme()
    st.session_state["active_theme"] = theme
    # st.write(theme)

    # endregion

    # region 페이지 설정

    pages_dict = {
        "Home $weet Home": [
            st.Page(page="view/notice.py", title="공지사항", icon="📣", default=True),
            st.Page(page="view/my_info.py", title="내 QR 코드", icon="💙"),
        ],
        "PO￦ER": [
            st.Page(page="view/help.py", title="도움말", icon="🤔"),
        ],
    }
    if "admin" in (st.session_state.get("roles") or []):
        pages_dict["PO￦ER"].append(st.Page(page="view/admin.py", title="관리자", icon="👑"))

    pages = st.navigation(pages_dict)

    # endregion

    sidebar()

    # region 쿼리 파라미터 처리

    if st.query_params.get("capture"):
        # 로그인 여부 확인
        if not st.session_state.get("authentication_status"):
            st.toast("❗ :red[잡기 위해서는 로그인이 필요합니다.]")
        else:
            target_name = st.query_params.get("capture")  # username
            no_penalty = st.query_params.get("no_penalty")  # boolean (true or false)
            if target_name is not None:
                target_name = urllib.parse.unquote(target_name)
                target_name = target_name.replace("_", " ")

                no_penalty = no_penalty == "true"

                result = Action.attempt_capture(target_name, no_penalty)
                st.query_params.clear()

                if result == "success":
                    st.success("잡기 성공!")
                elif result == "fail":
                    st.error("잡기 실패!")
                else:
                    st.warning(result)

    # endregion

    # region 페이지 렌더링

    pages.run()

    # endregion
