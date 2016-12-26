import { take, put, call, fork, select } from 'redux-saga/effects'
import * as actions from 'actions'
import { REGISTRATION_URL, apiCall } from 'services/api'


function* registration(form){
    const result = yield call(apiCall, REGISTRATION_URL, 'POST', form)
    if (result.isError){
        yield put({type: actions.REGISTRATION.ERROR, payload: result.data})    
    } else {
        yield put({type: actions.REGISTRATION.SUCCESS, payload: ''})
    }
}

export function* watchRegistration(){
  while(true){
    const { form } = yield take(actions.REGISTRATION.SUBMIT)
    yield fork(registration, form)
  }
}