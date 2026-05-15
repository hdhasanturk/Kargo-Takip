import json
import logging

import flet as ft

from database import get_shipment_by_tracking, update_shipment_location, get_history
from kargo_api import get_cities, get_route_progress, estimate_delivery_time, calculate_distance_km
from views.home_view import home_view


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
                            ft.Container(
                                width=16,
                                height=16,
                                border_radius=8,
                                bgcolor=color,
                            ),
                            ft.Container(
                                width=2,
                                height=40,
                                bgcolor=line_color,
                                visible=not is_last,
                            ) if not is_last else ft.Container(height=0),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=0,
                    ),
                    ft.Column(
                        [
                            ft.Text(h["created_at"], size=11, color="gray"),
                            ft.Text(h["status"], size=14, weight=ft.FontWeight.BOLD, color=color),
                            ft.Text(h["description"], size=12),
                            ft.Text(h["location_city"], size=11, color="gray") if h["location_city"] else ft.Text(""),
                        ],
                        spacing=2,
                    ),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.START,
            )
        )
    return widgets


def shipment_detail_view(page: ft.Page, tracking_number: str, user: dict = None):
    page.title = "Kargo Detay"
    page.clean()
    page.scroll = ft.ScrollMode.AUTO
    logger = logging.getLogger("app")

    shipment = get_shipment_by_tracking(tracking_number)
    if not shipment:
        page.add(
            ft.Column(
                [
                    ft.Text("Kargo bulunamadi!", color="red", size=18),
                    ft.ElevatedButton(
                        content=ft.Text("Geri"),
                        on_click=lambda e: home_view(page, user),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
        return

    current_city = shipment["current_city"] or shipment["sender_city"]
    route_list = shipment["route"].split(",") if shipment["route"] else []
    parcels_count = None
    parcels_raw = shipment.get("parcels_json")
    if parcels_raw:
        try:
            parcels_data = json.loads(parcels_raw)
            if isinstance(parcels_data, list):
                parcels_count = len(parcels_data)
        except ValueError:
            parcels_count = None

    city_dropdown = ft.Dropdown(
        label="Guncel Sehir",
        width=300,
        options=[ft.dropdown.Option(c) for c in get_cities()],
        value=current_city,
    )
    status_dropdown = ft.Dropdown(
        label="Durum",
        width=300,
        options=[
            ft.dropdown.Option("Hazirlaniyor"),
            ft.dropdown.Option("Yolda"),
            ft.dropdown.Option("Teslim Edildi"),
        ],
        value=shipment["status"],
    )
    result_text = ft.Text("", visible=False, color="green")

    route_distance = calculate_distance_km(route_list) if route_list else 0
    delivery_days = estimate_delivery_time(route_list)
    from datetime import datetime, timedelta
    if shipment.get("created_date"):
        try:
            created = datetime.strptime(shipment["created_date"], "%Y-%m-%d %H:%M")
            est_date = created + timedelta(days=delivery_days)
            est_str = est_date.strftime("%d-%m-%Y")
        except ValueError:
            est_str = f"{delivery_days} gun"
    else:
        est_str = f"{delivery_days} gun"

    history = get_history(tracking_number)
    timeline_widgets = _build_timeline_widgets(history)

    def go_back(e):
        home_view(page, user)

    def update_cargo(e):
        status = status_dropdown.value
        current = city_dropdown.value
        update_shipment_location(tracking_number, current, status, shipment["route"])
        user_label = user.get("username") if isinstance(user, dict) else "-"
        logger.info("Shipment updated: tracking=%s status=%s current_city=%s user=%s",
                     tracking_number, status, current, user_label)
        result_text.value = "Kargo guncellendi!"
        if status == "Teslim Edildi":
            result_text.value = "Kargo teslim edildi! Bildirim gonderildi."
        result_text.color = "green"
        result_text.visible = True
        page.update()

    status_color = (
        "green" if shipment["status"] == "Teslim Edildi"
        else "blue" if shipment["status"] == "Yolda"
        else "orange"
    )

    route_widgets = []
    if route_list:
        progress = get_route_progress(route_list, current_city)
        route_widgets.append(
            ft.Text(f"Ilerleme: %{progress['progress']}", size=14, weight=ft.FontWeight.BOLD)
        )
        for city in route_list:
            if city in progress["completed"]:
                icon = "[x]"; color = "green"
            elif city == current_city:
                icon = ">>"; color = "blue"
            else:
                icon = "[ ]"; color = "gray"
            route_widgets.append(ft.Text(f"{icon} {city}", color=color, size=14))

    page.add(
        ft.Column(
            [
                ft.Text("Kargo Detay", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(f"Takip No: {shipment['tracking_number']}",
                                    weight=ft.FontWeight.BOLD, size=18),
                            ft.Text(f"Gercek Takip No: {shipment.get('real_tracking_number') or '-'}",
                                    size=12, color="gray"),
                            ft.Text(f"Kargo Firmasi: {shipment.get('courier') or '-'}",
                                    size=12, color="gray"),
                            ft.Text(f"Durum: {shipment['status']}", color=status_color, size=16),
                            ft.Text(f"Kayit Tarihi: {shipment['created_date']}", size=12, color="gray"),
                        ]
                    ),
                    padding=15, bgcolor="#E0E0E0", border_radius=10,
                ),
                ft.Container(height=10),
                ft.Text("TAHMINI TESLIMAT", size=16, weight=ft.FontWeight.BOLD, color="gray"),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(f"Tahmini Tarih: {est_str}", size=16, color="green",
                                    weight=ft.FontWeight.BOLD),
                            ft.Text(f"Mesafe: {route_distance} km | Rota: {len(route_list)} durak",
                                    size=12, color="gray"),
                        ]
                    ),
                    padding=15, bgcolor="#E8F5E9", border_radius=10,
                ),
                ft.Container(height=10),
                ft.Text("DURUM GECMISI", size=16, weight=ft.FontWeight.BOLD, color="gray"),
                ft.Container(
                    content=ft.Column(timeline_widgets, spacing=5),
                    padding=15, bgcolor="#FAFAFA", border_radius=10,
                ),
                ft.Container(height=10),
                ft.Text("GUZERGAH TAKIBI", size=16, weight=ft.FontWeight.BOLD, color="gray"),
                *route_widgets,
                ft.Container(height=10),
                ft.Text("GONDERICI", size=16, weight=ft.FontWeight.BOLD, color="gray"),
                ft.Text(f"Ad: {shipment['sender_name']}", size=14),
                ft.Text(f"Sehir: {shipment['sender_city']}", size=14),
                ft.Text(f"Ilce: {shipment.get('sender_county') or '-'}", size=12),
                ft.Text(f"Mahalle: {shipment.get('sender_neighborhood') or '-'}", size=12),
                ft.Text(f"Telefon: {shipment['sender_phone'] or '-'}", size=12),
                ft.Text(f"Adres: {shipment['sender_address'] or '-'}", size=12),
                ft.Container(height=10),
                ft.Text("ALICI", size=16, weight=ft.FontWeight.BOLD, color="gray"),
                ft.Text(f"Ad: {shipment['receiver_name']}", size=14),
                ft.Text(f"Sehir: {shipment['receiver_city']}", size=14),
                ft.Text(f"Ilce: {shipment.get('receiver_county') or '-'}", size=12),
                ft.Text(f"Mahalle: {shipment.get('receiver_neighborhood') or '-'}", size=12),
                ft.Text(f"Telefon: {shipment['receiver_phone'] or '-'}", size=12),
                ft.Text(f"Adres: {shipment['receiver_address'] or '-'}", size=12),
                ft.Container(height=10),
                ft.Text("ODEME BILGILERI", size=16, weight=ft.FontWeight.BOLD, color="gray"),
                ft.Text(f"Kargo Ucreti: {shipment['price']} TL", size=14),
                ft.Text(f"Alicidan Tahsil: {shipment['payment_price']} TL", size=14, color="green"),
                ft.Container(height=10),
                ft.Text("KARGO BILGILERI", size=16, weight=ft.FontWeight.BOLD, color="gray"),
                ft.Text(f"Koli Sayisi: {parcels_count if parcels_count is not None else '-'}", size=14),
                ft.Text(f"Agirlik: {shipment['weight']} kg", size=14),
                ft.Text(f"Hacim: {shipment['volume']} cm3", size=14),
                ft.Text(f"Desi: {shipment.get('desi', 0)}", size=14),
                ft.Text(f"Mesafe: {shipment.get('distance_km', 0)} km", size=14),
                ft.Text(f"Teslim Tipi: {shipment.get('delivery_type', '-')}", size=14),
                ft.Text(f"Kayit Tipi: {shipment.get('party_type', '-')}", size=14),
                ft.Text(f"Not: {shipment.get('shipment_note') or '-'}", size=12, color="gray"),
                ft.Container(height=15),
                ft.Text("GUNCELLEME", size=16, weight=ft.FontWeight.BOLD, color="gray"),
                city_dropdown,
                status_dropdown,
                ft.Container(height=10),
                result_text,
                ft.Container(height=10),
                ft.ElevatedButton(
                    content=ft.Text("Guncelle", size=16),
                    width=200, height=45, bgcolor="#2196F3", color="white",
                    on_click=update_cargo,
                ),
                ft.Container(height=10),
                ft.ElevatedButton(content=ft.Text("Geri"), on_click=go_back),
                ft.Container(height=50),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=6,
        )
    )
