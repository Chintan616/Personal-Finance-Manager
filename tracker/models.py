from django.db import models
from django.contrib.auth.models import User

class IncomeCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to logged-in user
    category = models.ForeignKey('IncomeCategory', on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.amount} ({self.category})"

class ExpenseCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    def __str__(self):
        return self.name

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to logged-in user
    category = models.ForeignKey('ExpenseCategory', on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} ({self.category})"

class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    year = models.IntegerField(default=2025)
    month = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.year}-{self.month:02d}"