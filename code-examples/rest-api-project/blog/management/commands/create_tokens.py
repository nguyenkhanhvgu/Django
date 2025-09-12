"""
Management command to create authentication tokens for all users.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class Command(BaseCommand):
    help = 'Create authentication tokens for all users'

    def handle(self, *args, **options):
        users_count = 0
        tokens_created = 0
        
        for user in User.objects.all():
            token, created = Token.objects.get_or_create(user=user)
            users_count += 1
            if created:
                tokens_created += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created token for user: {user.username}')
                )
            else:
                self.stdout.write(f'Token already exists for user: {user.username}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nProcessed {users_count} users. Created {tokens_created} new tokens.'
            )
        )