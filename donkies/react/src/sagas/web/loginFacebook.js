import { take, put, call, fork, select } from 'redux-saga/effects'
import * as actions from 'actions'
import { LOGIN_FACEBOOK_URL, apiCall } from 'services/api'


/**
 * Saga uses separate API url for login facebook,
 * but result is the same as regular login.
 * Get token if success, else error.
 * Therefore the reducer is the same as in regular login. 
 */
function* loginFacebook(code){
    let data = {code}
    const result = yield call(apiCall, LOGIN_FACEBOOK_URL, 'POST', data)
    if (result.isError){
        yield put({type: actions.LOGIN.ERROR, payload: result.data})    
    } else {
        yield put({type: actions.LOGIN.SUCCESS, payload: result.data.token})
    }
}

export function* watchLoginFacebook(){
  while(true){
    const { code } = yield take(actions.LOGIN_FACEBOOK.SUBMIT)
    yield fork(loginFacebook, code)
  }
}


