from django.conf.urls import url
from django.views.generic import TemplateView
from .import views as v

handler404 = v.error404
handler500 = v.error500


urlpatterns = [
    url(r'^robots\.txt$', TemplateView.as_view(
        template_name='web/txt/robots.txt', content_type='text/plain')),

    url(r'^auth/login/', v.login, name='auth_login'),
    url(r'^auth/logout/$', v.logout, name='auth_logout'),
    url(r'^test', TemplateView.as_view(template_name='web/test.html')),

    url(
        r'^(?P<version>(v1))/oauth/test$',
        v.OauthTest.as_view(),
        name='oauth_test'),

    url(
        r'^(?P<version>(v1))/auth/signup$',
        v.Signup.as_view(),
        name='signup'),

    url(
        r'^(?P<version>(v1))/auth/signup/confirm$',
        v.SignupConfirm.as_view(),
        name='signup_confirm'),

    url(
        r'^(?P<version>(v1))/auth/login$',
        v.Login.as_view(),
        name='login'),

    url(
        r'^(?P<version>(v1))/password/reset/require$',
        v.PasswordResetRequire.as_view(),
        name='password_reset_require'),

    url(
        r'^(?P<version>(v1))/password/reset$',
        v.PasswordReset.as_view(),
        name='password_reset'),

    url(
        r'^(?P<version>(v1))/user$',
        v.UserDetail.as_view(),
        name='user_detail'),

    url(r'^$', v.api_root, name='api_root'),
]
