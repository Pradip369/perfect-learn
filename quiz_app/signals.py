from django.dispatch.dispatcher import receiver
from django.db.models.signals import pre_save
from .models import Category,FileUpload

@receiver(pre_save, sender=Category)
def pre_save_image(sender, instance, *args, **kwargs):
    try:
        old_img = instance.__class__.objects.get(id=instance.id).category_img.path
        try:
            new_img = instance.category_img.path
        except:
            new_img = None
        if new_img != old_img:
            import os
            if os.path.exists(old_img):
                os.remove(old_img)
    except:
        pass

@receiver(pre_save, sender=FileUpload)
def pre_save_file(sender, instance, *args, **kwargs):
    try:
        old_file = instance.__class__.objects.get(id=instance.id).source_file.path
        try:
            new_file = instance.source_file.path
        except:
            new_file = None
        if new_file != old_file:
            import os
            if os.path.exists(old_file):
                os.remove(old_file)
    except:
        pass