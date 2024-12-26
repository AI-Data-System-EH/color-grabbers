# 도움말 페이지

import streamlit as st

from dataclass.colors import Colors
from dataclass.game import GameConfiguration


def help():
    game_config: GameConfiguration = st.session_state.get("game_config", None)

    st.title("게임 규칙")

    assistant = st.chat_message(
        name="assistant",
        avatar="resources/chloe.webp",
    )
    with assistant:
        st.write("***본인의 색깔을 잘 숨기고, 혼자 또는 큰 그룹으로 끝까지 살아남으세요.***")
        st.write(
            "***같은 색 팀원과 협력하거나, 팀원을 궁지로 몰아넣어 혼자 모든 것을 독차지 할 수도 있습니다.***"
        )
    st.divider()

    with st.expander("QR 코드 규칙"):
        st.write("❌ QR 코드를 보기 위해 물리적으로 뺏으려 하지 말아주세요.")
        st.write("✅ 상대방이 QR 코드를 보여달라고 하면 보여주면 돼요.")
        with st.chat_message(name="assistant", avatar="resources/chloe.webp"):
            st.write(
                f":gray[잡기에 실패하면 **{game_config.Penalty_Duration}분** 동안 아무도 잡을 수 없어요.]"
            )
        st.write("ℹ️ 내 정보 페이지에서 QR 코드를 촬영할 수 있어요.")

    with st.expander("우승 조건"):
        st.write("✅ **마지막 한 팀**이 남은 경우")
        st.write("✅ 제한시간까지 생존한 색깔 중 **가장 큰 그룹**을 가진 색깔이 우승")
        st.write("ℹ️ 남은 색깔의 그룹 크기가 동일하면 남은 색깔팀 수만큼 전체 상금 분배")
        # with st.chat_message(name="assistant", avatar="resources/chloe.webp"):
        #     st.write(f":gray[제한시간은 **{game_config.end_time_str()}**까지입니다.]")
        #     st.write(f":gray[현재 남은시간은 **{game_config.remaining_time(dtype='str')}**입니다.]")

    with st.expander("상금 분배"):
        st.write("✅ 팀원 전원 생존 시: 상금을 균등 분배")
        st.write("✅ 팀원 일부 생존 시: 남은 생존자에게 상금 분배")
        st.write("ℹ️ 세부 상금은 협의하여 자유롭게 분배 가능")
        with st.chat_message(name="assistant", avatar="resources/chloe.webp"):
            st.write(
                ":gray[팀원 중 참여하지 않는 사람이 있을 경우, 관리자 확인 후 미참여자는 상금에서 제외합니다.]"
            )

    with st.expander("색깔 규칙"):
        st.write("❌ 내 색깔은 모두에게 비공개에요. 심지어 팀원도 모르죠.")
        st.write("✅ 본인 바로 다음 색깔만 잡을 수 있어요.")
        with st.chat_message(name="assistant", avatar="resources/chloe.webp"):
            st.write(
                ":gray["
                + f"{Colors.RED.color_text('빨강')}→"
                + f"{Colors.ORANGE.color_text('주황')}→"
                + f"{Colors.YELLOW.color_text('노랑')}→"
                + f"{Colors.GREEN.color_text('초록')}→"
                + f"{Colors.BLUE.color_text('파랑')}→"
                + f"{Colors.NAVY.color_text('남색')}→"
                + f"{Colors.PURPLE.color_text('보라')}→"
                + f"{Colors.RED.color_text('빨강')}"
                + "]",
                unsafe_allow_html=True,
            )
        st.write("ℹ️ 색깔 정보 공유는 대화를 통해 자유롭게 가능해요.")

    with st.expander("잡기 규칙"):
        st.write("✅ 잡기가 성공하면, 공지에 누군가 잡혔다는 것만 알려줘요.")
        st.write("❌ 잡기 실패 시 기록이 남고, 시도한 사람의 QR 코드 링크를 공지에 노출해요.")
        with st.chat_message(name="assistant", avatar="resources/chloe.webp"):
            st.write(
                f":gray[실패하면 **:red[{game_config.Penalty_Duration}분]** 동안 잡기 권한이 사라져요.]"
            )
            st.write(":gray[맨 처음 한 번은 패널티를 없앴어요. 사람 일은 모르는 거니까요!]")
        with st.chat_message(name="assistant", avatar="resources/chloe.webp"):
            st.write(":gray[기록은 이렇게 보여요. 색깔은 표시하지 않아요.]")
            st.write("[2024-12-25 19:41] 실패 ❌ **김철수** 님이 **박영희** 님을 잡지 못했습니다.")
        with st.chat_message(name="assistant", avatar="resources/chloe.webp"):
            st.write(
                f":gray[패널티로 QR 코드가 노출되는 시간은 **:red[{game_config.Penalty_Duration}분]** 이에요.]"
            )
            st.write(
                ":gray[노출된 링크는 누구나 한 번, **패널티 없이** 버튼을 눌러 잡을 수 있어요.]"
            )
            st.write(":gray[이미 패널티가 적용 중이면, 노출된 링크라도 잡을 수 없어요.]")
        # st.write("⚠️ 활동이 없는 사람 중 랜덤으로 한 명의 QR 코드 링크가 노출돼요.")
        # with st.chat_message(name="assistant", avatar="resources/chloe.webp"):
        #     st.write(f":gray[활동 없음 제한 시간은 **{game_config.Inactive_Duration}분**이에요.]")

    with st.expander("그룹 규칙"):
        st.write("✅ 팀원 전체가 다음 색깔을 잡을 수 있어요.")
        with st.chat_message(name="assistant", avatar="resources/chloe.webp"):
            st.write(
                ":gray["
                + f"\"{Colors.RED.color_text('빨강')}, {Colors.ORANGE.color_text('주황')}\" → "
                + f"{Colors.YELLOW.color_text('노랑')}"
                + "]",
                unsafe_allow_html=True,
            )
        st.write("❌ 한 명이 잡기를 실패하면, 그룹 전체가 잡기 권한을 잃어요.")
        st.write("ℹ️ 내 정보는 사이드바에서 확인 가능해요.")


help()
