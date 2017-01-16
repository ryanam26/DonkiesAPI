import * as actions from 'actions'
import { DEBIT, DEBT } from 'constants'


const iState = {
    allAccounts: null,
    debtAccounts: null,
    debitAccounts: null
}


export function accounts(state=iState, action){
    switch(action.type){
        case actions.ACCOUNTS.REQUEST:
            return {
                ...state
            }

        case actions.ACCOUNTS.SUCCESS:
            let debtAccounts = []
            let debitAccounts = []

            for (let obj of action.payload){
                if (obj.type_ds === DEBT){
                    debtAccounts.push(obj)    
                }

                if (obj.type_ds === DEBIT){
                    debitAccounts.push(obj)    
                }
            }

            return {
                ...state,
                allAccounts: action.payload,
                debtAccounts: debtAccounts,
                debitAccounts: debitAccounts
            }

        default:
            return state
    }
}
