import flet as ft
from views.login_view import login_view
from views.home_view import home_view
from views.add_shipment_view import add_shipment_view
from views.shipment_detail_view import shipment_detail_view
from views.register_view import register_view
from views.tracking_view import tracking_view


def main(page: ft.Page):
    page.title = "Kargo Takip Sistemi"
    
    def route_change(e):
        route = page.route
        user = getattr(page, 'current_user', None)
        protected_routes = {"/home", "/add-shipment", "/shipment"}
        
        if route == "/" or route == "/login" or route is None:
            login_view(page)
        elif route in protected_routes and not user:
            page.go("/login")
        elif route == "/home":
            home_view(page, user)
        elif route == "/add-shipment":
            add_shipment_view(page, user)
        elif route == "/shipment":
            query = page.query
            tracking = query.get("tracking") if query else None
            if tracking:
                shipment_detail_view(page, tracking, user)
            else:
                home_view(page, user)
        elif route == "/register":
            register_view(page)
        elif route == "/track":
            tracking_view(page)
        else:
            login_view(page)
    
    page.on_route_change = route_change
    login_view(page)


if __name__ == "__main__":
    ft.app(target=main)
