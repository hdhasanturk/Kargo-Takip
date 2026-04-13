import flet as ft
from database import create_user, init_db


def register_view(page: ft.Page):
    page.title = "Kargo Takip - Kayıt Ol"
    page.padding = 50
    page.clean()
    init_db()
    
    username_field = ft.TextField(
        label="Kullanıcı Adı",
        autofocus=True,
        text_align=ft.TextAlign.CENTER,
    )
    
    password_field = ft.TextField(
        label="Şifre",
        password=True,
        text_align=ft.TextAlign.CENTER,
    )
    
    confirm_password_field = ft.TextField(
        label="Şifre Tekrar",
        password=True,
        text_align=ft.TextAlign.CENTER,
    )
    
    error_text = ft.Text(
        visible=False,
        color="red",
        size=14,
    )
    
    success_text = ft.Text(
        visible=False,
        color="green",
        size=14,
    )
    
    def handle_register(e):
        username = (username_field.value or "").strip()
        password = password_field.value or ""
        confirm_password = confirm_password_field.value or ""
        
        # Alanları kontrol et
        if not username or not password or not confirm_password:
            error_text.value = "Lütfen tüm alanları doldurun."
            error_text.visible = True
            success_text.visible = False
            page.update()
            return
        
        # Şifre eşleşme kontrolü
        if password != confirm_password:
            error_text.value = "Şifreler eşleşmiyor!"
            error_text.visible = True
            success_text.visible = False
            page.update()
            return
        
        # Şifre uzunluk kontrolü
        if len(password) < 4:
            error_text.value = "Şifre en az 4 karakter olmalı."
            error_text.visible = True
            success_text.visible = False
            page.update()
            return
        
        # Veritabaninda kullanici olustur
        try:
            result = create_user(username, password, username)
        except Exception:
            error_text.value = "Kayit sirasinda beklenmeyen bir hata olustu."
            error_text.visible = True
            success_text.visible = False
            page.update()
            return
        
        if result:
            success_text.value = "Kayıt başarılı! Giriş yapabilirsiniz."
            success_text.visible = True
            error_text.visible = False
            # Alanları temizle
            username_field.value = ""
            password_field.value = ""
            confirm_password_field.value = ""
            page.update()
        else:
            error_text.value = "Bu kullanıcı adı zaten var!"
            error_text.visible = True
            success_text.visible = False
            page.update()
    
    def go_to_login(e):
        page.go("/login")
    
    register_button = ft.ElevatedButton(
        content=ft.Text("Kayıt Ol"),
        width=200,
        on_click=handle_register,
    )
    
    login_link = ft.TextButton(
        content=ft.Text("Zaten hesabın var mı? Giriş yap"),
        on_click=go_to_login,
    )
    
    page.add(
        ft.Column(
            [
                ft.Text(
                    "Kargo Takip",
                    size=32,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    "Kayıt Ol",
                    size=18,
                ),
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
