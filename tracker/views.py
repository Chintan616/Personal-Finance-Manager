import matplotlib
matplotlib.use('Agg')  # Use Agg backend to avoid GUI issues
import matplotlib.pyplot as plt
from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm
from django.contrib.auth.forms import AuthenticationForm
from .models import IncomeCategory , Income , Expense , ExpenseCategory
from django.contrib import messages 
from django.db.models import Sum
from itertools import chain
from operator import attrgetter
from .models import Goal
from datetime import date
import calendar
from .forms import EditProfileForm
import io
import base64
from django.shortcuts import render
from datetime import datetime
from dateutil.relativedelta import relativedelta

def base_view(request): 
    return render(request, "base.html")

def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Signup successful! Welcome to your dashboard!")
            return redirect('basic_user')  # Ensure this URL name is correct
        else:
             # Debugging: Print form errors to console
            messages.error(request, "Signup failed. Please check the form.")
    else:
        form = SignUpForm()

    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == "POST":
        # Check the form data manually if you aren't using AuthenticationForm
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user)
            messages.success(request, "Thank You!")
            messages.success(request, "Login successful! Welcome to your dashboard!")
            return redirect('basic_user')
        else:
            # If authentication fails, create a form with error message
            form = AuthenticationForm(request, data=request.POST)
            # form.add_error(None, 'Invalid username or password')
        messages.success(request, "Invalid username or password")

    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def profile_view(request):
    user = request.user
    total_income = Income.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = Expense.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0
    net_savings = total_income - total_expense

    context = {
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'net_savings': net_savings,
        'joined_date': user.date_joined,
    }

    return render(request, 'profile.html', context)


@login_required
def edit_profile_view(request):
    user = request.user
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = EditProfileForm(instance=user)

    context = {
        'form': form
    }

    return render(request, 'edit_profile.html', context)

@login_required
def basic_user_dashboard(request):
    total_income = Income.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = Expense.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
    remaining_balance = total_income - total_expense

    recent_incomes = Income.objects.filter(user=request.user).order_by('-date')[:5]
    recent_expenses = Expense.objects.filter(user=request.user).order_by('-date')[:5]

    for income in recent_incomes:
        income.type = 'Income'
    for expense in recent_expenses:
        expense.type = 'Expense'

    # Combine and sort recent transactions by date
    recent_transactions = sorted(
        chain(recent_incomes, recent_expenses),
        key=attrgetter('date'),
        reverse=True
    )[:10]

    # Current goal
    current_year = date.today().year
    current_month = date.today().month
    goal = Goal.objects.filter(user=request.user, year=current_year, month=current_month).first()
    goal_amount = goal.amount if goal else 0
    goal_achievement = (remaining_balance / goal_amount * 100) if goal_amount > 0 else 0
    # Last month's goal
    if current_month == 1:
        last_month = 12
        last_month_year = current_year - 1
    else:
        last_month = current_month - 1
        last_month_year = current_year

    last_month_goal = Goal.objects.filter(user=request.user, year=last_month_year, month=last_month).first()
    last_month_goal_amount = last_month_goal.amount if last_month_goal else 0

    context = {
        'total_income': total_income,
        'total_expense': total_expense,
        'remaining_balance': remaining_balance,
        'recent_transactions': recent_transactions,
        'goal_achievement': goal_achievement,
        'last_month_goal_amount': last_month_goal_amount,
    }

    return render(request, 'basic_user.html', context)




@login_required     
def set_goal_view(request):
    if request.method == "POST":
        goal_amount = request.POST.get("goal_amount")
        goal_month = request.POST.get("goal_month")
        year, month = map(int, goal_month.split('-'))
        Goal.objects.create(user=request.user, amount=goal_amount, year=year, month=month)
        messages.success(request, "Goal set successfully!")
        return redirect("set_goal")

    goals = Goal.objects.filter(user=request.user).order_by('-year', '-month')
    for goal in goals:
        goal.month_name = calendar.month_name[goal.month]
    return render(request, "set_goal.html", {'goals': goals})

