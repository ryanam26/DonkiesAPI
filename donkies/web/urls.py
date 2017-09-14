from django.conf.urls import url, include
from django.views.generic import TemplateView
from .import views as v


handler404 = v.error404
handler500 = v.error500

urlpatterns = [

    url(r'^api-auth/', include("rest_framework.urls",
                               namespace='rest_framework')),

    url(r'^docs/$', v.SwaggerSchemaView.as_view()),

    url(r'^robots\.txt$', TemplateView.as_view(
        template_name='web/txt/robots.txt', content_type='text/plain')),

    url(
        r'^(?P<version>[v1]+)/auth/signup$',
        v.Signup.as_view(),
        name='signup'),

    url(
        r'^(?P<version>[v1]+)/auth/signup_parent$',
        v.SignupParent.as_view(),
        name='signup_parent'),

    url(
        r'^(?P<version>[v1]+)/auth/signup/confirm$',
        v.SignupConfirm.as_view(),
        name='signup_confirm'),

    url(
        r'^(?P<version>[v1]+)/auth/login$',
        v.Login.as_view(),
        name='login'),

    url(
        r'^(?P<version>[v1]+)/auth/logout$',
        v.Logout.as_view(),
        name='logout'),

    url(
        r'^(?P<version>[v1]+)/auth/facebook$',
        v.AuthFacebook.as_view(),
        name='auth_facebook'),

    url(
        r'^(?P<version>[v1]+)/password/reset/request$',
        v.PasswordResetRequest.as_view(),
        name='password_reset_request'),

    url(
        r'^(?P<version>[v1]+)/password/reset$',
        v.PasswordReset.as_view(),
        name='password_reset'),

    url(
        r'^(?P<version>[v1]+)/settings$',
        v.Settings.as_view(),
        name='settings'),

    url(
        r'^(?P<version>[v1]+)/settings/login$',
        v.SettingsLogin.as_view(),
        name='settings_login'),

    url(
        r'^(?P<version>[v1]+)/user/resend_reg_confirmation_link$',
        v.UserResendRegConfirmationLink.as_view(),
        name='user_resend_reg_confirmation_link'),

    url(
        r'^(?P<version>[v1]+)/user/change/password$',
        v.UserChangePassword.as_view(),
        name='user_change_password'),

    url(
        r'^(?P<version>[v1]+)/user/change/email$',
        v.UserChangeEmail.as_view(),
        name='user_change_email'),

    url(
        r'^(?P<version>[v1]+)/user/change/email/confirm/(?P<encrypted_id>\w+)/(?P<token>\w+)$',
        v.UserChangeEmailConfirm.as_view(),
        name='user_change_email_confirm'),

    url(
        r'^(?P<version>[v1]+)/user$',
        v.UserDetail.as_view(),
        name='user_detail'),

    url(
        r'^(?P<version>[v1]+)/user_settings$',
        v.UserSettings.as_view(),
        name='user_settings'),

    url(
        r'^(?P<version>[v1]+)/user_close_account$',
        v.UserCloseAccount.as_view(),
        name='user_close_account'),

    url(
        r'^(?P<version>[v1]+)/invite_parent$',
        v.InviteParent.as_view(),
        name='invite_parent'),

    url(r'^$', v.home, name='home'),
]
