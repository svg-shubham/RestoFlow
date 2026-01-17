from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
  class Role(models.TextChoices):
    ADMIN = "ADMIN","Admin"
    MANAGER = "MANAGER","Manager"
    CHEF = "CHEF","Chef"
    CASHIER = "CASHIER","Cashier"
  base_role = Role.ADMIN
  role = models.CharField(max_length=10,choices=Role.choices)

  @property
  def is_manager(self):
    return self.role == self.Role.MANAGER
  
  @property
  def is_chef(self):
    return self.role == self.Role.CHEF
  
  @property
  def is_cashier(self):
    return self.role == self.Role.CASHIER