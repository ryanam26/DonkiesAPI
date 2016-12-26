import { take, put, call, fork, select } from 'redux-saga/effects'
import * as actions from 'actions'
import { LOGIN_URL, apiCall } from 'services/api'


function* login(email, password){
    let data = {email, password}
    const result = yield call(apiCall, LOGIN_URL, 'POST', data)
    if (result.isError){
        yield put({type: actions.LOGIN.ERROR, payload: result.data})    
    } else {
        yield put({type: actions.LOGIN.SUCCESS, payload: result.data.token})
    }
}

export function* watchLogin(){
  while(true){
    const { email, password } = yield take(actions.LOGIN.SUBMIT)
    yield fork(login, email, password)
  }
}