@login_required
def edit_goal_view(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id)

    if request.method == "POST":
        goal.amount = request.POST.get("goal_amount")
        goal_month = request.POST.get("goal_month")
        goal.year, goal.month = map(int, goal_month.split('-'))
        goal.save()
        messages.success(request, "Goal updated successfully!")
        return redirect("set_goal")

    return render(request, "edit_goal.html", {"goal": goal})

@login_required
def delete_goal_view(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id)
    if request.method == "POST":
        goal.delete()
        messages.success(request, "Goal deleted successfully!")
        return redirect("set_goal")
    return render(request, "set_goal.html")

@login_required
def add_income_view(request):
    if request.method == "POST":
        amount = request.POST.get("amount")
        category_id = request.POST.get("category")
        date = request.POST.get("date")
        description = request.POST.get("description")

        # Get the category instance
        category = IncomeCategory.objects.get(id=category_id)

        # Save to database
        Income.objects.create(user=request.user,amount=amount, category=category, date=date, description=description)

        # Add success message
        messages.success(request, "Income added successfully!")

        return redirect("add_income")  # Redirect to same page to display the message

    categories = IncomeCategory.objects.all()
    return render(request, "add_income.html", {"categories": categories})

@login_required
def add_expense_view(request):
    if request.method == "POST":
        amount = request.POST.get("amount")
        category_id = request.POST.get("category")
        date = request.POST.get("date")
        description = request.POST.get("description")

        # Get the category instance
        category = ExpenseCategory.objects.get(id=category_id)

        # Save to database
        Expense.objects.create(user=request.user,amount=amount, category=category, date=date, description=description)

        # Add success message
        messages.success(request, "Expense added successfully!")

        return redirect("add_expense")  # Redirect to same page to display the message

    categories = ExpenseCategory.objects.all()
    return render(request, "add_expense.html", {"categories": categories})

@login_required
def view_income_view(request):
    incomes = Income.objects.select_related('category').filter(user=request.user).order_by('-date')
    total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or 0  # Sum of all income amounts
    return render(request, 'view_income.html', {'incomes': incomes, 'total_income': total_income})

@login_required
def view_expense_view(request):
    expenses = Expense.objects.select_related('category').filter(user=request.user).order_by('-date')
    total_expense = expenses.aggregate(Sum('amount'))['amount__sum'] or 0  # Sum of all income amounts
    return render(request, 'view_expense.html', {'expenses': expenses, 'total_expense': total_expense})


@login_required
def edit_income_view(request, income_id):
    income = get_object_or_404(Income, id=income_id)
    categories = IncomeCategory.objects.all()

    if request.method == "POST":
        income.amount = request.POST["amount"]
        income.category_id = request.POST["category"]
        income.date = request.POST["date"]
        income.description = request.POST["description"]
        income.save()
        messages.success(request, "Income updated successfully!")
        return redirect("view_income")

    return render(request, "edit_income.html", {"income": income, "categories": categories})

@login_required
def delete_income_view(request, income_id):
    income = get_object_or_404(Income, id=income_id)
    income.delete()
    messages.success(request, "Income deleted successfully!")
    return redirect("view_income")

