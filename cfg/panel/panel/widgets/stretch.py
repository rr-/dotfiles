from panel.widgets.widget import Widget


class StretchWidget(Widget):
    delay = 1000

    def __init__(self, app, main_window):
        super().__init__(app, main_window)
        main_window[0].layout().addStretch()

    def refresh_impl(self):
        pass

    def render_impl(self):
        pass
