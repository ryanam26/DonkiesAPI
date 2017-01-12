 import * as actions from 'actions'

const iState = {
    allAccounts: null,
    debtAccounts: null,
    debitAccounts: null
}


export function accounts(state=iState, action){
    switch(action.type){
        case actions.ACCOUNTS.REQUEST:
            return {
                ...state,
                allAccounts: null,
                debtAccounts: null,
                debitAccounts: null
            }

        case actions.ACCOUNTS.SUCCESS:
            let debtAccounts = []
            let debitAccounts = []

            for (let obj of action.payload){
                if (obj.type_ds === 'debt'){
                    debtAccounts.push(obj)    
                }

                if (obj.type_ds === 'debit'){
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