@login_required
def edit_expense_view(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    categories = ExpenseCategory.objects.all()

    if request.method == "POST":
        expense.amount = request.POST["amount"]
        expense.category_id = request.POST["category"]
        expense.date = request.POST["date"]
        expense.description = request.POST["description"]
        expense.save()
        messages.success(request, "Expense updated successfully!")
        return redirect("view_expense")

    return render(request, "edit_expense.html", {"expense": expense, "categories": categories})


@login_required
def delete_expense_view(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    expense.delete()
    messages.success(request, "Expense deleted successfully!")
    return redirect("view_expense")


@login_required
def report_view(request):
    report_data = []
    error_message = None
    no_transactions_message = None

    if request.method == 'POST':
        try:
            start_date_str = request.POST.get('start_date')
            end_date_str = request.POST.get('end_date')

            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

            if end_date < start_date:
                error_message = "End date cannot be earlier than the start date."
            else:
                # Fetch transactions only if no error
                incomes = Income.objects.filter(user=request.user, date__range=[start_date, end_date])
                expenses = Expense.objects.filter(user=request.user, date__range=[start_date, end_date])

                if not incomes.exists() and not expenses.exists():
                    no_transactions_message = "No transactions found in the selected date range."

                for income in incomes:
                    report_data.append({
                        'type': 'Income',
                        'amount': income.amount,
                        'category': income.category.name,
                        'date': income.date,
                        'description': income.description
                    })

                for expense in expenses:
                    report_data.append({
                        'type': 'Expense',
                        'amount': expense.amount,
                        'category': expense.category.name,
                        'date': expense.date,
                        'description': expense.description
                    })

                # Sort transactions by date
                report_data = sorted(report_data, key=lambda x: x['date'])
        
        except ValueError:
            error_message = "Invalid date format. Please enter valid dates."

    # Return without "No transactions" message if there's an error
    return render(request, 'report.html', {
        'report_data': report_data if not error_message else None,
        'no_transactions_message': no_transactions_message if not error_message else None,
        'error_message': error_message,
    })

@login_required
def chart_view(request):
    # Get the last 5 months accurately
    today = datetime.today()
    last_five_months = [(today - relativedelta(months=i)).strftime('%Y-%m') for i in range(4, -1, -1)]
    month_names = [calendar.month_name[int(month.split('-')[1])] for month in last_five_months]

    # Fetch categories (ensuring uniqueness)
    income_categories = IncomeCategory.objects.order_by('name').distinct()
    expense_categories = ExpenseCategory.objects.order_by('name').distinct()

    # Fetch aggregated income and expense data
    income_data = (
        Income.objects.filter(user=request.user, date__year__gte=today.year - 1)
        .values('category_id', 'date__year', 'date__month')
        .annotate(total=Sum('amount'))
    )

    expense_data = (
        Expense.objects.filter(user=request.user, date__year__gte=today.year - 1)
        .values('category_id', 'date__year', 'date__month')
        .annotate(total=Sum('amount'))
    )

    # Convert to lookup dictionaries
    def process_data(data):
        return {
            (entry['category_id'], entry['date__year'], entry['date__month']): entry['total']
            for entry in data
        }

    income_dict = process_data(income_data)
    expense_dict = process_data(expense_data)

    # Chart generator with consistent dark theme styling
    def generate_chart(data, category_name, color, title_prefix, bg_color="#212631"):
        if all(value == 0 for value in data):
            return None  # Skip empty charts

        fig, ax = plt.subplots(figsize=(8, 5))
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)
        ax.plot(month_names, data, color=color, alpha=0.7)

        ax.set_title(f'{title_prefix} in {category_name} Category (Last 5 Months)', color="white", fontsize=19)
        ax.set_xlabel('Month', color="white")
        ax.set_ylabel('Amount', color="white")
        ax.tick_params(axis='x', colors="white")
        ax.tick_params(axis='y', colors="white")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', facecolor=fig.get_facecolor())
        buf.seek(0)
        chart_image = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        plt.close(fig)
        return chart_image

    # Generate unique income charts
    income_charts = []
    seen_income = set()
    for category in income_categories:
        if category.id in seen_income:
            continue
        seen_income.add(category.id)

        totals = [
            income_dict.get((category.id, int(m.split('-')[0]), int(m.split('-')[1])), 0)
            for m in last_five_months
        ]
        chart_image = generate_chart(totals, category.name, 'blue', 'Income')
        if chart_image:
            income_charts.append({'category': category.name, 'chart_image': chart_image})

    # Generate unique expense charts
    expense_charts = []
    seen_expense = set()
    for category in expense_categories:
        if category.id in seen_expense:
            continue
        seen_expense.add(category.id)

        totals = [
            expense_dict.get((category.id, int(m.split('-')[0]), int(m.split('-')[1])), 0)
            for m in last_five_months
        ]
        chart_image = generate_chart(totals, category.name, 'red', 'Expense')
        if chart_image:
            expense_charts.append({'category': category.name, 'chart_image': chart_image})

    return render(request, 'chart.html', {
        'income_charts': income_charts,
        'expense_charts': expense_charts,
    })