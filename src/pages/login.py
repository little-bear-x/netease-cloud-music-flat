"""登录页面"""

import flet as ft
import models
import qrcode
import io
import base64


class LoginPage(ft.View):
    """登录页面"""

    def __init__(self, globals_var: models.Globals):
        super().__init__()

        self.page = globals_var.page
        self.api = globals_var.music_api
        self.globals = globals_var
        self.route = "/login"
        self.adaptive = True
        self.padding = ft.padding.all(20)

        # AppBar
        self.appbar = ft.AppBar(
            title=ft.Text("登录")
        )

        self.load_view()  # 加载页面内容

    
    def load_view(self):
        """加载页面内容"""
        import qrcode
        import io
        import base64

        self.qr_code = self.api.login_qr_create()  # 获取二维码登录URL

        # 获取二维码
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(self.qr_code[0])
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # 转换为base64
        buffered = io.BytesIO()
        qr_img.save(buffered)
        qr_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        # 二维码图片组件
        self.qr_image = ft.Image(
            src_base64=qr_base64,
            width=200,
            height=200,
            fit=ft.ImageFit.CONTAIN,
        )

        # 检查登录状态按钮
        self.check_login_button = ft.ElevatedButton(
            "检查登录状态",
            on_click=self.check_login_status,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
        )

        # 更新页面内容
        self.controls = [
            ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    "扫描二维码登录",
                                    size=20,
                                    weight=ft.FontWeight.BOLD,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                ft.Container(
                                    content=self.qr_image,
                                    alignment=ft.alignment.center,
                                    margin=ft.margin.only(top=20, bottom=20),
                                ),
                                ft.Container(
                                    content=self.check_login_button,
                                    alignment=ft.alignment.center,
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=ft.padding.all(30),
                        border_radius=10,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        ]

    def check_login_status(self, e):
        """检查登录状态"""
        msg, login_info = self.api.login_qr_check(self.qr_code[1])
        
        if login_info.account:  # 登录成功
            models.info("登录成功")
            # 保存登录信息
            self.globals.save_login_status(login_info) 
            # 返回首页
            self.page.go('/')  # type: ignore
        else:
            models.warning(f"登录状态检查失败: {msg}, {login_info}")