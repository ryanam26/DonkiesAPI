 import * as actions from 'actions'

const iState = {
    items: null
}


export function transactions(state=iState, action){
    switch(action.type){
        case actions.TRANSACTIONS.SUCCESS:
            return {
                ...state,
                items: action.payload
            }

        default:
            return state
    }
}
