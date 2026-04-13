import flet as ft
from database import get_all_shipments, delete_shipment


def home_view(page: ft.Page, user: dict = None):
    page.title = "Kargo Takip - Ana Sayfa"
    page.clean()
    page.scroll = ft.ScrollMode.AUTO
    
    username = user["name"] if user else "Kullanıcı"
    user_role = user.get("role", "personel") if user else "personel"
    
    shipments_container = ft.Column([])
    
    def logout(e):
        page.current_user = None
        page.go("/login")
    
    def go_to_add(e):
        page.go("/add-shipment")
    
    def go_to_detail(tracking_number):
        page.go(f"/shipment?tracking={tracking_number}")
    
    def delete_handler(tracking_number):
        delete_shipment(tracking_number)
        load_shipments()
        page.update()
    
    def load_shipments():
        shipments = get_all_shipments()
        
        if shipments:
            shipments_container.controls = [
                ft.Text("Tüm Kargolar", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
            ]
            
            for s in shipments:
                status_color = "green" if s["status"] == "Teslim Edildi" else "blue" if s["status"] == "Yolda" else "orange"
                
                shipments_container.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Row(
                                [
                                    ft.Text(f"Takip: {s['tracking_number']}", weight=ft.FontWeight.BOLD, size=16),
                                    ft.Text(f"Durum: {s['status']}", color=status_color, size=14),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Text(f"Gönderici: {s['sender_name']}", size=12),
                            ft.Text(f"Alıcı: {s['receiver_name']}", size=12),
                            ft.Text(
                                f"Konum: {s.get('current_city') or s.get('current_location', '-')}",
                                size=12,
                                color="gray",
                            ),
                            ft.Text(f"Ucret: {s['price']} TL", size=12, color="gray"),
                            ft.Text(
                                f"Desi: {s.get('desi', 0)} | Mesafe: {s.get('distance_km', 0)} km",
                                size=12,
                                color="gray",
                            ),
                            ft.Text(
                                f"Teslim Tipi: {s.get('delivery_type', '-')}",
                                size=12,
                                color="gray",
                            ),
                            ft.Text(
                                f"Kayit Tipi: {s.get('party_type', '-')}",
                                size=12,
                                color="gray",
                            ),
                            ft.Text(
                                f"Not: {s.get('shipment_note') or '-'}",
                                size=12,
                                color="gray",
                            ),
                            ft.Container(height=10),
                            ft.Row(
                                [
                                    ft.ElevatedButton(
                                        content=ft.Text("Detay", size=12),
                                        on_click=lambda e, t=s['tracking_number']: go_to_detail(t),
                                    ),
                                    ft.ElevatedButton(
                                        content=ft.Text("Sil", size=12),
                                        bgcolor="red",
                                        on_click=lambda e, t=s['tracking_number']: delete_handler(t),
                                    ),
                                ],
                                spacing=10,
                            ),
                        ]),
                        padding=15,
                        bgcolor="white",
                        border_radius=10,
                        margin=5,
                    )
                )
        else:
            shipments_container.controls = [
                ft.Text("Henüz kargo yok.", color="gray", size=16),
            ]
        
        page.update()
    
    add_button = ft.ElevatedButton(
        content=ft.Text("Yeni Kargo Ekle"),
        bgcolor="#2196F3",
        color="white",
        on_click=go_to_add,
    )
    
    logout_button = ft.TextButton(
        content=ft.Text("Cikis"),
        on_click=logout,
    )
    
    load_shipments()
    
    page.add(
        ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(f"Hos geldin, {username}", size=24, weight=ft.FontWeight.BOLD),
                        logout_button,
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
