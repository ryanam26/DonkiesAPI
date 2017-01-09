import * as actions from 'actions'

const iState = null

export function settings(state=iState, action){
    switch(action.type){
        case actions.SETTINGS.SUCCESS:
            return action.payload

        default:
            return state
    }
}
