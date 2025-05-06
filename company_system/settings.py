import dj_database_url
from pathlib import Path
import os
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-9xnll_s&6$uct))y6+rhhf2ovpy)9)6#zeg3e$y!i&*qogso!#'

DEBUG = True
ALLOWED_HOSTS = ['*']
AUTH_USER_MODEL = 'core.CustomUser'

# Приложения
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',
    'core',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # <- добавляем для мультиязычности
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'company_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'company_system.wsgi.application'

# База данных
DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://companysystemdb_user:utJNEJahb8aAZoJDnfvZ1lOjTQijo6u0@dpg-d08uuvqdbo4c73ebevv0-a.oregon-postgres.render.com/companysystemdb',
        conn_max_age=600,
        ssl_require=True
    )
}


# Валидаторы паролей
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

# Язык и время
LANGUAGE_CODE = 'ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Статические файлы
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

# Локализация
LANGUAGES = [
    ('ru', _('Russian')),
    ('en', _('English')),
    ('pl', _('Polish')),
]
LOCALE_PATHS = [BASE_DIR / 'locale']

# Защита: куда редиректить если не залогинен
LOGIN_URL = 'login'

# Ключ по умолчанию для моделей
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Медиа файлы (для загрузки и отдачи PDF, фото и т.п.)
MEDIA_URL = '/media/'
MEDIA_ROOT = '/var/data/media'

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')