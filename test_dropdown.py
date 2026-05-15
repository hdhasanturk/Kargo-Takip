import flet as ft


def main(page: ft.Page):
    page.title = "Dropdown Test"

    dd1 = ft.Dropdown(
        label="Sehir",
        options=[
            ft.dropdown.Option("ADANA"),
            ft.dropdown.Option("ISTANBUL"),
        ],
    )
    dd2 = ft.Dropdown(label="Ilce", options=[])

    def on_city_change(e):
        print(f"on_change fired: e.data={e.data}, dd1.value={dd1.value}")
        selected = e.data if e.data else dd1.value
        if not selected:
            return
        dd1.value = selected
        items = {"ADANA": ["CEYHAN", "FEKE"], "ISTANBUL": ["KADIKOY", "BESIKTAS"]}
        dd2.options = [ft.dropdown.Option(x) for x in items.get(selected, [])]
        dd2.value = None
        dd2.update()
        print(f"dd2 options set: {dd2.options}")

    dd1.on_change = on_city_change

    page.add(dd1, dd2)


if __name__ == "__main__":
    ft.run(main)
