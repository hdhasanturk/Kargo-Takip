import json
import logging

import flet as ft

from database import add_shipment
from import_location_data import ensure_location_data
from kargo_api import (
    calculate_route,
    calculate_shipping_price,
    format_route,
    get_cities,
    get_counties_by_city,
    get_neighborhoods_by_county,
)
from views.home_view import home_view


def add_shipment_view(page: ft.Page, user: dict = None):
    page.title = "Yeni Kargo Ekle"
    page.clean()
    page.scroll = ft.ScrollMode.AUTO

    logger = logging.getLogger("app")

    ensure_location_data()
    cities = get_cities()
    city_options = [ft.dropdown.Option(city, city) for city in cities]

    sender_name = ft.TextField(label="Gonderici Adi", width=300)
    sender_phone = ft.TextField(label="Gonderici Telefon", width=300)
    sender_name_error = ft.Text("", size=11, color="red", visible=False)
    sender_phone_error = ft.Text("", size=11, color="red", visible=False)
    sender_address = ft.TextField(label="Gonderici Adres", width=300, multiline=True)
    sender_city = ft.Dropdown(label="Gonderici Sehir", width=300, options=city_options)
    sender_county = ft.Dropdown(label="Gonderici Ilce", width=300, options=[], disabled=True)
    sender_neighborhood = ft.Dropdown(label="Gonderici Mahalle", width=300, options=[], disabled=True)
    confirm_city_button = ft.ElevatedButton(content=ft.Text("Sehri Onayla", size=12), width=140)
    confirm_county_button = ft.ElevatedButton(
        content=ft.Text("Ilceyi Onayla", size=12),
        width=140,
        disabled=True,
    )

    receiver_name = ft.TextField(label="Alici Adi", width=300)
    receiver_phone = ft.TextField(label="Alici Telefon", width=300)
    receiver_address = ft.TextField(label="Alici Adres", width=300, multiline=True)
    receiver_city = ft.Dropdown(label="Alici Sehir", width=300, options=city_options)
    receiver_county = ft.Dropdown(label="Alici Ilce", width=300, options=[], disabled=True)
    receiver_neighborhood = ft.Dropdown(label="Alici Mahalle", width=300, options=[], disabled=True)
    confirm_receiver_city_button = ft.ElevatedButton(
        content=ft.Text("Sehri Onayla", size=12),
        width=140,
    )
    confirm_receiver_county_button = ft.ElevatedButton(
        content=ft.Text("Ilceyi Onayla", size=12),
        width=140,
        disabled=True,
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
    weight = ft.TextField(label="Toplam Agirlik (kg)", width=300, read_only=True)
    volume = ft.TextField(label="Toplam Hacim (cm3)", width=300, read_only=True)
    desi_text = ft.Text("Toplam Desi: 0", size=12, color="gray")
    billable_text = ft.Text("Faturalandirilan Agirlik: 0 kg", size=12, color="gray")
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
    courier_code = ft.TextField(label="Kargo Firmasi (Courier Code)", width=300)
    real_tracking_number = ft.TextField(label="Gercek Takip No (Ship24)", width=300)

    route_preview = ft.Text("", size=12, color="gray", visible=False)
    result_text = ft.Text("", visible=False, color="green")

    location_row = ft.Column(
        [
            ft.Row(
                [sender_city, confirm_city_button],
                spacing=10,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(
                [sender_county, confirm_county_button],
                spacing=10,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(
                [sender_neighborhood],
                spacing=10,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        spacing=6,
        alignment=ft.MainAxisAlignment.CENTER,
    )
    location_status = ft.Text("", size=11, color="gray", visible=False)
    receiver_location_row = ft.Column(
        [
            ft.Row(
                [receiver_city, confirm_receiver_city_button],
                spacing=10,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(
                [receiver_county, confirm_receiver_county_button],
                spacing=10,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(
                [receiver_neighborhood],
                spacing=10,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        spacing=6,
        alignment=ft.MainAxisAlignment.CENTER,
    )
    receiver_location_status = ft.Text("", size=11, color="gray", visible=False)
    parcels = []
    parcels_column = ft.Column([], spacing=6)
    parcel_error_text = ft.Text("", size=11, color="red", visible=False)

    def _digits_only(value):
        return "".join(ch for ch in (value or "") if ch.isdigit())

    def _normalize_decimal(value):
        text = (value or "").replace(",", ".")
        cleaned = []
        dot_seen = False
        for ch in text:
            if ch.isdigit():
                cleaned.append(ch)
            elif ch == "." and not dot_seen:
                cleaned.append(ch)
                dot_seen = True
        return "".join(cleaned)

    def _to_float(value):
        if value is None:
            return None
        text = str(value).strip()
        if not text:
            return None
        try:
            return float(text)
        except ValueError:
            return None

    def _format_number(value, decimals=2):
        text = f"{value:.{decimals}f}"
        if "." in text:
            text = text.rstrip("0").rstrip(".")
        return text

    def _calculate_totals(parcels_data, route, delivery_type_value):
        total_price = 0
        total_billable = 0
        total_volume = 0
        distance_km = 0

        for parcel in parcels_data:
            total_volume += parcel["volume_cm3"]
            calc = calculate_shipping_price(
                parcel["weight_kg"],
                parcel["volume_cm3"],
                route,
                delivery_type_value,
            )
            total_price += calc["price"]
            total_billable += calc["billable_weight"]
            distance_km = calc["distance_km"]

        total_desi = round(total_volume / 3000, 2) if total_volume > 0 else 0

        return {
            "price": round(total_price, 2),
            "billable_weight": round(total_billable, 2),
            "desi": round(total_desi, 2),
            "distance_km": distance_km,
        }

    def _is_valid_full_name(value):
        parts = [part for part in value.split() if part]
        if len(parts) < 2:
            return False
        return all(part.replace("-", "").isalpha() for part in parts)

    def _validate_sender_name_inline():
        value = (sender_name.value or "").strip()
        if not value:
            sender_name_error.value = "Gonderici adi bos birakilamaz."
            sender_name_error.visible = True
            return False
        if not _is_valid_full_name(value):
            sender_name_error.value = "Gecerli bir ad soyad girin (sayi kullanmayin)."
            sender_name_error.visible = True
            return False
        sender_name_error.visible = False
        return True

    def _normalize_phone_fields():
        sender_clean = _digits_only(sender_phone.value)[:10]
        receiver_clean = _digits_only(receiver_phone.value)[:10]
        changed = False

        if sender_phone.value != sender_clean:
            sender_phone.value = sender_clean
            changed = True
        if receiver_phone.value != receiver_clean:
            receiver_phone.value = receiver_clean
            changed = True

        sender_phone_error.visible = False

        if changed:
            page.update()

    def _event_value(e):
        data_value = getattr(e, "data", None)
        control_value = getattr(e.control, "value", None)
        return data_value if data_value not in (None, "") else control_value

    def update_pricing():
        if not sender_city.value or not receiver_city.value:
            return

        parcels_data, parcel_errors = _collect_parcels()
        if not parcels_data or parcel_errors:
            price.value = ""
            desi_text.value = "Toplam Desi: 0"
            billable_text.value = "Faturalandirilan Agirlik: 0 kg"
            distance_text.value = "Mesafe: 0 km"
            update_payment_price()
            page.update()
            return

        route = calculate_route(sender_city.value, receiver_city.value)
        calc = _calculate_totals(parcels_data, route, delivery_type.value)
        price.value = str(calc["price"])
        desi_text.value = f"Toplam Desi: {calc['desi']}"
        billable_text.value = f"Faturalandirilan Agirlik: {calc['billable_weight']} kg"
        distance_text.value = f"Mesafe: {calc['distance_km']} km"
        route_preview.value = f"Guzergah: {' -> '.join(route)}"
        route_preview.visible = True
        update_payment_price()
        page.update()

    def update_payment_price(update_page=False):
        if sender_type.value == "gonderici":
            payment_price.value = "0"
        else:
            payment_price.value = price.value or ""

        if update_page:
            page.update()

    def _parcel_field_changed(e):
        field = e.control
        cleaned = _normalize_decimal(field.value)
        if field.value != cleaned:
            field.value = cleaned
        _recalculate_parcels()

    def _recalculate_parcels():
        total_weight = 0
        total_volume = 0
        has_input = False
        has_invalid = False

        for parcel in parcels:
            values = [
                parcel["weight"].value,
                parcel["length"].value,
                parcel["width"].value,
                parcel["height"].value,
            ]
            if any(value for value in values):
                has_input = True
                numbers = [_to_float(value) for value in values]
                if all(num is not None and num > 0 for num in numbers):
                    weight_val, length_val, width_val, height_val = numbers
                    total_weight += weight_val
                    total_volume += length_val * width_val * height_val
                else:
                    has_invalid = True

        weight.value = _format_number(total_weight) if total_weight > 0 else "0"
        volume.value = _format_number(total_volume) if total_volume > 0 else "0"
        parcel_error_text.value = "Koli bilgilerinde eksik veya hatali alan var."
        parcel_error_text.visible = has_input and has_invalid
        update_pricing()

    def _refresh_parcel_labels():
        for index, parcel in enumerate(parcels, start=1):
            parcel["label"].value = f"Koli {index}"
        parcels_column.update()

    def _remove_parcel(parcel):
        if parcel in parcels:
            parcels.remove(parcel)
        if parcel.get("container") in parcels_column.controls:
            parcels_column.controls.remove(parcel["container"])
        if not parcels:
            _add_parcel()
        _refresh_parcel_labels()
        _recalculate_parcels()

    def _add_parcel(e=None):
        label = ft.Text("")
        weight_field = ft.TextField(label="Agirlik (kg)", width=180, on_change=_parcel_field_changed)
        length_field = ft.TextField(label="En (cm)", width=110, on_change=_parcel_field_changed)
        width_field = ft.TextField(label="Boy (cm)", width=110, on_change=_parcel_field_changed)
        height_field = ft.TextField(label="Yukseklik (cm)", width=110, on_change=_parcel_field_changed)
        parcel = {}

        def remove_handler(_):
            _remove_parcel(parcel)

        remove_button = ft.TextButton(content=ft.Text("Sil"), on_click=remove_handler)

        container = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [label, remove_button],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    weight_field,
                    ft.Row(
                        [length_field, width_field, height_field],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10,
                    ),
                ],
                spacing=6,
            ),
            padding=8,
        )

        parcel.update(
            {
                "label": label,
                "weight": weight_field,
                "length": length_field,
                "width": width_field,
                "height": height_field,
                "container": container,
            }
        )

        parcels.append(parcel)
        parcels_column.controls.append(container)
        _refresh_parcel_labels()
        _recalculate_parcels()

    def _collect_parcels():
        items = []
        invalid_indexes = []
        for index, parcel in enumerate(parcels, start=1):
            values = [
                parcel["weight"].value,
                parcel["length"].value,
                parcel["width"].value,
                parcel["height"].value,
            ]
            if not any(values):
                continue
            numbers = [_to_float(value) for value in values]
            if not all(num is not None and num > 0 for num in numbers):
                invalid_indexes.append(index)
                continue
            weight_val, length_val, width_val, height_val = numbers
            volume_cm3 = length_val * width_val * height_val
            items.append(
                {
                    "weight_kg": round(weight_val, 2),
                    "length_cm": round(length_val, 2),
                    "width_cm": round(width_val, 2),
                    "height_cm": round(height_val, 2),
                    "volume_cm3": round(volume_cm3, 2),
                    "desi": round(volume_cm3 / 3000, 2),
                }
            )
        return items, invalid_indexes

    add_parcel_button = ft.ElevatedButton(content=ft.Text("Koli Ekle"), on_click=_add_parcel)

    def apply_city_selection():
        city = sender_city.value
        if not city:
            location_status.value = "Lutfen sehir secin."
            location_status.visible = True
            page.update()
            return

        counties = get_counties_by_city(city) or []
        sender_county.options = [ft.dropdown.Option(c, c) for c in counties]
        sender_county.value = None
        sender_neighborhood.options = []
        sender_neighborhood.value = None
        sender_county.disabled = False
        confirm_county_button.disabled = False
        sender_neighborhood.disabled = True

        location_status.value = f"Sehir: {city} | Ilce: {len(counties)} | Mahalle: 0"
        location_status.visible = True
        sender_county.update()
        sender_neighborhood.update()
        confirm_county_button.update()
        page.update()

    def apply_county_selection():
        city = sender_city.value
        county = sender_county.value
        if not city:
            location_status.value = "Once sehir secin ve onaylayin."
            location_status.visible = True
            page.update()
            return
        if not county:
            location_status.value = "Lutfen ilce secin."
            location_status.visible = True
            page.update()
            return

        neighborhoods = get_neighborhoods_by_county(city, county) or []
        sender_neighborhood.options = [ft.dropdown.Option(n, n) for n in neighborhoods]
        sender_neighborhood.value = None
        sender_neighborhood.disabled = False

        location_status.value = (
            f"Sehir: {city} | Ilce: {len(sender_county.options)} | Mahalle: {len(neighborhoods)}"
        )
        location_status.visible = True
        sender_neighborhood.update()
        page.update()

    def apply_receiver_city_selection():
        city = receiver_city.value
        if not city:
            receiver_location_status.value = "Lutfen sehir secin."
            receiver_location_status.visible = True
            page.update()
            return

        counties = get_counties_by_city(city) or []
        receiver_county.options = [ft.dropdown.Option(c, c) for c in counties]
        receiver_county.value = None
        receiver_neighborhood.options = []
        receiver_neighborhood.value = None
        receiver_county.disabled = False
        confirm_receiver_county_button.disabled = False
        receiver_neighborhood.disabled = True

        receiver_location_status.value = f"Sehir: {city} | Ilce: {len(counties)} | Mahalle: 0"
        receiver_location_status.visible = True
        receiver_county.update()
        receiver_neighborhood.update()
        confirm_receiver_county_button.update()
        page.update()

    def apply_receiver_county_selection():
        city = receiver_city.value
        county = receiver_county.value
        if not city:
            receiver_location_status.value = "Once sehir secin ve onaylayin."
            receiver_location_status.visible = True
            page.update()
            return
        if not county:
            receiver_location_status.value = "Lutfen ilce secin."
            receiver_location_status.visible = True
            page.update()
            return

        neighborhoods = get_neighborhoods_by_county(city, county) or []
        receiver_neighborhood.options = [ft.dropdown.Option(n, n) for n in neighborhoods]
        receiver_neighborhood.value = None
        receiver_neighborhood.disabled = False

        receiver_location_status.value = (
            f"Sehir: {city} | Ilce: {len(receiver_county.options)} | Mahalle: {len(neighborhoods)}"
        )
        receiver_location_status.visible = True
        receiver_neighborhood.update()
        page.update()

    def rebuild_form():
        page.clean()
        page.scroll = ft.ScrollMode.AUTO
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
                    location_row,
                    location_status,
                    sender_address,
                    ft.Container(height=20),
                    ft.Text("ALICI BILGILERI", size=16, weight=ft.FontWeight.BOLD, color="gray"),
                    receiver_name,
                    receiver_phone,
                    ft.Text("Sadece rakam girin (10 hane).", size=11, color="gray"),
                    receiver_location_row,
                    receiver_location_status,
                    receiver_address,
                    route_preview,
                    ft.Text(
                        "Guzergah, sehir baglantilarina gore en az aktarma ile hesaplanir.",
                        size=11,
                        color="gray",
                    ),
                    ft.Container(height=20),
                    ft.Text("KARGO BILGILERI", size=16, weight=ft.FontWeight.BOLD, color="gray"),
                    courier_code,
                    real_tracking_number,
                    ft.Text("Ship24 icin gercek takip no ve courier code girin (opsiyonel).", size=11, color="gray"),
                    sender_type,
                    ft.Text("KOLI BILGILERI", size=14, weight=ft.FontWeight.BOLD, color="gray"),
                    ft.Text("Her koli icin agirlik ve olculeri girin (desi = en x boy x yukseklik / 3000).", size=11, color="gray"),
                    parcels_column,
                    add_parcel_button,
                    parcel_error_text,
                    weight,
                    volume,
                    desi_text,
                    billable_text,
                    distance_text,
                    price,
                    payment_price,
                    delivery_type,
                    shipment_note,
                    ft.Container(height=20),
                    result_text,
                    ft.Container(height=10),
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                content=ft.Text("Kaydet", size=16),
                                width=200,
                                height=45,
                                bgcolor="#2196F3",
                                color="white",
                                on_click=save_cargo,
                            ),
                            ft.ElevatedButton(content=ft.Text("Geri"), on_click=lambda e: home_view(page, user)),
                        ],
                        spacing=10,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Container(height=50),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            )
        )
        page.update()

    def initialize_location_state():
        if not cities:
            return
        sender_city.value = cities[0]
        location_status.value = "Sehir secin ve 'Sehri Onayla' butonuna basin."
        location_status.visible = True
        receiver_location_status.value = "Sehir secin ve 'Sehri Onayla' butonuna basin."
        receiver_location_status.visible = True
        page.update()

    def sender_city_changed(e):
        selected_city = _event_value(e)
        if selected_city:
            sender_city.value = selected_city

    def sender_county_changed(e):
        selected_county = _event_value(e)
        if selected_county:
            sender_county.value = selected_county

    def receiver_city_changed(e):
        selected_city = _event_value(e)
        if selected_city:
            receiver_city.value = selected_city
            update_pricing()

    def receiver_county_changed(e):
        selected_county = _event_value(e)
        if selected_county:
            receiver_county.value = selected_county

    def save_cargo(e):
        _normalize_phone_fields()
        sender_name_ok = _validate_sender_name_inline()

        sender_name_val = (sender_name.value or "").strip()
        receiver_name_val = (receiver_name.value or "").strip()
        sender_phone_val = _digits_only(sender_phone.value)
        receiver_phone_val = _digits_only(receiver_phone.value)
        sender_address_val = (sender_address.value or "").strip()
        receiver_address_val = (receiver_address.value or "").strip()
        courier_val = (courier_code.value or "").strip()
        real_tracking_val = (real_tracking_number.value or "").strip()

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

        if not sender_county.value or not sender_neighborhood.value:
            result_text.value = "Gonderici icin ilce ve mahalle secimi zorunludur."
            result_text.color = "red"
            result_text.visible = True
            page.update()
            return

        if not receiver_county.value or not receiver_neighborhood.value:
            result_text.value = "Alici icin ilce ve mahalle secimi zorunludur."
            result_text.color = "red"
            result_text.visible = True
            page.update()
            return

        if delivery_type.value == "Adrese Teslim" and (
            not sender_address_val or not receiver_address_val
        ):
            result_text.value = "Adrese teslim secildiginde gonderici ve alici adresi zorunludur."
            result_text.color = "red"
            result_text.visible = True
            page.update()
            return

        parcels_data, parcel_errors = _collect_parcels()
        if not parcels_data:
            result_text.value = "En az bir koli girin."
            result_text.color = "red"
            result_text.visible = True
            page.update()
            return

        if parcel_errors:
            errors = ", ".join(str(index) for index in parcel_errors)
            result_text.value = f"Koli {errors} bilgilerinde eksik veya hatali alan var."
            result_text.color = "red"
            result_text.visible = True
            page.update()
            return

        try:
            weight_value = sum(item["weight_kg"] for item in parcels_data)
            volume_value = sum(item["volume_cm3"] for item in parcels_data)
            weight.value = _format_number(weight_value)
            volume.value = _format_number(volume_value)
            update_pricing()
        except ValueError:
            result_text.value = "Sayisal alanlari duzgun girin!"
            result_text.color = "red"
            result_text.visible = True
            page.update()
            return

        if weight_value <= 0 or volume_value <= 0:
            result_text.value = "Toplam agirlik ve hacim sifirdan buyuk olmali."
            result_text.color = "red"
            result_text.visible = True
            page.update()
            return

        route = calculate_route(sender_city.value, receiver_city.value)
        route_str = format_route(route)
        calc = _calculate_totals(parcels_data, route, delivery_type.value)
        price_value = calc["price"]
        price.value = str(price_value)

        try:
            payment_value = float(payment_price.value) if payment_price.value else price_value
        except ValueError:
            result_text.value = "Tahsil edilecek tutar sayisal olmali."
            result_text.color = "red"
            result_text.visible = True
            page.update()
            return

        parcels_json = json.dumps(parcels_data, ensure_ascii=True)

        try:
            tracking = add_shipment(
                sender_name_val,
                sender_phone_val,
                sender_address_val,
                sender_city.value,
                receiver_name_val,
                receiver_phone_val,
                receiver_address_val,
                receiver_city.value,
                receiver_county.value or "",
                receiver_neighborhood.value or "",
                weight_value,
                volume_value,
                price_value,
                payment_value,
                route_str,
                delivery_type.value,
                shipment_note.value or "",
                calc["distance_km"],
                calc["desi"],
                sender_type.value,
                sender_county.value or "",
                sender_neighborhood.value or "",
                courier_val,
                real_tracking_val,
                parcels_json=parcels_json,
            )
        except Exception as exc:
            logger.exception("Shipment create failed: sender=%s receiver=%s", sender_name_val, receiver_name_val)
            result_text.value = f"Kargo kaydi yapilamadi: {exc}"
            result_text.color = "red"
            result_text.visible = True
            page.update()
            return

        party_label = "Gonderici" if sender_type.value == "gonderici" else "Alici"
        real_tracking_line = f"Gercek Takip No: {real_tracking_val}\n" if real_tracking_val else ""
        user_label = user.get("username") if isinstance(user, dict) else "-"
        logger.info(
            "Shipment created: tracking=%s real_tracking=%s courier=%s sender=%s receiver=%s user=%s",
            tracking,
            real_tracking_val or "-",
            courier_val or "-",
            sender_name_val,
            receiver_name_val,
            user_label,
        )
        result_text.value = (
            f"Kargo kaydedildi!\nTakip No: {tracking}\n{real_tracking_line}Kayit Tipi: {party_label}\n"
            f"Koli Sayisi: {len(parcels_data)}\nGuzergah: {' -> '.join(route)}\n"
            f"Mesafe: {calc['distance_km']} km | Desi: {calc['desi']}"
        )
        result_text.color = "green"
        result_text.visible = True
        page.update()

    sender_phone.on_change = lambda e: _normalize_phone_fields()
    receiver_phone.on_change = lambda e: _normalize_phone_fields()
    sender_name.on_change = lambda e: _validate_sender_name_inline()
    sender_city.on_change = sender_city_changed
    sender_county.on_change = sender_county_changed
    confirm_city_button.on_click = lambda e: apply_city_selection()
    confirm_county_button.on_click = lambda e: apply_county_selection()
    receiver_city.on_change = receiver_city_changed
    receiver_county.on_change = receiver_county_changed
    confirm_receiver_city_button.on_click = lambda e: apply_receiver_city_selection()
    confirm_receiver_county_button.on_click = lambda e: apply_receiver_county_selection()
    delivery_type.on_change = lambda e: update_pricing()
    sender_type.on_change = lambda e: update_payment_price(update_page=True)

    rebuild_form()
    initialize_location_state()
    _add_parcel()
    update_payment_price(update_page=True)
