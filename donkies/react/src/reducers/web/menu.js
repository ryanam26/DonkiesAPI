 import * as actions from 'actions'

const iState = {
    activeUrl: null
}


export function menu(state=iState, action){
    switch(action.type){
        case actions.SET_ACTIVE_MENU:
            return {
                ...state,
                activeUrl: action.url
            }

        default:
            return state
    }
}
