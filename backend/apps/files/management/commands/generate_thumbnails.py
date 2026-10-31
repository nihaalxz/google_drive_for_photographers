from django.core.management.base import BaseCommand
from django.db.models import Q
from apps.files.models import FileAsset
from apps.storage.services.b2 import b2_service
from apps.files.utils import generate_compressed_thumbnail

class Command(BaseCommand):
    help = 'Generate compressed WebP thumbnails for all uploaded images missing a thumbnail_key.'

    def handle(self, *args, **options):
        images_missing_thumbs = FileAsset.objects.filter(
            Q(thumbnail_key__isnull=True) | Q(thumbnail_key=''),
            upload_status='UPLOADED',
            mime_type__startswith='image/'
        )
        total = images_missing_thumbs.count()
        self.stdout.write(f"Found {total} images needing compressed thumbnails.")

        success_count = 0
        for asset in images_missing_thumbs:
            try:
                self.stdout.write(f"Generating thumbnail for: {asset.safe_display_name} ({asset.id})...")
                raw_bytes = b2_service.get_object_bytes(asset.object_key)
                if not raw_bytes:
                    self.stdout.write(self.style.WARNING(f"  Empty or missing object bytes for {asset.object_key}"))
                    continue

                thumb_bytes = generate_compressed_thumbnail(raw_bytes)
                if not thumb_bytes:
                    self.stdout.write(self.style.WARNING(f"  Pillow failed to process {asset.safe_display_name}"))
                    continue

                thumb_key = f"thumbnails/{asset.workspace.id}/{asset.id}.webp"
                b2_service.upload_bytes(thumb_key, thumb_bytes, content_type='image/webp')
                asset.thumbnail_key = thumb_key
                asset.save(update_fields=['thumbnail_key'])
                success_count += 1
                self.stdout.write(self.style.SUCCESS(f"  Generated {len(thumb_bytes)} bytes WebP thumbnail -> {thumb_key}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  Error for {asset.id}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"Finished! Successfully generated {success_count}/{total} thumbnails."))
