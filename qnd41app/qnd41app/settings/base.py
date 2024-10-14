import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from the .env_stage file.
ENV_FILE_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_FILE_PATH)

# Retrieve the Django secret key from environment variables.
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# Optionally, you can add a default value or raise an exception if SECRET_KEY is not set
if SECRET_KEY is None:
    raise ValueError("DJANGO_SECRET_KEY is not set in the environment variables.")

# Application definition
INSTALLED_APPS = [
    'baton',
    'businessmodel',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',  # Asegúrate de que esta línea esté presente
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'core',
    'wagtail',
    'wagtailmedia',
    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'django.contrib.humanize',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.locales',
    'rosetta',
    'wagtail.admin',
    'wagtail.contrib.routable_page',
    "wagtail_localize",
    'wagtailgmaps',
    'wagtailmenus',
    'django_social_share',
    'taggit',
    'widget_tweaks',
    'django_forms_bootstrap',

    'social_django',
    'sorl.thumbnail',
    'embed_video',
    'qr_code',
    'storages',
    'django_countries',
    'cities_light',
    'rest_framework',
    #'ckeditor',
    'django_matplotlib',
    
    'wagtail.contrib.settings',
    'baton.autodiscover',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
]

ROOT_URLCONF = 'qnd41app.urls'

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]


BATON = {
    'SITE_HEADER': '<a href="#"><img src="/static/img/m2.png" height="26px"></a>',
    'SITE_TITLE': '',
    'INDEX_TITLE': 'Business Analytics Board',
    'SUPPORT_HREF': '#',
    'COPYRIGHT': '<a href="#"><img src="/static/img/m2.png" height="18px"></a>&nbsp;&nbsp; copyright © 2024', # noqa
    'POWERED_BY': '<a href="#"><img src="/static/img/logo_smartquailgray.png" height="13px"</a>',
    'CONFIRM_UNSAVED_CHANGES': True,
    'SHOW_MULTIPART_UPLOADING': True,
    'ENABLE_IMAGES_PREVIEW': True,
    'CHANGELIST_FILTERS_IN_MODAL': True,
    'CHANGELIST_FILTERS_ALWAYS_OPEN': False,
    'CHANGELIST_FILTERS_FORM': True,
    'MENU_ALWAYS_COLLAPSED': True,
    'MENU_TITLE': 'Todo en Orden',
    'MESSAGES_TOASTS': False,
    'GRAVATAR_DEFAULT_IMG': 'retro',
    'LOGIN_SPLASH': '/static/img/fondo.jpg',
   
    'MENU': (
       
        {
            'type': 'app',
            'name': 'auth',
            'label': 'Authentication',
            'icon': 'fa fa-lock',
            'models': (
                {
                    'name': 'user',
                    'label': 'Users'
                },
                {
                    'name': 'group',
                    'label': 'Groups'
                },
            )
        },
         { 'type': 'title', 'label': 'Dirección Espacio Público', 'apps': ('auth','todo_en_orden', ) },
         {
            'type': 'app',
            'name': 'actividades_espacio_publico',
            'label': 'Propuestas',
            'icon': 'fa fa-user',
            'models': (
                {
                    'name': 'subject',
                    'label': 'Administración de eventos'
                },
                {
                    'name': 'evento_30000',
                    'label': 'Evento 30000'
                },
                 {
                    'name': 'evento_20000',
                    'label': 'Evento 20000'
                },
                {
                    'name': 'evento_10000',
                    'label': 'Evento 10000'
                },
                {
                    'name': 'evento_5000',
                    'label': 'Evento 5000'
                },
              
            )
        },
         { 'type': 'title', 'label': 'Dirección Creatividad & Fomento', 'apps': ('auth','todo_en_orden', ) },
        {
            'type': 'app',
            'name': 'editorial_literaria',
            'label': 'Editorial & literario',
            'icon': 'fa fa-user',
            'models': (
                {
                    'name': 'subject',
                    'label': 'Categorías de convocatorias'
                },
                {
                    'name': 'course',
                    'label': 'Convocatorias realizadas'
                },
                
                {
                    'name': 'module',
                    'label': 'Bases técnicas inscriptas en convocatorias'
                },
              
            )
        },
         {
            'type': 'app',
            'name': 'proyectos',
            'label': 'Proyectos postulados',
            'icon': 'fa fa-user',
            'models': (
                {
                    'name': 'subject',
                    'label': 'Volumenes editoriales'
                },
                {
                    'name': 'project',
                    'label': 'Proyectos editoriales '
                },
            )
        },

         { 'type': 'title', 'label': 'Administración de perfiles', 'apps': ('auth','todo_en_orden', ) },
              {
            'type': 'app',
            'name': 'usuarios',
            'label': 'Administración de usuarios',
            'icon': 'fa fa-user',
            'models': (
                {
                    'name': 'profile',
                    'label': 'Perfil de usuarios'
                },
                {
                    'name': 'contacts',
                    'label': 'Perfil de contactos'
                },
                {
                    'name': 'legal',
                    'label': 'Perfil de personería'
                },
                {
                    'name': 'activity',
                    'label': 'Perfil de actividad cultural'
                },
                {
                    'name': 'declaracionveracidad',
                    'label': 'declaratorias'
                },
            )
        },
         { 'type': 'title', 'label': 'Comunicación', 'apps': ('auth','todo_en_orden', ) },
         {
            'type': 'app',
            'name': 'usuarios',
            'label': 'Información y Normativas',
            'icon': 'fa fa-user',
            'models': (
                {
                    'name': 'dashboard',
                    'label': 'Pagina de Inicio'
                },
                {
                    'name': 'privacypolicy',
                    'label': 'Políticas de privacidad Fomento editorial'
                },
                {
                    'name': 'termsofuse',
                    'label': 'Condiciones de uso Fomento editorial'
                },

                {
                    'name': 'activityprivacypolicy',
                    'label': 'Políticas de privacidad Espacio público'
                },
                 {
                    'name': 'activitytermsofuse',
                    'label': 'Condiciones de uso Espacio público'
                },


            )
        },
   

        
         
    ),
}


# Wagtail setups
WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.search.backends.database',
    }
}

WAGTAILADMIN_BASE_URL = 'https://www.smartquail.io/'
WAGTAIL_SITE_NAME = 'Smart Business Media'

# REST framework settings
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}

# Braintree setup
BRAINTREE_MERCHANT_ID = os.environ.get('BRAINTREE_M_ID')
BRAINTREE_PUBLIC_KEY = os.environ.get('BRAINTREE_KEY')
BRAINTREE_PRIVATE_KEY = os.environ.get('BRAINTREE_PRIVATE_KEY')

from braintree import Configuration, Environment

Configuration.configure(
    Environment.Sandbox,
    BRAINTREE_MERCHANT_ID,
    BRAINTREE_PUBLIC_KEY,
    BRAINTREE_PRIVATE_KEY
)

# Authentication backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'wagtailmenus.context_processors.wagtailmenus',
                'wagtail.contrib.settings.context_processors.settings',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = 'qnd41app.wsgi.application'

WAGTAIL_ADMIN_BASE_URL = os.environ.get('DOMAINS')
WAGTAILIMAGES_MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5 MB en bytes
WAGTAILIMAGES_MAX_IMAGE_PIXELS = 1000000000  # 1 billón de píxeles

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'es-Ec'
TIME_ZONE = 'America/Guayaquil'

WAGTAIL_CONTENT_LANGUAGES = LANGUAGES = [
    ('en', 'English'),
    ('fr', 'French'),
    ('es', 'Spanish'),
]

WAGTAIL_I18N_ENABLED = True

USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)


