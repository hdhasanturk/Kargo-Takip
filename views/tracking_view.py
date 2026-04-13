import flet as ft
from database import get_shipment_for_party
from kargo_api import get_route_progress


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

    def _digits_only(value):
        return "".join(ch for ch in (value or "") if ch.isdigit())

    def normalize_phone_input(e):
        clean = _digits_only(phone_field.value)
        if phone_field.value != clean:
            phone_field.value = clean
            page.update()

    phone_field.on_change = normalize_phone_input

    def do_search(e):
        tracking = (tracking_field.value or "").strip()
        phone = _digits_only(phone_field.value)
        if not tracking or not phone:
            info_text.value = "Takip kodu ve telefon zorunludur."
            info_text.color = "red"
            info_text.visible = True
            result_box.controls = []
            page.update()
            return

        if len(phone) != 10:
            info_text.value = "Telefon 10 haneli olmali (5XXXXXXXXX)."
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
        route_list = shipment["route"].split(",") if shipment.get("route") else []
        progress_info = get_route_progress(route_list, shipment.get("current_city")) if route_list else None
        progress_line = (
            f"Ilerleme: %{progress_info['progress']} | Kalan durak: {len(progress_info['remaining'])}"
            if progress_info
            else "Ilerleme bilgisi yok."
        )

        result_box.controls = [
            ft.Text(f"Takip No: {shipment['tracking_number']}", weight=ft.FontWeight.BOLD, size=16),
            ft.Text(f"Durum: {shipment['status']}"),
            ft.Text(f"Guncel Sehir: {shipment.get('current_city') or '-'}"),
            ft.Text(progress_line),
            ft.Text(f"Gonderici: {shipment['sender_name']}"),
            ft.Text(f"Alici: {shipment['receiver_name']}"),
            ft.Text(f"Agirlik: {shipment.get('weight', 0)} kg | Desi: {shipment.get('desi', 0)}"),
            ft.Text(f"Mesafe: {shipment.get('distance_km', 0)} km"),
            ft.Text(f"Teslim Tipi: {shipment.get('delivery_type', '-')}"),
            ft.Text(f"Not: {shipment.get('shipment_note') or '-'}", color="gray"),
            ft.Text(f"Ucret: {shipment['price']} TL"),
            ft.Text(f"Kayit Tarihi: {shipment.get('created_date') or '-'}", size=11, color="gray"),
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
                ft.Text("Telefon sadece rakam ve 10 hane olmali.", size=11, color="gray"),
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
