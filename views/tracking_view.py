import flet as ft
from database import get_shipment_for_party


def tracking_view(page: ft.Page):
    page.title = "Kargo Takip Sorgu"
    page.clean()
    page.scroll = ft.ScrollMode.AUTO

    tracking_field = ft.TextField(label="Takip Kodu", width=320)
    party_type = ft.Dropdown(
        label="Kisi Tipi",
        width=320,
        value="gonderici",
        options=[
            ft.dropdown.Option("gonderici", "Gonderici"),
            ft.dropdown.Option("alici", "Alici"),
        ],
    )
    phone_field = ft.TextField(label="Telefon", width=320)
    result_box = ft.Column([])
    info_text = ft.Text("", visible=False)

    def do_search(e):
        tracking = (tracking_field.value or "").strip()
        phone = (phone_field.value or "").strip()
        if not tracking or not phone:
            info_text.value = "Takip kodu ve telefon zorunludur."
            info_text.color = "red"
            info_text.visible = True
            result_box.controls = []
            page.update()
            return

        shipment = get_shipment_for_party(tracking, party_type.value, phone)
        if not shipment:
            info_text.value = "Kayit bulunamadi. Bilgileri kontrol edin."
            info_text.color = "red"
            info_text.visible = True
            result_box.controls = []
            page.update()
            return

        info_text.visible = False
        result_box.controls = [
            ft.Text(f"Takip No: {shipment['tracking_number']}", weight=ft.FontWeight.BOLD, size=16),
            ft.Text(f"Durum: {shipment['status']}"),
            ft.Text(f"Guncel Sehir: {shipment.get('current_city') or '-'}"),
            ft.Text(f"Gonderici: {shipment['sender_name']}"),
            ft.Text(f"Alici: {shipment['receiver_name']}"),
            ft.Text(f"Teslim Tipi: {shipment.get('delivery_type', '-')}"),
            ft.Text(f"Not: {shipment.get('shipment_note') or '-'}", color="gray"),
            ft.Text(f"Ucret: {shipment['price']} TL"),
        ]
        page.update()

    page.add(
        ft.Column(
            [
                ft.Text("Kargo Takip Sorgu", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                tracking_field,
                party_type,
                phone_field,
                ft.ElevatedButton("Sorgula", on_click=do_search),
                info_text,
                ft.Container(height=10),
                result_box,
                ft.Container(height=15),
                ft.TextButton("Giris ekranina don", on_click=lambda e: page.go("/login")),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )
