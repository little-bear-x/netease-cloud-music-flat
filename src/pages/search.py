import flet as ft


class SearchPage(ft.View):
    def __init__(self):
        super().__init__()

        self.route = "/search"
        self.adaptive = True
        self.padding = ft.padding.all(20)

        self.appbar = ft.AppBar(
            title=ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        on_click=lambda e: self.page.go("/"), # type: ignore
                    ),
                    ft.TextField(hint_text="搜索", expand=True, autofocus=True, border_width=0),
                ],
                alignment=ft.MainAxisAlignment.START,
            )
        )
