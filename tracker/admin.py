from django.contrib import admin
from .models import IncomeCategory , Income , Expense , ExpenseCategory , Goal

admin.site.register(IncomeCategory)
admin.site.register(Income)
admin.site.register(ExpenseCategory)
admin.site.register(Expense)
admin.site.register(Goal)