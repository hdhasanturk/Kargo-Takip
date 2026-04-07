import flet as ft

def main(page: ft.Page):
    page.add(ft.ElevatedButton("Tıkla", on_click=lambda _: print("çalıştı")))

ft.app(main)