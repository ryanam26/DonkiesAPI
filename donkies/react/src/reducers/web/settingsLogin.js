import * as actions from 'actions'

const iState = null

export function settingsLogin(state=iState, action){
    switch(action.type){
        case actions.SETTINGS_LOGIN.SUCCESS:
            return action.payload

        default:
            return state
    }
}
