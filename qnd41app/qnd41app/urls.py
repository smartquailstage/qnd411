"""
URL configuration for qnd41app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path,re_path,include
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from baton.autodiscover import admin
from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail import urls as wagtaildocs_urls
from django.contrib.auth import views as auth_views
from businessmodel.views import  ventas_grafico

#from editorial_literaria.views import CourseListView
#from usuarios.views import user_login


urlpatterns = i18n_patterns(

    path('analytics/', admin.site.urls),
    path('baton/', include('baton.urls')),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('rosetta/', include('rosetta.urls')),
    path('ventas/grafico/', ventas_grafico, name='ventas_grafico'),
  #  path('ventas/', mostrar_ventas, name='mostrar_ventas'),
    path('businessmodel/', include('businessmodel.urls', namespace='businessmodel')),
    
   # path('sblshop/', include('sblshop.urls', namespace='sblshop')),
   # path('sblcart/', include('sblcart.urls', namespace='sblcart')),
   # path('Sblorders/', include('sblorders.urls', namespace='sblorders')),
  
    #path('orders/', include('orders.urls', namespace='orders')),
    #path('payment/', include('payment.urls', namespace='payment')),
 #   path('shop/', include('shop.urls', namespace='shop')),
 #   path('cart/', include('cart.urls', namespace='cart')),
   

  #  path('sbashop/', include('sbashop.urls', namespace='sbashop')),
  #  path('sbacart/', include('sbacart.urls', namespace='sbacart')),
  #  path('sbaorders/', include('sbaorders.urls', namespace='sbaorders')),

  #  path('sbtshop/', include('sbtshop.urls', namespace='sbtshop')),
  #  path('sbtcart/', include('sbtcart.urls', namespace='sbtcart')),
  #  path('Sbtorders/', include('sbtorders.urls', namespace='sbtorders')),

  #  path('sbmshop/', include('sbmshop.urls', namespace='sbmshop')),
  #  path('sbmcart/', include('sbmcart.urls', namespace='sbmcart')),
  #  path('Sbmorders/', include('sbmorders.urls', namespace='sbmorders')),
   # path('QuitoCultura/', include('usuarios.urls', namespace='usuarios')),
  #  path('editorial_literaria/', include('editorial_literaria.urls')),
  #  path('proponer_actividades_espacio_publico/', include('actividades_espacio_publico.urls', namespace='actividades')),
  #  path('proyectos/', include('proyectos.urls')),
  #  path('convocatorias_disponibles/', CourseListView.as_view(), name='course_list'),
  #  path('postularse/', include('students.urls')),
   # path('login/', auth_views.LoginView.as_view(), name='login'),
  #  path('logout/', auth_views.LogoutView.as_view(), name='logout'),
  #  path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
  #  path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    # reset password urls
  #  path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
  #  path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
  #  path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
 #   path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    re_path(r'^businessmedia/', include(wagtailadmin_urls),name='wagtail'),
    re_path(r'^documents/', include(wagtaildocs_urls)),
    re_path(r'', include(wagtail_urls)),

   

  )  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)