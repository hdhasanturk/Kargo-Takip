import flet as ft
from database import get_shipment_by_tracking, update_shipment_location
from kargo_api import get_cities, get_route_progress
from views.home_view import home_view


def shipment_detail_view(page: ft.Page, tracking_number: str, user: dict = None):
    page.title = "Kargo Detay"
    page.clean()
    page.scroll = ft.ScrollMode.AUTO
    
    shipment = get_shipment_by_tracking(tracking_number)
    
    if not shipment:
        page.add(
            ft.Column(
                [
                    ft.Text("Kargo bulunamadi!", color="red", size=18),
                    ft.ElevatedButton(
                        content=ft.Text("Geri"),
                        on_click=lambda e: home_view(page, user)
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
        return
    
    cities = get_cities()
    city_options = [ft.dropdown.Option(c, c) for c in cities]
    
    route_list = shipment["route"].split(",") if shipment["route"] else []
    current_city = shipment["current_city"] or shipment["sender_city"]
    
    status_dropdown = ft.Dropdown(
        label="Durum",
        width=300,
        options=[
            ft.dropdown.Option("Hazirlaniyor", "Hazirlaniyor"),
            ft.dropdown.Option("Yolda", "Yolda"),
            ft.dropdown.Option("Teslim Edildi", "Teslim Edildi"),
        ],
        value=shipment["status"],
    )
    
    city_dropdown = ft.Dropdown(
        label="Guncel Sehir",
        width=300,
        options=city_options,
        value=current_city,
    )
    
    result_text = ft.Text("", visible=False, color="green")
    
    def go_back(e):
        home_view(page, user)
    
    def update_cargo(e):
        status = status_dropdown.value
        current = city_dropdown.value
        
        update_shipment_location(tracking_number, current, status, shipment["route"])
        
        result_text.value = "Kargo guncellendi!"
        if status == "Teslim Edildi":
            result_text.value = "Kargo teslim edildi! Bildirim gonderildi."
        result_text.color = "green"
        result_text.visible = True
        page.update()
    
    update_button = ft.ElevatedButton(
        content=ft.Text("Guncelle", size=16),
        width=200,
        height=45,
        bgcolor="#2196F3",
        color="white",
        on_click=update_cargo,
    )
    
    back_button = ft.ElevatedButton(
        content=ft.Text("Geri"),
        on_click=go_back,
    )
    
    status_color = "green" if shipment["status"] == "Teslim Edildi" else "blue" if shipment["status"] == "Yolda" else "orange"
    
    route_widgets = []
    if route_list:
        progress = get_route_progress(route_list, current_city)
        
        route_widgets.append(
            ft.Text(f"Ilerleme: %{progress['progress']}", size=14, weight=ft.FontWeight.BOLD)
        )
        
        for i, city in enumerate(route_list):
            if city in progress['completed']:
                icon = "✓"
                color = "green"
            elif city == current_city:
                icon = ">>"
                color = "blue"
            else:
                icon = "○"
                color = "gray"
            
            route_widgets.append(
                ft.Text(f"{icon} {city}", color=color, size=14)
            )
    
    page.add(
        ft.Column(
            [
                ft.Text("Kargo Detay", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(height=20),
                
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"Takip No: {shipment['tracking_number']}", weight=ft.FontWeight.BOLD, size=18),
                        ft.Text(f"Durum: {shipment['status']}", color=status_color, size=16),
                        ft.Text(f"Kayit Tarihi: {shipment['created_date']}", size=12, color="gray"),
                    ]),
                    padding=15,
                    bgcolor="#E0E0E0",
                    border_radius=10,
                ),
                ft.Container(height=20),
                
                ft.Text("GONDERICI", size=16, weight=ft.FontWeight.BOLD, color="gray"),
                ft.Text(f"Ad: {shipment['sender_name']}", size=14),
                ft.Text(f"Sehir: {shipment['sender_city']}", size=14),
                ft.Text(f"Telefon: {shipment['sender_phone'] or '-'}", size=12),
                ft.Text(f"Adres: {shipment['sender_address'] or '-'}", size=12),
                ft.Container(height=15),
                
                ft.Text("ALICI", size=16, weight=ft.FontWeight.BOLD, color="gray"),
                ft.Text(f"Ad: {shipment['receiver_name']}", size=14),
                ft.Text(f"Sehir: {shipment['receiver_city']}", size=14),
                ft.Text(f"Telefon: {shipment['receiver_phone'] or '-'}", size=12),
                ft.Text(f"Adres: {shipment['receiver_address'] or '-'}", size=12),
                ft.Container(height=15),
                
                ft.Text("GUZERGAH TAKIBI", size=16, weight=ft.FontWeight.BOLD, color="gray"),
                *route_widgets,
                ft.Container(height=15),
                
                ft.Text("ODEME BILGILERI", size=16, weight=ft.FontWeight.BOLD, color="gray"),
                ft.Text(f"Kargo Ucreti: {shipment['price']} TL", size=14),
                ft.Text(f"Alicidan Tahsil: {shipment['payment_price']} TL", size=14, color="green"),
                ft.Container(height=15),
                
                ft.Text("KARGO BILGILERI", size=16, weight=ft.FontWeight.BOLD, color="gray"),
                ft.Text(f"Agirlik: {shipment['weight']} kg", size=14),
                ft.Text(f"Hacim: {shipment['volume']} cm3", size=14),
                ft.Text(f"Desi: {shipment.get('desi', 0)}", size=14),
                ft.Text(f"Mesafe: {shipment.get('distance_km', 0)} km", size=14),
                ft.Text(f"Teslim Tipi: {shipment.get('delivery_type', '-')}", size=14),
                ft.Text(f"Kayit Tipi: {shipment.get('party_type', '-')}", size=14),
                ft.Text(f"Not: {shipment.get('shipment_note') or '-'}", size=12, color="gray"),
                ft.Container(height=20),
                
                ft.Text("GUNCELLEME", size=16, weight=ft.FontWeight.BOLD, color="gray"),
                city_dropdown,
                status_dropdown,
                ft.Container(height=10),
                result_text,
                ft.Container(height=10),
                update_button,
                ft.Container(height=10),
                back_button,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
    )
