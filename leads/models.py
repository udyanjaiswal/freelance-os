from django.db import models

class Lead(models.Model):

    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('interested', 'Interested'),
        ('follow_up', 'Follow Up'),
        ('not_interested', 'Not Interested'),
        ('converted', 'Converted'),
        ('lost', 'Lost'),
    ]

    POTENTIAL_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]

    # Business
    business_name = models.CharField(max_length=200)
    category = models.CharField(max_length=150, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)

    # Contact
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)

    # Discovery
    source = models.CharField(max_length=100, blank=True)
    source_id = models.CharField(max_length=200, blank=True)

    # Qualification
    score = models.IntegerField(default=0)
    potential = models.CharField(
        max_length=20,
        choices=POTENTIAL_CHOICES,
        default='low'
    )

    # Sales
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='new'
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.business_name