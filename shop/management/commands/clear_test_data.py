from django.core.management.base import BaseCommand
from accounts.models import User
from shop.models import Shop, Product, Order, OrderItem, DropshipImport


class Command(BaseCommand):
    help = 'Clear all test data from the database (users, shops, products, orders)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm that you want to delete all data',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This command will delete ALL data from the database!\n'
                    'Run with --confirm flag to proceed:\n'
                    'python manage.py clear_test_data --confirm'
                )
            )
            return

        self.stdout.write('🗑️  Starting database cleanup...')

        # Get initial counts
        initial_counts = {
            'users': User.objects.count(),
            'shops': Shop.objects.count(),
            'products': Product.objects.count(),
            'orders': Order.objects.count(),
            'order_items': OrderItem.objects.count(),
            'dropship_imports': DropshipImport.objects.count(),
        }

        self.stdout.write(f"📊 Initial counts:")
        for model, count in initial_counts.items():
            self.stdout.write(f"   {model}: {count}")

        # Clear data in correct order (respecting foreign key constraints)
        try:
            # 1. Clear order items first
            deleted_items = OrderItem.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(f'✅ Deleted {deleted_items[0]} order items')
            )

            # 2. Clear orders
            deleted_orders = Order.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(f'✅ Deleted {deleted_orders[0]} orders')
            )

            # 3. Clear dropship imports
            deleted_imports = DropshipImport.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(f'✅ Deleted {deleted_imports[0]} dropship imports')
            )

            # 4. Clear products
            deleted_products = Product.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(f'✅ Deleted {deleted_products[0]} products')
            )

            # 5. Clear shops
            deleted_shops = Shop.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(f'✅ Deleted {deleted_shops[0]} shops')
            )

            # 6. Clear users (this should be last)
            deleted_users = User.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(f'✅ Deleted {deleted_users[0]} users')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error during cleanup: {str(e)}')
            )
            return

        # Verify cleanup
        final_counts = {
            'users': User.objects.count(),
            'shops': Shop.objects.count(),
            'products': Product.objects.count(),
            'orders': Order.objects.count(),
            'order_items': OrderItem.objects.count(),
            'dropship_imports': DropshipImport.objects.count(),
        }

        self.stdout.write('\n🎉 Database cleanup completed successfully!')
        self.stdout.write('📊 Final counts:')
        for model, count in final_counts.items():
            self.stdout.write(f'   {model}: {count}')

        # Verify all counts are zero
        if all(count == 0 for count in final_counts.values()):
            self.stdout.write(
                self.style.SUCCESS('\n✅ Database is now completely clean!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('\n⚠️  Some data may still remain in the database.')
            )