from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Theme(models.Model):
    title = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.title


class Room(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    theme = models.ForeignKey(Theme, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100, default=None)
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    description = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated_at', '-created_at']
        verbose_name = 'Комната'
        verbose_name_plural = 'Комнаты'

    def __str__(self):
        return self.name


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    text = models.TextField(null=False, default='Hi')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'