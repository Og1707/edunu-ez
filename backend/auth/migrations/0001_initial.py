from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('api', '0005_categoriajuego_juegoeducativo_partidajuego'),
    ]

    operations = [
        migrations.CreateModel(
            name='MagicLinkToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('used', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='magic_link_tokens', to='api.usuario')),
            ],
            options={
                'indexes': [models.Index(fields=['token'], name='auth_magi_token_3c2ea4_idx'), models.Index(fields=['created_at'], name='auth_magi_crea_1b8b98_idx')],
            },
        ),
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='invitations', to='api.usuario')),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['created_by'], name='auth_invi_created_by_57f7c3_idx'), models.Index(fields=['created_at'], name='auth_invi_created_at_b72fbe_idx')],
            },
        ),
    ]
