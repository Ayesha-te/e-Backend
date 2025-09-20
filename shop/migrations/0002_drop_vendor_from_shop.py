from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("shop", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE shop_shop DROP COLUMN IF EXISTS vendor_id;",
            reverse_sql=(
                # Reverse just re-creates a nullable vendor_id without FK to avoid failing on reverse
                # (the previous state was out-of-sync with code anyway)
                "ALTER TABLE shop_shop ADD COLUMN IF NOT EXISTS vendor_id integer NULL;"
            ),
        ),
    ]