from django.db import migrations

def fix_invalid_authors(apps, schema_editor):
    BlogPost = apps.get_model('blog', 'BlogPost')
    User = apps.get_model('auth', 'User')
    
    # Get the first user as default (or create one if none exists)
    default_user = User.objects.first()
    if not default_user:
        default_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpassword'
        )
    
    # Update the problematic post using the correct field name
    BlogPost.objects.filter(pk=8).update(author=default_user)

def reverse_fix(apps, schema_editor):
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('blog', '0011_remove_blogpost_profile'),  # Make sure this matches your last migration
    ]

    operations = [
        migrations.RunPython(fix_invalid_authors, reverse_fix),
    ]