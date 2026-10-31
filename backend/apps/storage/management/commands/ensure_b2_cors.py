from django.core.management.base import BaseCommand
from apps.storage.services.b2 import b2_service

class Command(BaseCommand):
    help = 'Apply CORS rules to Backblaze B2 bucket so web browsers can stream and upload without 403 errors.'

    def handle(self, *args, **options):
        self.stdout.write(f"Configuring CORS on B2 bucket: {b2_service.bucket_name}...")
        success = b2_service.ensure_bucket_cors()
        if success:
            self.stdout.write(self.style.SUCCESS(f"Successfully applied S3 CORS rules to {b2_service.bucket_name}!"))
        else:
            self.stdout.write(self.style.WARNING("CORS could not be applied automatically. Please verify credentials or set CORS in Backblaze B2 console."))
