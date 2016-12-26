import { combineReducers } from 'redux'
import { routerReducer } from 'react-router-redux'
import { auth } from './web/auth'
import { alerts } from './web/alerts'
import { formErrors } from './web/formErrors'
import { menu } from './web/menu'

const rootReducer = combineReducers({
    auth,
    alerts,
    formErrors,
    menu,
    routing: routerReducer
})

export default rootReducer