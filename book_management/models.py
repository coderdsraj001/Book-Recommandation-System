from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import CustomUserManager  


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    objects = CustomUserManager() 
    
    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)


class Book(models.Model):
    title = models.CharField(max_length=255)
    authors = models.CharField(max_length=255) 
    genre = models.CharField(max_length=100)
    publication_date = models.DateField()
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

class ReadingList(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="reading_lists")
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} by {self.user.username}"


class ReadingListItem(models.Model):
    reading_list = models.ForeignKey(ReadingList, on_delete=models.CASCADE, related_name="items")
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order'] 

    def __str__(self):
        return f"{self.book.title} in {self.reading_list.name}"