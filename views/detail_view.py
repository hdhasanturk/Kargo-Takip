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
                    ft.Text("Kargo bulunamadı!", color="red", size=18),
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
    
    tracking_no = shipment["tracking_number"]
    courier = shipment["courier"]
    
    cargo_data = get_shipment_status(tracking_no, courier)
    
    def go_back(e):
        page.go("/home")
    
    back_button = ft.ElevatedButton(
        content=ft.Text("← Geri"),
        on_click=go_back,
    )
    
    if cargo_data:
        movements_text = ""
        for m in cargo_data["movements"]:
            movements_text += f"📍 {m['date']} - {m['location']}\n   {m['description']}\n\n"
        
        status_color = "green" if cargo_data["status"] == "Teslim Edildi" else "blue"
        
        page.add(
            ft.Column(
                [
                    back_button,
                    ft.Container(height=20),
                    ft.Text("Kargo Detay", size=24, weight=ft.FontWeight.BOLD),
                    ft.Container(height=20),
                    ft.Container(
                        content=ft.Column([
                            ft.Text(f"Takip No: {tracking_no}", weight=ft.FontWeight.BOLD, size=18),
                            ft.Text(f"Kargo Firması: {courier}", size=14),
                            ft.Text(f"Durum: {cargo_data['status']}", color=status_color, weight=ft.FontWeight.BOLD),
                            ft.Text(f"Son Güncelleme: {cargo_data['last_update']}", size=12, color="gray"),
                            ft.Divider(),
                            ft.Text(" Hareket Geçmişi:", weight=ft.FontWeight.BOLD),
                            ft.Text(movements_text, size=12),
                        ]),
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
    else:
        page.add(
            ft.Column(
                [
                    back_button,
                    ft.Container(height=20),
                    ft.Text(f"Takip No: {tracking_no}", weight=ft.FontWeight.BOLD),
                    ft.Text(f"Kargo Firması: {courier}", size=14),
                    ft.Text("Kargo bilgisi bulunamadı!", color="red"),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
