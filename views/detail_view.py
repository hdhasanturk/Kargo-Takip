from datetime import datetime

import flet as ft

from database import get_shipment
from kargo_api import get_shipment_status


def detail_view(page: ft.Page, shipment_id: int):
    page.title = "Kargo Detay"
    page.clean()

    shipment = get_shipment(shipment_id)
    if not shipment:
        page.add(
            ft.Column(
                [
                    ft.Text("Kargo bulunamadi!", color="red", size=18),
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

    tracking_no = shipment["tracking_number"]
    real_tracking_no = shipment.get("real_tracking_number") or tracking_no
    courier = shipment.get("courier") or "Sistem Ici Dagitim"

    back_button = ft.ElevatedButton(
        content=ft.Text("<- Geri"),
        on_click=lambda e: page.go("/home"),
    )

    tracking_text = ft.Text(f"Takip No: {tracking_no}", weight=ft.FontWeight.BOLD, size=18)
    real_tracking_text = ft.Text(f"Gercek Takip No: {real_tracking_no}", size=12, color="gray")
    courier_text = ft.Text(f"Kargo Firmasi: {courier}", size=14)
    status_text = ft.Text("Durum: -", color="blue", weight=ft.FontWeight.BOLD)
    last_update_text = ft.Text("Son Guncelleme: -", size=12, color="gray")
    api_source_text = ft.Text("API Kaynak: -", size=11, color="gray")
    api_sync_text = ft.Text("API Senkron: -", size=11, color="gray")
    api_error_text = ft.Text("", size=11, color="red", visible=False)
    movements_column = ft.Column([])
    info_text = ft.Text("", color="red", visible=False)

    def load_cargo_data(e=None):
        nonlocal courier

        cargo_data = get_shipment_status(real_tracking_no, courier)
        if not cargo_data:
            info_text.value = "Kargo bilgisi bulunamadi!"
            info_text.visible = True
            movements_column.controls = []
            page.update()
            return

        if cargo_data.get("courier"):
            courier = cargo_data.get("courier")
            courier_text.value = f"Kargo Firmasi: {courier}"

        status_text.value = f"Durum: {cargo_data['status']}"
        status_text.color = "green" if cargo_data["status"] == "Teslim Edildi" else "blue"
        last_update_text.value = f"Son Guncelleme: {cargo_data['last_update']}"

        api_source_text.value = f"API Kaynak: {cargo_data.get('source') or '-'}"
        api_sync_text.value = f"API Senkron: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        api_error = cargo_data.get("error")
        if api_error:
            api_error_text.value = f"API Hata: {api_error}"
            api_error_text.visible = True
        else:
            api_error_text.visible = False

        movements = cargo_data.get("movements") or []
        movements_column.controls = [
            ft.Text(
                f"* {movement['date']} - {movement['location']}\n  {movement['description']}",
                size=12,
            )
            for movement in movements
        ]
        if not movements_column.controls:
            movements_column.controls = [ft.Text("Hareket kaydi yok.", size=12, color="gray")]

        info_text.visible = False
        page.update()

    refresh_button = ft.ElevatedButton(
        content=ft.Text("Yenile"),
        on_click=load_cargo_data,
    )

    page.add(
        ft.Column(
            [
                ft.Row(
                    [back_button, refresh_button],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),
                ft.Container(height=20),
                ft.Text("Kargo Detay", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(height=20),
                info_text,
                ft.Container(
                    content=ft.Column(
                        [
                            tracking_text,
                            real_tracking_text,
                            courier_text,
                            status_text,
                            last_update_text,
                            api_source_text,
                            api_sync_text,
                            api_error_text,
                            ft.Divider(),
                            ft.Text("Hareket Gecmisi:", weight=ft.FontWeight.BOLD),
                            movements_column,
                        ]
                    ),
                    padding=20,
                    bgcolor="#E0E0E0",
                    border_radius=10,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
        )
    )

    load_cargo_data()
