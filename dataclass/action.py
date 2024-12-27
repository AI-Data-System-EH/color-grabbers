from datetime import datetime, timedelta

import streamlit as st
from pytz import timezone

from dataclass.colors import Colors
from dataclass.game import GameConfiguration
from dataclass.qrcode import QRCodeStatus
from dataclass.supabase import Supabase


class Action:
    # color : 사용자 색깔
    # group_head : 그룹머리 색깔
    # group_tail : 그룹꼬리 색깔

    # 색깔 비교
    @staticmethod
    def color_compare(attacker, target):
        colors = [color.value for color in Colors.__members__.values()]

        attacker_group_tail = attacker["group_tail"]
        target_color = target["color"]

        attacker_color_index = colors.index(attacker_group_tail)
        target_color_index = colors.index(target_color)

        capturable_color_index = (attacker_color_index + 1) % len(colors)

        # 대상의 색깔이 공격자의 그룹꼬리 색깔 다음 색깔이면 성공
        # 대상의 색깔이 공격자의 그룹꼬리 색깔 다음 색깔이 아니면 실패
        if target_color_index == capturable_color_index:
            return "success"
        else:
            return "fail"

    # URL Query Parameter 처리 (QR 코드 링크 연결 시 잡기 시도)
    @staticmethod
    def attempt_capture(target_name: str, no_penalty: bool) -> str:
        supabase: Supabase | None = st.session_state.get("supabase")
        if supabase is None:
            return "error : Supabase 인스턴스가 없습니다."

        game_config: GameConfiguration | None = st.session_state.get("game_config")
        if game_config is None:
            return "error : 게임 설정이 없습니다."

        # 참가자 테이블 조회
        participants = supabase.get_table_dataframe("participants")
        if participants is None or participants.empty:
            return "error : 참가자 테이블이 비어있습니다."

        # 공격자 정보 조회
        attacker = st.session_state.get("login_user")
        if attacker is None:
            return "error : 본인 정보가 확인되지 않습니다."

        if no_penalty and attacker["qr_status"] == QRCodeStatus.HIDDEN.value:
            return "사용할 수 없는 QR 코드에 접근하셨습니다."

        # 공격자 패널티 타이머 확인
        penalty_time = attacker["penalty_time"]
        if penalty_time is not None:
            penalty_time = datetime.fromisoformat(penalty_time).replace(tzinfo=None)
            penalty_time = timezone("Asia/Seoul").localize(penalty_time)
            now = datetime.now(tz=timezone("Asia/Seoul"))

            if penalty_time > now:
                penalty_time_str = penalty_time.strftime("%H:%M")
                if penalty_time.date() > now.date():
                    penalty_time_str = f"내일 {penalty_time_str}"
                else:
                    penalty_time_str = f"오늘 {penalty_time_str}"
                return f"패널티 타이머가 **{penalty_time_str}** 까지 활성화되어 있습니다."

        # 대상 정보 조회
        target = participants[participants["name"] == target_name]
        target = target.to_dict(orient="records")
        target = target[0] if len(target) > 0 else None
        if not target:
            return "error : 대상 정보를 확인할 수 없습니다."

        if attacker["name"] == target["name"]:
            return "본인을 잡을 수 없습니다."

        result = Action.color_compare(attacker, target)
        if result == "success":
            supabase._supabase_service_role.table("logs").insert(
                {
                    "message": "누군가가 잡기에 성공했습니다.",
                    "result": "**:green[성공]** ✅ ",
                }
            ).execute()

            # 대상 그룹 전체의 그룹머리를 공격자의 그룹머리로 변경
            supabase._supabase_service_role.table("participants").update(
                {"group_head": attacker["group_head"]}
            ).eq("group_head", target["group_head"]).execute()

            # 공격자 그룹 전체의 그룹꼬리를 대상의 그룹꼬리로 변경
            supabase._supabase_service_role.table("participants").update(
                {"group_tail": target["group_tail"]}
            ).eq("group_tail", attacker["group_tail"]).execute()

            return "success"
        elif result == "fail":
            supabase._supabase_service_role.table("logs").insert(
                {
                    "message": f"**{attacker['name']}** 님이 **{target['name']}** 님을 잡지 못했습니다.",
                    "result": "**:red[실패]** ❌ ",
                }
            ).execute()

            if no_penalty:# or penalty_time is None:
                st.toast("이번은 패널티가 없어요. 다음번에는 패널티가 적용될 거예요.")
                # 시도한 사람의 무료시도 QR 링크 가리기
                supabase._supabase_service_role.table("participants").update(
                    {"qr_status": QRCodeStatus.HIDDEN.value}
                ).eq("color", attacker["color"]).execute()

            else:
                # 공격자 그룹 전체의 패널티 타이머 활성화
                penalty_time_new = datetime.now() + timedelta(minutes=game_config.Penalty_Duration)
                # DB 입력 시 Timezone 설정하지 않아도 supabase에서 자동으로 tz 설정됨
                # supabase 컬럼 설정 : (now() AT TIME ZONE 'Asia/Seoul'::text)
                supabase._supabase_service_role.table("participants").update(
                    {"penalty_time": penalty_time_new.isoformat()}
                ).eq("group_head", attacker["group_head"]).execute()

                # 본인 제외 모든 사람에게 무료시도 QR 코드 노출
                supabase._supabase_service_role.table("participants").update(
                    {"qr_status": QRCodeStatus.REVEALED.value}
                ).neq("color", attacker["color"]).execute()

                st.toast(
                    f"패널티 타이머가 **{penalty_time_new.strftime('%H:%M')}** 까지 활성화되었습니다."
                )

            return "fail"
        else:
            return "error"
