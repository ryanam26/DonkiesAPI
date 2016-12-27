/*
    This reducer processes all form errors.
    Action can arrive from front-end:
    Example: type: FORM_ERRORS, action: {formType: 'login', errors: errors}

    Action can arrive from back-end (via saga)
    Example: type: LOGIN_ERROR, action: payload (payload contains errors)

    The errors object is always has same properties:
    field1: [errors]
    field2: [errors]
    non_field_errors: [errors]
*/


import * as actions from 'actions'

const iState = {
    login: null,
    registration: null,
    changeEmail: null,
    changePassword: null,
    editProfile: null

}


export function formErrors(state=iState, action){
    switch(action.type){
        case actions.FORM_ERRORS:
            if (action.formType === 'clear'){
                return iState
            } else {
                return {
                    ...iState,
                    [action.formType]: action.errors
                }    
            }

        case actions.LOGIN.ERROR:
            return {
                ...iState,
                login: action.payload
            }

        case actions.REGISTRATION.ERROR:
            return {
                ...iState,
                registration: action.payload
            }

        case actions.EDIT_PROFILE.ERROR:
            return {
                ...iState,
                editProfile: action.payload
            }

        case actions.CHANGE_EMAIL.ERROR:
            return {
                ...iState,
                changeEmail: action.payload
            }

        case actions.CHANGE_PASSWORD.ERROR:
            return {
                ...iState,
                changePassword: action.payload
            }

        default:
            return state
    }
}





        

