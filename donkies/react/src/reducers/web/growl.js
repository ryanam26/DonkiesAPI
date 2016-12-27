/**
 * This reducer processes global growl alerts.
 * The state is array of growl objects.   
 * Required param for object: "message" and "id"
 * id is used for controlling Redux state (remove growls).
 * Other params are listed in class: services/Growl.js
 * 
 */

import * as actions from 'actions'

const iState = {
    data: []
}

export function growl(state=iState, action){
    switch(action.type){
        case actions.GROWL_ADD:
            return {
                ...state,
                data: [
                    ...state.data,
                    action.payload
                ]
            }

        case actions.GROWL_REMOVE:
            let newData = state.data.filter((obj) => obj.id !== action.id)
            return {
                ...state,
                data: newData
            }

        default:
            return state
    }
}
