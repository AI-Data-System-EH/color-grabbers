import subprocess
import threading

# 웹사이트 설정
# PUBLIC_URL = "123.215.183.139"
PUBLIC_URL = "192.168.100.12"
PUBLIC_PORT = 8501
PUBLIC_API_PORT = 8000


def run_api():
    subprocess.run(
        [
            "uvicorn",
            "api:app",
            "--reload",
            "--host",
            PUBLIC_URL,
            "--port",
            str(PUBLIC_API_PORT),
        ]
    )


def run_streamlit():
    subprocess.run(["streamlit", "run", "app.py", "--server.port", str(PUBLIC_PORT)])


if __name__ == "__main__":
    thread_api = threading.Thread(target=run_api)
    thread_app = threading.Thread(target=run_streamlit)
    thread_api.start()
    thread_app.start()
    thread_api.join()
    thread_app.join()
