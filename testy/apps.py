from django.apps import AppConfig


class TestyAppConfig(AppConfig):
    name = "testy"

    def ready(self):
        import testy.signals
