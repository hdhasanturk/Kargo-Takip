import logging

import flet as ft

from database import get_all_users


def users_view(page: ft.Page, current_username=""):
    if isinstance(current_username, dict):
        current_username = current_username.get("username", "")

    logger = logging.getLogger("app")

    if current_username != "admin":
        page.title = "Erisim Reddedildi"
        page.clean()
        page.add(
            ft.Column(
                [
                    ft.Text("Bu sayfaya erisim yetkiniz yok!", size=20, color="red"),
                    ft.ElevatedButton(
                        content=ft.Text("Geri"),
                        on_click=lambda e: page.go("/home"),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
        return

    page.title = "Kullanicilar"
    page.clean()

    user_list = ft.Column([])

    def load_users(e=None):
        users = get_all_users()

        logger.info("Users refresh: count=%s user=%s", len(users), current_username or "-")

        if not users:
            user_list.controls = [
                ft.Text("Henuz kayitli kullanici yok.", color="gray"),
            ]
            page.update()
            return

        user_list.controls = [
            ft.Text("Kayitli Kullanicilar:", size=20, weight=ft.FontWeight.BOLD),
        ]

        for user in users:
            user_list.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                f"Kullanici Adi: {user['username']}",
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(f"Ad Soyad: {user.get('name', '-')}", size=12, color="gray"),
                            ft.Text(f"Rol: {user.get('role', '-')}", size=12, color="gray"),
                            ft.Text(f"ID: {user['id']}", size=12, color="gray"),
                        ]
                    ),
                    padding=15,
                    bgcolor="white",
                    border_radius=10,
                    margin=5,
                )
            )

        page.update()

    back_button = ft.ElevatedButton(
        content=ft.Text("Geri"),
        on_click=lambda e: page.go("/home"),
    )

    load_users()

    page.add(
        ft.Column(
            [
                back_button,
                ft.Container(height=20),
                ft.Text("Kullanici Yonetimi", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(height=20),
                ft.ElevatedButton(content=ft.Text("Yenile"), on_click=load_users),
                ft.Container(height=20),
                user_list,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
    )
