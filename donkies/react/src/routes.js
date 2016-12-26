import React from 'react'
import { Route, IndexRoute } from 'react-router'

import {
    HomePage,
    NotFoundPage,
    TestPage,
    LoginPage,
    ForgotPasswordPage,
    RegistrationPage } from 'pages'


import App from 'containers/App'
import { requireAuth } from 'components/Auth'


export default (
    <div>
        <Route component={LoginPage} path="/login" />     
        <Route component={RegistrationPage} path="/registration" />     
                
        <Route component={requireAuth(App)} path="/">
            <IndexRoute component={HomePage} />
            <Route component={TestPage} path="/test_page" />
        </Route>

        <Route component={NotFoundPage} path="*" /> 
    </div>
)
