from django.dispatch import Signal, receiver


ncdfile_downloaded_signal = Signal()
@receiver(ncdfile_downloaded_signal)
def ncdfile_downloaded_signal_handler(sender, instance, **kwargs):
    print("NCD file was downloaded!")
    instance.status = 'ncdfile_downloaded'
    instance.save()
    dataproduct_script = str(instance.dataproduct.script)
    func = getattr(instance, dataproduct_script)
    func()
    
    
