from django.core.management.base import BaseCommand
from movies.models import SectionItem

class Command(BaseCommand):
    help = 'Clean up orphaned SectionItem records where content_object is None'

    def handle(self, *args, **options):
        # Find all SectionItem records where content_object is None
        orphaned_items = []
        for item in SectionItem.objects.all():
            if item.content_object is None:
                orphaned_items.append(item)
        
        if orphaned_items:
            self.stdout.write(f"Found {len(orphaned_items)} orphaned SectionItem records:")
            for item in orphaned_items:
                self.stdout.write(f"  - SectionItem {item.id}: Section '{item.section.name}', ContentType {item.content_type}, ObjectID {item.object_id}")
            
            # Delete the orphaned items
            for item in orphaned_items:
                item.delete()
            
            self.stdout.write(self.style.SUCCESS(f"Successfully deleted {len(orphaned_items)} orphaned SectionItem records"))
        else:
            self.stdout.write(self.style.SUCCESS("No orphaned SectionItem records found")) 