import logging

import flet as ft

from database import delete_shipment, get_all_shipments


def home_view(page: ft.Page, user: dict = None):
    page.title = "Kargo Takip - Ana Sayfa"
    page.clean()
    page.scroll = ft.ScrollMode.AUTO

    logger = logging.getLogger("app")

    username = user["name"] if user else "Kullanici"
    is_admin = bool(user) and (user.get("role") == "admin" or user.get("username") == "admin")
    shipments_container = ft.Column([])

    def logout(e):
        user_label = user.get("username") if isinstance(user, dict) else "-"
        logger.info("Logout: user=%s", user_label)
        page.current_user = None
        page.go("/login")

    def go_to_add(e):
        page.go("/add-shipment")

    def go_to_detail(tracking_number):
        page.go(f"/shipment/{tracking_number}")

    def delete_handler(tracking_number):
        delete_shipment(tracking_number)
        user_label = user.get("username") if isinstance(user, dict) else "-"
        logger.info("Shipment deleted: tracking=%s user=%s", tracking_number, user_label)
        load_shipments()
        page.update()

    def load_shipments():
        shipments = get_all_shipments()

        if not shipments:
            shipments_container.controls = [
                ft.Text("Henuz kargo yok.", color="gray", size=16),
            ]
            page.update()
            return

        shipments_container.controls = [
            ft.Text("Tum Kargolar", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(height=10),
        ]

        for shipment in shipments:
            status_color = (
                "green"
                if shipment["status"] == "Teslim Edildi"
                else "blue"
                if shipment["status"] == "Yolda"
                else "orange"
            )

            shipments_container.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(
                                        f"Takip: {shipment['tracking_number']}",
                                        weight=ft.FontWeight.BOLD,
                                        size=16,
                                    ),
                                    ft.Text(
                                        f"Durum: {shipment['status']}",
                                        color=status_color,
                                        size=14,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Text(f"Gonderici: {shipment['sender_name']}", size=12),
                            ft.Text(f"Alici: {shipment['receiver_name']}", size=12),
                            ft.Text(
                                f"Konum: {shipment.get('current_city') or '-'}",
                                size=12,
                                color="gray",
                            ),
                            ft.Text(f"Ucret: {shipment['price']} TL", size=12, color="gray"),
                            ft.Text(
                                f"Desi: {shipment.get('desi', 0)} | Mesafe: {shipment.get('distance_km', 0)} km",
                                size=12,
                                color="gray",
                            ),
                            ft.Text(
                                f"Teslim Tipi: {shipment.get('delivery_type', '-')}",
                                size=12,
                                color="gray",
                            ),
                            ft.Text(
                                f"Kayit Tipi: {shipment.get('party_type', '-')}",
                                size=12,
                                color="gray",
                            ),
                            ft.Text(
                                f"Not: {shipment.get('shipment_note') or '-'}",
                                size=12,
                                color="gray",
                            ),
                            ft.Container(height=10),
                            ft.Row(
                                [
                                    ft.ElevatedButton(
                                        content=ft.Text("Detay", size=12),
                                        on_click=lambda e, tracking=shipment["tracking_number"]: go_to_detail(tracking),
                                    ),
                                    ft.ElevatedButton(
                                        content=ft.Text("Sil", size=12),
                                        bgcolor="red",
                                        on_click=lambda e, tracking=shipment["tracking_number"]: delete_handler(tracking),
                                    ),
                                ],
                                spacing=10,
                            ),
                        ]
                    ),
                    padding=15,
                    bgcolor="white",
                    border_radius=10,
                    margin=5,
                )
            )

        page.update()

    add_button = ft.ElevatedButton(
        content=ft.Text("Yeni Kargo Ekle"),
        bgcolor="#2196F3",
        color="white",
        on_click=go_to_add,
    )
    logout_button = ft.TextButton(content=ft.Text("Cikis"), on_click=logout)
    admin_button = ft.ElevatedButton(
        content=ft.Text("Kullanicilar"),
        on_click=lambda e: page.go("/users"),
        visible=is_admin,
    )

    header_actions = [logout_button]
    if is_admin:
        header_actions.insert(0, admin_button)

    load_shipments()

    page.add(
        ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(f"Hos geldin, {username}", size=24, weight=ft.FontWeight.BOLD),
                        ft.Row(header_actions, spacing=10),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Container(height=20),
                add_button,
                ft.Container(height=20),
                shipments_container,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
    )
