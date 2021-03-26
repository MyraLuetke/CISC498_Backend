from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import ugettext_lazy as _


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """User model."""

    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    is_customer = models.BooleanField(default=False)


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_num = models.CharField(max_length=11)
    created_date = models.DateTimeField(auto_now_add=True)
    email_verification = models.BooleanField(default=False)

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class Business(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=100)
    phone_num = models.CharField(max_length=11)
    address = models.TextField()
    capacity = models.IntegerField()

    def __str__(self):
        return self.name


class UnregisteredVisit(models.Model):
    dateTime = models.DateTimeField(auto_now_add=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_num = models.CharField(max_length=11)
    business = models.ForeignKey(Business, on_delete=models.PROTECT)
    numVisitors = models.IntegerField()

    def __str__(self):
        return self.first_name + ' ' + self.last_name + ' ' + self.phone_num + ' ' + self.business.__str__() + ' ' + self.dateTime.__str__()


class Visit(models.Model):
    dateTime = models.DateTimeField(auto_now_add=False)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    business = models.ForeignKey(Business, on_delete=models.PROTECT)
    numVisitors = models.IntegerField()

    def __str__(self):
        return self.customer.__str__() + ' ' + self.business.__str__() + ' ' + self.dateTime.__str__()
