from datetime import datetime
from enum import Enum

from pytz import timezone


class GameConfiguration:
    Penalty_Duration: int  # 패널티 활성화 시간 (분)
    Inactive_Duration: int  # 활동 없음 제한 시간 (분)

    Game_Start_Time: datetime | None  # 게임 시작 시간
    Game_End_Time: datetime | None  # 게임 종료 시간
    Game_Status: str  # 게임 상태

    TimeZone = timezone("Asia/Seoul")

    def start_time_str(self):
        if self.Game_Start_Time is None:
            return "미정"
        else:
            time_str = self.Game_Start_Time.strftime("%H:%M")
            if self.Game_Start_Time.date() == datetime.now(tz=self.TimeZone).date():
                time_str = f"오늘 {time_str}"
            else:
                time_str = f"내일 {time_str}"
            return f"{time_str}"

    def end_time_str(self):
        if self.Game_End_Time is None:
            return "미정"
        else:
            time_str = self.Game_End_Time.strftime("%H:%M")
            if self.Game_End_Time.date() == datetime.now(tz=self.TimeZone).date():
                time_str = f"오늘 {time_str}"
            else:
                time_str = f"내일 {time_str}"
            return f"{time_str}"

    def remaining_time(self, dtype: str = "number"):
        # dtype: "number" or "str"
        if dtype not in ["number", "str"]:
            raise ValueError("dtype must be 'number' or 'str'")

        if self.Game_End_Time is None:
            return None if dtype == "number" else "미정"
        else:
            delta = self.Game_End_Time - datetime.now(tz=self.TimeZone)
            if dtype == "number":
                return delta
            elif dtype == "str":
                return (
                    f"{delta.days * 24 + delta.seconds // 60:02d}:{delta.seconds % 60:02d}"  # HH:MM
                )


class GamePlayerStatus(Enum):
    ACTIVE = "생존"
    INACTIVE = "미참여"
    CAPTURED = "잡힘"
    PENALTY = "패널티"

    @staticmethod
    def get_status_color(status: str):
        if status == GamePlayerStatus.ACTIVE.value:
            return "green"
        elif status == GamePlayerStatus.INACTIVE.value:
            return "gray"
        elif status == GamePlayerStatus.CAPTURED.value:
            return "red"
        elif status == GamePlayerStatus.PENALTY.value:
            return "orange"
