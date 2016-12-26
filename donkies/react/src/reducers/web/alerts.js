/**
 * This reducer processes global site alerts.
 * The state is array of alert objects.   
 * Each objects has 2 properties: alertType, message
 * "alertType" can be one of: info, success, warning, danger
 */

import * as actions from 'actions'

const iState = {
    data: []
}

export function alerts(state=iState, action){
    switch(action.type){
        case actions.ALERT_ADD:
            return {
                ...state,
                data: [
                    ...state.data,
                    {alertType: action.alertType, message: action.message}
                ]
            }
            
        case actions.ALERT_REMOVE:
            let newData = state.data.filter((obj) => obj.message !== action.message)
            return {
                ...state,
                data: newData
            }

        default:
            return state
    }
}
