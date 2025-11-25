from django.apps import AppConfig


class GestionAdministrativaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gestion_administrativa'


from django.apps import AppConfig

class GestionAdministrativaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gestion_administrativa'

    def ready(self):
        import gestion_administrativa.signals       # Asegúrate de que la ruta es correcta
