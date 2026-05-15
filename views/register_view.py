import logging

import flet as ft

from database import create_user, init_db


def register_view(page: ft.Page):
    page.title = "Kargo Takip - Kayit Ol"
    page.padding = 50
    page.clean()
    init_db()

    logger = logging.getLogger("app")

    username_field = ft.TextField(
        label="Kullanici Adi",
        autofocus=True,
        text_align=ft.TextAlign.CENTER,
    )
    password_field = ft.TextField(
        label="Sifre",
        password=True,
        text_align=ft.TextAlign.CENTER,
    )
    confirm_password_field = ft.TextField(
        label="Sifre Tekrar",
        password=True,
        text_align=ft.TextAlign.CENTER,
    )

    error_text = ft.Text(visible=False, color="red", size=14)
    success_text = ft.Text(visible=False, color="green", size=14)

    def handle_register(e):
        username = (username_field.value or "").strip()
        password = password_field.value or ""
        confirm_password = confirm_password_field.value or ""

        if not username or not password or not confirm_password:
            error_text.value = "Lutfen tum alanlari doldurun."
            error_text.visible = True
            success_text.visible = False
            page.update()
            return

        if password != confirm_password:
            error_text.value = "Sifreler eslesmiyor!"
            error_text.visible = True
            success_text.visible = False
            page.update()
            return

        if len(password) < 4:
            error_text.value = "Sifre en az 4 karakter olmali."
            error_text.visible = True
            success_text.visible = False
            page.update()
            return

        try:
            result = create_user(username, password, username)
        except Exception:
            logger.exception("Register failed: user=%s", username)
            error_text.value = "Kayit sirasinda beklenmeyen bir hata olustu."
            error_text.visible = True
            success_text.visible = False
            page.update()
            return

        if result:
            logger.info("Register success: user=%s", username)
            success_text.value = "Kayit basarili! Giris yapabilirsiniz."
            success_text.visible = True
            error_text.visible = False
            username_field.value = ""
            password_field.value = ""
            confirm_password_field.value = ""
            page.update()
            return

        logger.warning("Register failed (exists): user=%s", username)
        error_text.value = "Bu kullanici adi zaten var!"
        error_text.visible = True
        success_text.visible = False
        page.update()

    register_button = ft.ElevatedButton(
        content=ft.Text("Kayit Ol"),
        width=200,
        on_click=handle_register,
    )
    login_link = ft.TextButton(
        content=ft.Text("Zaten hesabin var mi? Giris yap"),
        on_click=lambda e: page.go("/login"),
    )

    page.add(
        ft.Column(
            [
                ft.Text("Kargo Takip", size=32, weight=ft.FontWeight.BOLD),
                ft.Text("Kayit Ol", size=18),
                ft.Container(height=30),
                username_field,
                password_field,
                confirm_password_field,
                ft.Container(height=10),
                error_text,
                success_text,
                ft.Container(height=20),
                register_button,
                login_link,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
        )
    )
