from datetime import datetime

import pandas as pd


class Participant:
    id: int
    name: str
    color: str | None
    group_head: str | None
    group_tail: str | None
    status: str | None
    qr_status: str | None
    penalty_time: datetime | None  # timestamptz

    def __init__(
        self,
        id: int,
        name: str,
        color: str | None,
        group_head: str | None,
        group_tail: str | None,
        status: str | None,
        qr_status: str | None,
        penalty_time: datetime | None,
    ):
        self.id = id
        self.name = name
        self.color = color
        self.group_head = group_head
        self.group_tail = group_tail
        self.status = status
        self.qr_status = qr_status
        self.penalty_time = penalty_time

    @staticmethod
    def from_dataframe(df: pd.DataFrame):
        return [
            Participant(
                id=row["id"],
                name=row["name"],
                color=row["color"],
                group_head=row["group_head"],
                group_tail=row["group_tail"],
                status=row["status"],
                qr_status=row["qr_status"],
                penalty_time=row["penalty_time"],
            )
            for row in df.to_dict(orient="records")
        ]

    def to_dataframe(self):
        return pd.DataFrame([self.__dict__])

    @staticmethod
    def create_empty_dataframe():
        # 참가자 테이블 생성 (컬럼 이름, 데이터 타입)
        return pd.DataFrame(
            {
                "id": pd.Series(dtype="int64"),
                "name": pd.Series(dtype="str"),
                "color": pd.Series(dtype="str"),
                "group_head": pd.Series(dtype="str"),
                "group_tail": pd.Series(dtype="str"),
                "status": pd.Series(dtype="str"),
                "qr_status": pd.Series(dtype="str"),
                "penalty_time": pd.Series(dtype="str"),
            }
        )
