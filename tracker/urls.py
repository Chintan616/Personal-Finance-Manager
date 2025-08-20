from django.urls import path
from .views import signup_view, login_view, logout_view, base_view, report_view, basic_user_dashboard, add_expense_view, add_income_view, view_expense_view, view_income_view, edit_income_view, delete_income_view, edit_expense_view, delete_expense_view, set_goal_view, edit_goal_view, delete_goal_view, profile_view, edit_profile_view , chart_view 
urlpatterns = [
    path("", base_view, name="base"),
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("basic_user/", basic_user_dashboard, name='basic_user'),
    path("add_income/", add_income_view, name="add_income"),
    path("add_expense/", add_expense_view, name="add_expense"),
    path("view_income/", view_income_view, name="view_income"),
    path("view_expense/", view_expense_view, name="view_expense"),
    path("edit_income/<int:income_id>/", edit_income_view, name="edit_income"),
    path("delete_income/<int:income_id>/", delete_income_view, name="delete_income"),
    path("edit_expense/<int:expense_id>/", edit_expense_view, name="edit_expense"),
    path("delete_expense/<int:expense_id>/", delete_expense_view, name="delete_expense"),
    path("set_goal/", set_goal_view, name="set_goal"),
    path("edit_goal/<int:goal_id>/", edit_goal_view, name="edit_goal"),
    path("delete_goal/<int:goal_id>/", delete_goal_view, name="delete_goal"),
    path("report/", report_view, name="report"),
    path("profile/", profile_view, name="profile"),
    path("edit_profile/", edit_profile_view, name="edit_profile"),
    path("chart/", chart_view, name="chart")    
]