""" from django.test import TestCase

# Create your tests here. """

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView, ListView, View, FormView
from django.views.generic.edit import FormView
from django.db.models import Subquery, OuterRef, Sum, F, Q, Value,  Count, Min,Max, ExpressionWrapper, DecimalField, Case, When, FloatField
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator, EmptyPage,PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from .models import Tempe, Inventario



registros = Tempe.objects.all()
for reg in registros:
    encontrar = Inventario.objects.filter(nombre = reg.producto).first()
    if encontrar:
        Tempe.objects.filter(id=reg.id).update(
            inventario = encontrar.id
        )


print("FIN")
