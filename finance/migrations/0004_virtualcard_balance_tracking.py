from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import migrations, models


def populate_card_totals(apps, schema_editor):
    VirtualCard = apps.get_model("finance", "VirtualCard")

    for card in VirtualCard.objects.all():
        incomes = card.transactions.filter(type="income").aggregate(total=models.Sum("amount"))["total"] or Decimal("0.00")
        expenses = card.transactions.filter(type="expense").aggregate(total=models.Sum("amount"))["total"] or Decimal("0.00")
        card.total_income = incomes
        card.total_expense = expenses
        card.balance = (card.starting_balance or Decimal("0.00")) + incomes - expenses
        card.save(update_fields=["total_income", "total_expense", "balance"])


class Migration(migrations.Migration):

    dependencies = [
        ("finance", "0003_alter_virtualcard_options_alter_virtualcard_name_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="virtualcard",
            name="balance",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0.00"),
                max_digits=12,
                validators=[MinValueValidator(Decimal("0.00"))],
            ),
        ),
        migrations.AddField(
            model_name="virtualcard",
            name="total_expense",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0.00"),
                max_digits=12,
                validators=[MinValueValidator(Decimal("0.00"))],
            ),
        ),
        migrations.AddField(
            model_name="virtualcard",
            name="total_income",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0.00"),
                max_digits=12,
                validators=[MinValueValidator(Decimal("0.00"))],
            ),
        ),
        migrations.RunPython(populate_card_totals, migrations.RunPython.noop),
    ]
