import React from 'react'
import { Route, IndexRoute } from 'react-router'

import {
    AccountsPage,
    ForgotPasswordPage,
    HomePage,
    LoginPage,
    NotFoundPage,
    RegistrationPage,
    RegistrationConfirmPage,
    SettingsPage,
    TestPage,
    UserProfilePage } from 'pages'


import App from 'containers/App'
import { requireAuth } from 'components/Auth'


export default (
    <div>
        <Route component={LoginPage} path="/login" />     
        <Route component={RegistrationPage} path="/registration" />
        <Route component={RegistrationConfirmPage} path="/confirm" />
        <Route component={ForgotPasswordPage} path="/forgot_password" />     
                
        <Route component={requireAuth(App)} path="/">
            <IndexRoute component={HomePage} />
            <Route component={AccountsPage} path="/accounts" />
            <Route component={SettingsPage} path="/settings" />
            <Route component={TestPage} path="/test_page" />
            <Route component={UserProfilePage} path="/user_profile" />
        </Route>

        <Route component={NotFoundPage} path="*" /> 
    </div>
)
