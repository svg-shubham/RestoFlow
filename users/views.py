from django.shortcuts import render,redirect
from django.contrib.auth.views import LoginView
from django.urls import reverse
from django.shortcuts import resolve_url

# Create your views here.

class CustomLoginView(LoginView):
  template_name = 'users/login.html'


  def get_success_url(self):
      user = self.request.user
      print(f"DEBUG: Login Success for {user.username} with role {user.role}") # Terminal me dekhein
      
      if user.is_manager:
          return resolve_url('/tables/') # Direct path dekar dekho
      elif user.is_chef:
          return resolve_url('/kitchen/')
      elif user.is_cashier:
        return resolve_url('/cashier/dashboard/')
      return resolve_url('/')
    
    