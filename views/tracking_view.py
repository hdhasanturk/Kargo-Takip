from datetime import datetime, timedelta
import logging

import flet as ft

from database import get_shipment_for_party, get_history
from kargo_api import get_route_progress, get_shipment_status, estimate_delivery_time


def _build_timeline_widgets(history):
    widgets = []
    if not history:
        widgets.append(ft.Text("Henuz kayit yok", size=12, color="gray"))
        return widgets

    for i, h in enumerate(history):
        is_last = i == len(history) - 1
        status_colors = {
            "Hazirlaniyor": ft.Colors.ORANGE,
            "Yolda": ft.Colors.BLUE,
            "Teslim Edildi": ft.Colors.GREEN,
        }
        color = status_colors.get(h["status"], ft.Colors.GRAY)
        line_color = ft.Colors.GRAY_300 if not is_last else ft.Colors.TRANSPARENT

        widgets.append(
            ft.Row(
                [
                    ft.Column(
                        [
                            ft.Container(width=14, height=14, border_radius=7, bgcolor=color),
                            ft.Container(width=2, height=36, bgcolor=line_color)
                            if not is_last else ft.Container(height=0),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=0,
                    ),
                    ft.Column(
                        [
                            ft.Text(h["created_at"], size=11, color="gray"),
                            ft.Text(h["status"], size=14, weight=ft.FontWeight.BOLD, color=color),
                            ft.Text(h["description"], size=12),
                            ft.Text(h["location_city"], size=11, color="gray")
                            if h["location_city"] else ft.Text(""),
                        ],
                        spacing=2,
                    ),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.START,
            )
        )
    return widgets


def tracking_view(page: ft.Page):
    page.title = "Kargo Takip Sorgu"
    page.clean()
    page.scroll = ft.ScrollMode.AUTO
    logger = logging.getLogger("app")

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
    last_shipment = {"data": None}

    def _digits_only(value):
        return "".join(ch for ch in (value or "") if ch.isdigit())

    def normalize_phone_input(e):
        clean = _digits_only(phone_field.value)
        if phone_field.value != clean:
            phone_field.value = clean
            page.update()

    phone_field.on_change = normalize_phone_input

    def render_result(shipment):
        last_shipment["data"] = shipment
        route_list = shipment["route"].split(",") if shipment.get("route") else []
        progress_info = get_route_progress(route_list, shipment.get("current_city")) if route_list else None
        progress_line = (
            f"Ilerleme: %{progress_info['progress']} | Kalan durak: {len(progress_info['remaining'])}"
            if progress_info else "Ilerleme bilgisi yok."
        )

        delivery_days = estimate_delivery_time(route_list)
        if shipment.get("created_date"):
            try:
                created = datetime.strptime(shipment["created_date"], "%Y-%m-%d %H:%M")
                est_date = created + timedelta(days=delivery_days)
                est_str = est_date.strftime("%d-%m-%Y")
            except ValueError:
                est_str = f"{delivery_days} gun"
        else:
            est_str = f"{delivery_days} gun"

        history = get_history(shipment["tracking_number"])
        timeline_widgets = _build_timeline_widgets(history)

        api_tracking = shipment.get("real_tracking_number") or shipment.get("tracking_number")
        api_status = get_shipment_status(api_tracking, shipment.get("courier"))
        api_source = api_status.get("source") if api_status else "-"
        api_error = api_status.get("error") if api_status else "API hatasi"
        api_sync = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        api_movements = []
        if api_status and api_status.get("movements"):
            for movement in api_status["movements"][:3]:
                api_movements.append(
                    ft.Text(
                        f"* {movement['date']} - {movement['location']}: {movement['description']}",
                        size=11, color="gray",
                    )
                )

        result_box.controls = [
            ft.Text(f"Takip No: {shipment['tracking_number']}", weight=ft.FontWeight.BOLD, size=16),
            ft.Text(f"Gercek Takip No: {shipment.get('real_tracking_number') or '-'}"),
            ft.Text(f"Kargo Firmasi: {shipment.get('courier') or '-'}"),
            ft.Text(f"Durum: {shipment['status']}", weight=ft.FontWeight.BOLD),
        ]
        if api_status:
            result_box.controls.extend([
                ft.Text(f"API Durum: {api_status.get('status', '-')}"),
                ft.Text(f"API Son Guncelleme: {api_status.get('last_update', '-')}"),
                ft.Text(f"API Kaynak: {api_source}"),
                ft.Text(f"API Senkron: {api_sync}", size=11, color="gray"),
            ])
            if api_error:
                result_box.controls.append(
                    ft.Text(f"API Hata: {api_error}", size=11, color="red"),
                )
        if api_movements:
            result_box.controls.extend(api_movements)
        result_box.controls.extend([
            ft.Container(height=10),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("TAHMINI TESLIMAT", size=14, weight=ft.FontWeight.BOLD, color="gray"),
                        ft.Text(f"Tahmini Tarih: {est_str}", size=16, color="green",
                                weight=ft.FontWeight.BOLD),
                    ]
                ),
                padding=10, bgcolor="#E8F5E9", border_radius=8,
            ),
            ft.Container(height=10),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("DURUM GECMISI", size=14, weight=ft.FontWeight.BOLD, color="gray"),
                        *timeline_widgets,
                    ],
                    spacing=5,
                ),
                padding=10, bgcolor="#FAFAFA", border_radius=8,
            ),
            ft.Container(height=10),
            ft.Text(progress_line),
            ft.Text(f"Guncel Sehir: {shipment.get('current_city') or '-'}"),
            ft.Text(f"Gonderici: {shipment['sender_name']}"),
            ft.Text(f"Alici: {shipment['receiver_name']}"),
            ft.Text(f"Agirlik: {shipment.get('weight', 0)} kg | Desi: {shipment.get('desi', 0)}"),
            ft.Text(f"Mesafe: {shipment.get('distance_km', 0)} km"),
            ft.Text(f"Teslim Tipi: {shipment.get('delivery_type', '-')}"),
            ft.Text(f"Not: {shipment.get('shipment_note') or '-'}", color="gray"),
            ft.Text(f"Ucret: {shipment['price']} TL"),
            ft.Text(f"Kayit Tarihi: {shipment.get('created_date') or '-'}", size=11, color="gray"),
        ])

        refresh_button.disabled = False
        refresh_button.update()
        page.update()

    def refresh_api(e):
        if not last_shipment["data"]:
            return
        render_result(last_shipment["data"])

    refresh_button = ft.ElevatedButton("API Yenile", on_click=refresh_api, disabled=True)

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
            logger.warning("Tracking search failed: tracking=%s party=%s", tracking, party_type.value)
            info_text.value = "Kayit bulunamadi. Bilgileri kontrol edin."
            info_text.color = "red"
            info_text.visible = True
            result_box.controls = []
            page.update()
            return

        logger.info("Tracking search success: tracking=%s party=%s", tracking, party_type.value)
        info_text.visible = False
        render_result(shipment)

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
                refresh_button,
                info_text,
                ft.Container(height=10),
                result_box,
                ft.Container(height=15),
                ft.TextButton("Giris ekranina don", on_click=lambda e: page.go("/login")),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )
