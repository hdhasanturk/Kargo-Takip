import flet as ft
import re
from database import add_shipment
from kargo_api import (
    get_cities,
    calculate_route,
    format_route,
    calculate_shipping_price,
    get_districts_by_city,
    get_neighborhoods_by_city_and_district,
)
from views.home_view import home_view


def add_shipment_view(page: ft.Page, user: dict = None):
    page.title = "Yeni Kargo Ekle"
    page.clean()
    page.scroll = ft.ScrollMode.AUTO
    
    cities = get_cities()
    city_options = [ft.dropdown.Option(c) for c in cities]
    
    def go_back(e):
        home_view(page, user)
    
    sender_name = ft.TextField(label="Gonderici Adi", width=300)
    sender_phone = ft.TextField(label="Gonderici Telefon", width=300)
    sender_name_error = ft.Text("", size=11, color="red", visible=False)
    sender_phone_error = ft.Text("", size=11, color="red", visible=False)
    sender_address = ft.TextField(label="Gonderici Adres", width=300, multiline=True)
    sender_city = ft.Dropdown(
        label="Gonderici Sehir",
        width=300,
        options=city_options,
    )
    sender_district = ft.Dropdown(label="Gonderici Ilce", width=300, options=[])
    sender_neighborhood = ft.Dropdown(label="Gonderici Mahalle", width=300, options=[])
    
    receiver_name = ft.TextField(label="Alici Adi", width=300)
    receiver_phone = ft.TextField(label="Alici Telefon", width=300)
    receiver_address = ft.TextField(label="Alici Adres", width=300, multiline=True)
    receiver_city = ft.Dropdown(
        label="Alici Sehir",
        width=300,
        options=city_options,
    )
    
    sender_type = ft.Dropdown(
        label="Kayit Tipi",
        width=300,
        value="gonderici",
        options=[
            ft.dropdown.Option("gonderici"),
            ft.dropdown.Option("alici"),
        ],
    )
    weight = ft.TextField(label="Agirlik (kg)", width=300)
    volume = ft.TextField(label="Desi Hacmi (cm3)", width=300)
    desi_text = ft.Text("Desi: 0", size=12, color="gray")
    distance_text = ft.Text("Mesafe: 0 km", size=12, color="gray")
    price = ft.TextField(label="Kargo Ucreti (TL) - Otomatik", width=300, read_only=True)
    payment_price = ft.TextField(label="Alicidan Tahsil Edilecek (TL)", width=300)
    delivery_type = ft.Dropdown(
        label="Teslim Tipi",
        width=300,
        value="Adrese Teslim",
        options=[
            ft.dropdown.Option("Adrese Teslim"),
            ft.dropdown.Option("Subeden Teslim Al"),
        ],
    )
    shipment_note = ft.TextField(label="Kargo Notu", width=300, multiline=True)
    
    route_preview = ft.Text("", size=12, color="gray", visible=False)
    
    result_text = ft.Text("", visible=False, color="green")

    def _validate_sender_name_inline():
        value = (sender_name.value or "").strip()
        # Ad-soyad zorunlu, sadece harf ve bosluk kabul.
        is_valid = bool(re.fullmatch(r"[A-Za-zCĞİÖŞÜçğıöşü\s]+", value)) and len(value.split()) >= 2
        if not value:
            sender_name_error.value = "Gonderici adi bos birakilamaz."
            sender_name_error.visible = True
            return False
        if not is_valid:
            sender_name_error.value = "Gecerli bir ad soyad girin (sayi kullanmayin)."
            sender_name_error.visible = True
            return False
        sender_name_error.visible = False
        return True

    def _digits_only(value):
        return "".join(ch for ch in (value or "") if ch.isdigit())

    def _normalize_phone_fields():
        sender_clean = _digits_only(sender_phone.value)[:10]
        receiver_clean = _digits_only(receiver_phone.value)
        changed = False
        if sender_phone.value != sender_clean:
            sender_phone.value = sender_clean
            changed = True
        if receiver_phone.value != receiver_clean:
            receiver_phone.value = receiver_clean
            changed = True
        if changed:
            page.update()

        sender_phone_error.visible = False

    sender_phone.on_change = lambda e: _normalize_phone_fields()
    receiver_phone.on_change = lambda e: _normalize_phone_fields()
    sender_name.on_change = lambda e: _validate_sender_name_inline()

    def update_pricing():
        if not sender_city.value or not receiver_city.value:
            return
        route = calculate_route(sender_city.value, receiver_city.value)
        calc = calculate_shipping_price(weight.value or 0, volume.value or 0, route, delivery_type.value)
        price.value = str(calc["price"])
        desi_text.value = f"Desi: {calc['desi']}"
        distance_text.value = f"Mesafe: {calc['distance_km']} km"
        route_preview.value = f"Guzergah: {' -> '.join(route)}"
        route_preview.visible = True

    def _event_value(e):
        data_value = getattr(e, "data", None)
        control_value = getattr(e.control, "value", None)
        return (data_value if data_value not in (None, "") else control_value)

    def update_sender_location_options(selected_city=None):
        selected_city = selected_city or sender_city.value
        districts = get_districts_by_city(selected_city)
        sender_district.options.clear()
        for district in districts:
            sender_district.options.append(ft.dropdown.Option(district))
        sender_district.value = None
        sender_neighborhood.options.clear()
        sender_neighborhood.value = None
        sender_district.update()
        sender_neighborhood.update()
        page.update()

    def update_sender_neighborhood_options(selected_city=None, selected_district=None):
        selected_city = selected_city or sender_city.value
        selected_district = selected_district or sender_district.value
        neighborhoods = get_neighborhoods_by_city_and_district(selected_city, selected_district)
        sender_neighborhood.options.clear()
        for neighborhood in neighborhoods:
            sender_neighborhood.options.append(ft.dropdown.Option(neighborhood))
        sender_neighborhood.value = None
        sender_neighborhood.update()
        page.update()

    def sender_city_changed(e):
        selected_city = _event_value(e)
        sender_city.value = selected_city
        update_pricing()
        update_sender_location_options(selected_city)

    def sender_district_changed(e):
        selected_district = _event_value(e)
        sender_district.value = selected_district
        update_sender_neighborhood_options(sender_city.value, selected_district)

    sender_city.on_change = sender_city_changed
    sender_district.on_change = sender_district_changed
    receiver_city.on_change = lambda e: update_pricing()
    delivery_type.on_change = lambda e: update_pricing()
    weight.on_change = lambda e: update_pricing()
    volume.on_change = lambda e: update_pricing()
    
    def save_cargo(e):
        _normalize_phone_fields()
        sender_name_ok = _validate_sender_name_inline()

        sender_name_val = (sender_name.value or "").strip()
        receiver_name_val = (receiver_name.value or "").strip()
        sender_phone_val = _digits_only(sender_phone.value)
        receiver_phone_val = _digits_only(receiver_phone.value)
        sender_address_val = (sender_address.value or "").strip()
        receiver_address_val = (receiver_address.value or "").strip()

        if not sender_name_ok:
            result_text.value = "Gonderici ad soyad bilgisini duzeltin."
            result_text.color = "red"
            result_text.visible = True
            page.update()
            return

        if not receiver_name_val:
            result_text.value = "Gonderici ve alici adi zorunludur."
            result_text.color = "red"
            result_text.visible = True
            page.update()
            return

        if not sender_phone_val or not receiver_phone_val:
            result_text.value = "Gonderici ve alici telefon zorunludur."
            result_text.color = "red"
            result_text.visible = True
            page.update()
            return

        if len(sender_phone_val) != 10 or len(receiver_phone_val) != 10:
            sender_phone_error.value = "Lutfen gecerli bir numara girin."
            sender_phone_error.visible = len(sender_phone_val) != 10
            result_text.value = "Telefonlar 10 haneli olmali (5XXXXXXXXX)."
            result_text.color = "red"
            result_text.visible = True
            page.update()
            return
        
        if not sender_city.value or not receiver_city.value:
            result_text.value = "Gonderici ve alici sehri secin."
            result_text.color = "red"
            result_text.visible = True
            page.update()
            return

        if not sender_district.value or not sender_neighborhood.value:
            result_text.value = "Gonderici icin ilce ve mahalle secimi zorunludur."
            result_text.color = "red"
            result_text.visible = True
            page.update()
            return

        if delivery_type.value == "Adrese Teslim" and (not sender_address_val or not receiver_address_val):
            result_text.value = "Adrese teslim secildiginde gonderici ve alici adresi zorunludur."
            result_text.color = "red"
            result_text.visible = True
            page.update()
            return
        
        try:
            w = float(weight.value) if weight.value else 0
            v = float(volume.value) if volume.value else 0
            update_pricing()
            p = float(price.value) if price.value else 0
            pp = float(payment_price.value) if payment_price.value else p
        except ValueError:
            result_text.value = "Sayisal alanlari duzgun girin!"
            result_text.color = "red"
            result_text.visible = True
            page.update()
            return

        if w <= 0 or v <= 0:
            result_text.value = "Agirlik ve desi hacmi sifirdan buyuk olmali."
            result_text.color = "red"
            result_text.visible = True
            page.update()
            return
        
        route = calculate_route(sender_city.value, receiver_city.value)
        route_str = format_route(route)
        calc = calculate_shipping_price(w, v, route, delivery_type.value)
        
        tracking = add_shipment(
            sender_name_val,
            sender_phone_val,
            sender_address_val,
            sender_city.value,
            receiver_name_val,
            receiver_phone_val,
            receiver_address_val,
            receiver_city.value,
            w, v, p, pp, route_str,
            delivery_type.value,
            shipment_note.value or "",
            calc["distance_km"],
            calc["desi"],
            sender_type.value,
            sender_district.value or "",
            sender_neighborhood.value or "",
        )
        
        party_label = "Gonderici" if sender_type.value == "gonderici" else "Alici"
        result_text.value = (
            f"Kargo kaydedildi!\nTakip No: {tracking}\nKayit Tipi: {party_label}\n"
            f"Guzergah: {' -> '.join(route)}\nMesafe: {calc['distance_km']} km | Desi: {calc['desi']}"
        )
        result_text.color = "green"
        result_text.visible = True
        
        sender_name.value = ""
        sender_phone.value = ""
        sender_address.value = ""
        sender_city.value = None
        sender_district.value = None
        sender_district.options = []
        sender_neighborhood.value = None
        sender_neighborhood.options = []
        receiver_name.value = ""
        receiver_phone.value = ""
        receiver_address.value = ""
        receiver_city.value = None
        sender_type.value = "gonderici"
        weight.value = ""
        volume.value = ""
        price.value = ""
        payment_price.value = ""
        delivery_type.value = "Adrese Teslim"
        shipment_note.value = ""
        desi_text.value = "Desi: 0"
        distance_text.value = "Mesafe: 0 km"
        route_preview.visible = False
        
        page.update()
    
    save_button = ft.ElevatedButton(
        content=ft.Text("Kaydet", size=16),
        width=200,
        height=45,
        bgcolor="#2196F3",
        color="white",
        on_click=save_cargo,
    )
    
    back_button = ft.ElevatedButton(
        content=ft.Text("Geri"),
        on_click=go_back,
    )
    
    page.add(
        ft.Column(
            [
                ft.Text("Yeni Kargo Ekle", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(height=20),
                
                ft.Text("GONDERICI BILGILERI", size=16, weight=ft.FontWeight.BOLD, color="gray"),
                sender_name,
                sender_name_error,
                sender_phone,
                sender_phone_error,
                ft.Text("Sadece rakam girin (10 hane).", size=11, color="gray"),
                sender_city,
                sender_district,
                sender_neighborhood,
                sender_address,
                ft.Container(height=20),
                
                ft.Text("ALICI BILGILERI", size=16, weight=ft.FontWeight.BOLD, color="gray"),
                receiver_name,
                receiver_phone,
                ft.Text("Sadece rakam girin (10 hane).", size=11, color="gray"),
                receiver_city,
                receiver_address,
                route_preview,
                ft.Text(
                    "Guzergah, sehir baglantilarina gore en az aktarma (BFS) ile hesaplanir.",
                    size=11,
                    color="gray",
                ),
                ft.Container(height=20),
                
                ft.Text("KARGO BILGILERI", size=16, weight=ft.FontWeight.BOLD, color="gray"),
                sender_type,
                weight,
                volume,
                desi_text,
                distance_text,
                price,
                payment_price,
                delivery_type,
                shipment_note,
                ft.Container(height=20),
                
                result_text,
                ft.Container(height=10),
                
                save_button,
                ft.Container(height=10),
                back_button,
                ft.Container(height=50),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
    )
