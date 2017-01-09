import { combineReducers } from 'redux'
import { routerReducer } from 'react-router-redux'
import { auth } from './web/auth'
import { alerts } from './web/alerts'
import { growl } from './web/growl'
import { formErrors } from './web/formErrors'
import { menu } from './web/menu'
import { settings } from './web/settings'
import { settingsLogin } from './web/settingsLogin'
import { user } from './web/user'

const rootReducer = combineReducers({
    auth,
    alerts,
    formErrors,
    growl,
    menu,
    settings,
    settingsLogin,
    user,
    routing: routerReducer
})

export default rootReducer