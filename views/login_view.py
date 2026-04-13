import flet as ft
from database import verify_user, create_user, init_db


def login_view(page: ft.Page):
    page.title = "Kargo Takip - Giris"
    page.padding = 50
    page.clean()
    
    init_db()
    create_user("admin", "123456", "Yonetici")
    
    PRIMARY_COLOR = "#2196F3"
    
    def handle_login(e):
        username = username_field.value
        password = password_field.value
        
        if not username or not password:
            error_text.value = "Lutfen kullanici adi ve sifre girin."
            error_text.visible = True
            page.update()
            return
        
        user = verify_user(username, password)
        
        if user:
            page.current_user = user
            page.go("/home")
        else:
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
        on_submit=lambda _: handle_login(None)
    )
    
    error_text = ft.Text(
        visible=False,
        color="red",
        size=14,
    )
    
    login_button = ft.ElevatedButton(
        content=ft.Text("Giris Yap", size=16),
        width=200,
        height=45,
        bgcolor=PRIMARY_COLOR,
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
                ft.Text(
                    "Personel Girisi",
                    size=16,
                    color="#666666",
                ),
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
