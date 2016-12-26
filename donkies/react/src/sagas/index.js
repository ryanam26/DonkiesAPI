import { take, put, call, fork, select } from 'redux-saga/effects'
import { delay } from 'redux-saga'
import { history } from 'services'
import * as actions from 'actions'
import * as api from 'services/api'


import { watchApiGetRequest } from './web/apiGetRequest'
import { watchApiEditRequest } from './web/apiEditRequest'
import { watchRegistration } from './web/registration'
import { watchLogin } from './web/login'


function* watchNavigate(){
  while(true){
    const { pathname } = yield take(actions.NAVIGATE)
    yield history.push(pathname)
  }
}


export default function* root() {
  yield [
    fork(watchApiGetRequest),
    fork(watchApiEditRequest),
    fork(watchLogin),
    fork(watchNavigate),
    fork(watchRegistration),
  ]
}

