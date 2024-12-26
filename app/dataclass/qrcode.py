import urllib.parse
from enum import Enum

import qrcode
from PIL import Image
from pyshorteners import Shortener
from static.dns import PUBLIC_PORT, PUBLIC_URL


class QRCode:
    # QR 코드 생성 함수
    @staticmethod
    def generate_qrcode(data):
        qr = qrcode.QRCode(  # type: ignore
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,  # type: ignore
            box_size=10,
            border=2,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill="black", back_color="white")
        pil_image = img.get_image()
        return pil_image

    @staticmethod
    def qrcode_with_capture_param(name: str, no_penalty: bool = False) -> tuple[Image.Image, str]:
        quote_name = name.replace(" ", "_")
        quote_name = urllib.parse.quote(quote_name)
        qr_code_data = f"http://{PUBLIC_URL}:{PUBLIC_PORT}/?capture={quote_name}&no_penalty={str(no_penalty).lower()}"
        qr_code_data = Shortener().tinyurl.short(qr_code_data)
        qr_image = QRCode.generate_qrcode(qr_code_data)

        return qr_image, qr_code_data


class QRCodeStatus(Enum):
    HIDDEN = "숨겨짐"
    REVEALED = "노출됨"

    @staticmethod
    def get_status_color(status: str):
        if status == QRCodeStatus.HIDDEN.value:
            return "gray"
        elif status == QRCodeStatus.REVEALED.value:
            return "red"
