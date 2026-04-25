from decimal import Decimal

from django.db import migrations, models
import django.core.validators


def set_virtual_cards_to_zero(apps, schema_editor):
    VirtualCard = apps.get_model("finance", "VirtualCard")
    VirtualCard.objects.update(starting_balance=Decimal("0.00"))


class Migration(migrations.Migration):

    dependencies = [
        ("finance", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="virtualcard",
            name="starting_balance",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0.00"),
                max_digits=12,
                validators=[django.core.validators.MinValueValidator(Decimal("0.00"))],
            ),
        ),
        migrations.RunPython(set_virtual_cards_to_zero, migrations.RunPython.noop),
    ]
