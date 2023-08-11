from django.apps import AppConfig


class GaiaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gaia'
    #def ready(self):
     #    from . import update_collections
     #    update_collections.fetch_and_store_collections()
     #    print("App ready hook executed.")