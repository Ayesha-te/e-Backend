from django.db import migrations


def drop_vendor_column(apps, schema_editor):
    """Drop shop_shop.vendor_id only on PostgreSQL.
    SQLite either won't have this column (fresh schema) or lacks IF EXISTS support in this context.
    """
    vendor = schema_editor.connection.vendor
    if vendor == 'postgresql':
        schema_editor.execute("ALTER TABLE shop_shop DROP COLUMN IF EXISTS vendor_id;")
    else:
        # No-op for sqlite/mysql to avoid syntax/compat issues
        pass


def restore_vendor_column(apps, schema_editor):
    """Reverse: re-add vendor_id only on PostgreSQL as a nullable integer (no FK)."""
    vendor = schema_editor.connection.vendor
    if vendor == 'postgresql':
        schema_editor.execute("ALTER TABLE shop_shop ADD COLUMN IF NOT EXISTS vendor_id integer NULL;")
    else:
        # No-op for sqlite/mysql
        pass


class Migration(migrations.Migration):
    dependencies = [
        ("shop", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(drop_vendor_column, restore_vendor_column),
    ]