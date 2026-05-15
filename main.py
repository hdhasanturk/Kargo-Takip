import logging
import sys
from pathlib import Path

import flet as ft
from views.login_view import login_view
from views.home_view import home_view
from views.add_shipment_view import add_shipment_view
from views.shipment_detail_view import shipment_detail_view
from views.register_view import register_view
from views.tracking_view import tracking_view
from views.users_view import users_view
from views.detail_view import detail_view

LOG_DIR = Path(__file__).resolve().parent / "logs"
APP_LOG_PATH = LOG_DIR / "app.log"


def setup_logging():
    LOG_DIR.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[logging.FileHandler(APP_LOG_PATH, encoding="utf-8")],
    )


def _log_uncaught(exc_type, exc, tb):
    logging.getLogger("app").exception("Unhandled exception", exc_info=(exc_type, exc, tb))


_current_user = None


def _get_user(page):
    global _current_user
    if _current_user:
        return _current_user
    _current_user = page.session.get("user")
    return _current_user


def _set_user(page, user):
    global _current_user
    _current_user = user
    page.session.set("user", user)


def _clear_user(page):
    global _current_user
    _current_user = None
    page.session.set("user", None)


def main(page: ft.Page):
    page.title = "Kargo Takip Sistemi"
    logger = logging.getLogger("app")

    public_routes = {"/", "/login", "/register", "/track"}

    def route_change(e):
        try:
            route = page.route
            user = _get_user(page)
            logger.info("Route change: %s", route)

            if route == "/" or route == "/login" or route is None:
                login_view(page, _set_user, _clear_user)
            elif route == "/register":
                register_view(page)
            elif route == "/track":
                tracking_view(page)
            elif not user:
                page.go("/login")
            elif route == "/home":
                home_view(page, user, _clear_user)
            elif route == "/add-shipment":
                add_shipment_view(page, user)
            elif route.startswith("/shipment/"):
                tracking = route.split("/shipment/")[-1]
                if tracking:
                    shipment_detail_view(page, tracking, user)
                else:
                    home_view(page, user, _clear_user)
            elif route == "/users":
                users_view(page, user)
            elif route == "/detail":
                query = page.query
                shipment_id = None
                if query:
                    shipment_id = query.get("id") or query.get("shipment_id")
                try:
                    shipment_id = int(shipment_id) if shipment_id is not None else None
                except (TypeError, ValueError):
                    shipment_id = None
                if shipment_id:
                    detail_view(page, shipment_id)
                else:
                    home_view(page, user, _clear_user)
            else:
                page.go("/login")
        except Exception:
            logger.exception("Route handling failed")
            page.go("/login")

    page.on_route_change = route_change
    login_view(page, _set_user, _clear_user)


if __name__ == "__main__":
    setup_logging()
    sys.excepthook = _log_uncaught
    logging.getLogger("app").info("App starting")
    ft.app(target=main)
