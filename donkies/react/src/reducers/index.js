import { combineReducers } from 'redux'
import { routerReducer } from 'react-router-redux'
import { auth } from './web/auth'
import { alerts } from './web/alerts'
import { formErrors } from './web/formErrors'

const rootReducer = combineReducers({
    auth,
    alerts,
    formErrors,
    routing: routerReducer
})

export default rootReducer