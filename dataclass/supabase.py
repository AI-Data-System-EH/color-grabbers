import pandas as pd
import streamlit as st
from supabase import create_client


class Supabase:
    # cSpell: disable
    SUPABASE_URL = "https://usnlntxabtzotkkordxe.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVzbmxudHhhYnR6b3Rra29yZHhlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzQ4NTczMjIsImV4cCI6MjA1MDQzMzMyMn0.S-ivd-hwZNV-T6q3VqTZ9pJ31ensCQ5fKDmXw_a1Ncw"
    SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVzbmxudHhhYnR6b3Rra29yZHhlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNDg1NzMyMiwiZXhwIjoyMDUwNDMzMzIyfQ.e8ukUh4kANdOiYui2lnevUCSJhtcmvaZWo4gHoRX91c"
    # cSpell: enable

    def __init__(self):
        self._supabase = create_client(self.SUPABASE_URL, self.SUPABASE_KEY)
        self._supabase_service_role = create_client(
            self.SUPABASE_URL, self.SUPABASE_SERVICE_ROLE_KEY
        )

    def get_table_dataframe(self, table_name: str):
        try:
            table = self._supabase.table(table_name)
        except Exception as e:
            st.error(f"테이블 조회 실패: {e}")
            return None

        return pd.DataFrame(table.select("*").execute().data)

    def upsert_table_from_dataframe(self, table_name: str, dataframe: pd.DataFrame):
        try:
            table = self._supabase_service_role.table(table_name)
        except Exception as e:
            st.error(f"테이블 업데이트 실패: {e}")
            return None

        for _, row in dataframe.iterrows():
            table.upsert(row.to_dict()).execute()

    def delete_table_dataframe(self, table_name: str):
        try:
            self._supabase_service_role.table(table_name).delete().neq("id", 0).execute()
        except Exception as e:
            st.error(f"테이블 삭제 실패: {e}")
