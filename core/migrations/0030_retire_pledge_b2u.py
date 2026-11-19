# Retire Pledge (REWARDS) and Buy-to-unglue campaign types for NEW campaigns
# (Gluejar/regluit#1195). The default campaign type becomes THANKS; the legacy
# choices are retained so existing REWARDS/BUY2UNGLUE campaigns keep validating
# and displaying. No database schema change results (default and choices are
# Django-level), so this migration only updates migration state.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_auto_20241122_1525'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='type',
            field=models.PositiveSmallIntegerField(
                choices=[
                    (1, 'Pledge-to-unglue campaign'),
                    (2, 'Buy-to-unglue campaign'),
                    (3, 'Thanks-for-ungluing campaign'),
                ],
                default=3,
            ),
        ),
    ]
