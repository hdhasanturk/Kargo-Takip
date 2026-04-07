import flet as ft
from database import get_all_users


def users_view(page: ft.Page, current_username=""):
    if isinstance(current_username, dict):
        current_username = current_username.get("username", "")

    # Sadece admin gorebilir
    if current_username != "admin":
        page.title = "Erişim Reddedildi"
        page.clean()
        page.add(
            ft.Column(
                [
                    ft.Text("Bu sayfaya erişim yetkiniz yok!", size=20, color="red"),
                    ft.ElevatedButton(
                        content=ft.Text("Geri"),
                        on_click=lambda e: page.go("/home")
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
        return
    
    page.title = "Kullanıcılar"
    page.clean()
    
    def go_back(e):
        page.go("/home")
    
    def load_users(e=None):
        users = get_all_users()
        
        if users:
            user_list.controls = [
                ft.Text("Kayıtlı Kullanıcılar:", size=20, weight=ft.FontWeight.BOLD),
            ]
            
            for u in users:
                user_list.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(f"Kullanıcı Adı: {u['username']}", weight=ft.FontWeight.BOLD),
                            ft.Text(f"ID: {u['id']}", size=12, color="gray"),
                        ]),
                        padding=15,
                        bgcolor="white",
                        border_radius=10,
                        margin=5,
                    )
                )
        else:
            user_list.controls = [
                ft.Text("Henüz kayıtlı kullanıcı yok.", color="gray")
            ]
        
        page.update()
    
    back_button = ft.ElevatedButton(
        content=ft.Text("Geri"),
        on_click=go_back,
    )
    
    user_list = ft.Column([])
    
    load_users()
    
    page.add(
        ft.Column(
            [
                back_button,
                ft.Container(height=20),
                ft.Text("Kullanıcı Yönetimi", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(height=20),
                ft.ElevatedButton(
                    content=ft.Text("Yenile"),
                    on_click=load_users,
                ),
                ft.Container(height=20),
                user_list,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
    )
