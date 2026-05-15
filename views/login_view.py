import logging

import flet as ft

from database import ensure_default_admin, init_db, verify_user


def login_view(page: ft.Page, set_user=None, clear_user=None):
    page.title = "Kargo Takip - Giris"
    page.padding = 50
    page.clean()

    logger = logging.getLogger("app")

    init_db()
    ensure_default_admin()

    primary_color = "#2196F3"

    def handle_login(e):
        username = (username_field.value or "").strip()
        password = password_field.value or ""

        if not username or not password:
            error_text.value = "Lutfen kullanici adi ve sifre girin."
            error_text.visible = True
            page.update()
            return

        user = verify_user(username, password)
        if user:
            logger.info("Login success: user=%s", user.get("username") or "-")
            if set_user:
                set_user(page, user)
            page.go("/home")
            return

        if username:
            logger.warning("Login failed: user=%s", username)
        error_text.value = "Kullanici adi veya sifre hatali."
        error_text.visible = True
        username_field.value = ""
        password_field.value = ""
        page.update()

    username_field = ft.TextField(
        label="Kullanici Adi",
        autofocus=True,
        text_align=ft.TextAlign.CENTER,
    )
    password_field = ft.TextField(
        label="Sifre",
        password=True,
        text_align=ft.TextAlign.CENTER,
        on_submit=lambda _: handle_login(None),
    )
    error_text = ft.Text(visible=False, color="red", size=14)

    login_button = ft.ElevatedButton(
        content=ft.Text("Giris Yap", size=16),
        width=200,
        height=45,
        bgcolor=primary_color,
        color="white",
        on_click=handle_login,
    )
    register_button = ft.TextButton(
        content=ft.Text("Kayit Ol"),
        on_click=lambda e: page.go("/register"),
    )
    tracking_button = ft.TextButton(
        content=ft.Text("Kargo Takip Sorgula"),
        on_click=lambda e: page.go("/track"),
    )

    page.add(
        ft.Column(
            [
                ft.Text(
                    "Kargo Takip",
                    size=32,
                    weight=ft.FontWeight.BOLD,
                    color="#333333",
                ),
                ft.Text("Personel Girisi", size=16, color="#666666"),
                ft.Container(height=30),
                username_field,
                password_field,
                error_text,
                ft.Container(height=20),
                login_button,
                register_button,
                tracking_button,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
    )
