from enum import Enum

import numpy as np
import streamlit as st
from dataclass.participant import Participant


class Colors(Enum):
    RED = "빨강"
    ORANGE = "주황"
    YELLOW = "노랑"
    GREEN = "초록"
    BLUE = "파랑"
    NAVY = "남색"
    PURPLE = "보라"

    @staticmethod
    def get_color_name(color: str):
        return Colors.__members__.get(color)

    def color_text(self, text: str):
        # check dark mode
        if st.session_state["active_theme"].get("base") == "dark":
            color = self.name.lower()
            if color == "navy":
                color = "#4E76A1"
            return f"<span style='color: {color}'>{text}</span>"
        else:
            color = self.name.lower()
            if color == "yellow":
                color = "#FFD700"
            elif color == "navy":
                color = "#4E76A1"
            return f"<span style='color: {color}'>{text}</span>"

    @staticmethod
    def check_color(color: str):
        return color in Colors.__members__

    @staticmethod
    def assign_random_color(assign_targets: list[Participant]):
        color_list = [color.value for color in Colors.__members__.values()]
        for target in assign_targets:
            target.color = np.random.choice(color_list)
        return assign_targets

    @staticmethod
    def assign_uniform_color(assign_targets: list[Participant]):
        # 참가자 수와 색깔 수를 계산하여 색깔 배정
        total_length = len(assign_targets)
        repeat_num = total_length // len(Colors) + (total_length % len(Colors) > 0)
        color_list = [color.value for color in Colors.__members__.values()]
        colors = np.repeat(color_list, repeat_num)

        selected_colors = np.random.choice(colors, total_length, replace=False)
        for i, target in enumerate(assign_targets):
            target.color = selected_colors[i]
            target.group_head = selected_colors[i]
            target.group_tail = selected_colors[i]

        return assign_targets
