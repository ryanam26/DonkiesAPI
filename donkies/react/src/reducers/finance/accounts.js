 import * as actions from 'actions'

const iState = {
    items: null
}


export function accounts(state=iState, action){
    switch(action.type){
        case actions.ACCOUNTS.SUCCESS:
            return {
                ...state,
                items: action.payload
            }

        default:
            return state
    }
}
