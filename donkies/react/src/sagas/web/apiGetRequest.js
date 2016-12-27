/**
 * Generic API GET request. The name of request is equal the uppercase of action.
 * Example: name="some"
 * Actions: SOME.SUCCESS, SOME.ERROR
 * Url: SOME_URL 
 */

import { take, put, call, fork, select } from 'redux-saga/effects'
import * as actions from 'actions'
import * as api from 'services/api'
import { apiCall } from 'services/api'


/**
 * Require auth by default.
 */
function* apiGet(name, params, url){
    // TODO: add params to url
    const a = actions[name.toUpperCase()]
    const urlKey = `${name.toUpperCase()}_URL`
    if (!url){
        url = api[urlKey]    
    }
    
    let useToken = (params && params.hasOwnProperty('useToken') && params.useToken === false) ? false : true

    yield put({type: a.REQUEST})

    const result = yield call(apiCall, url, 'GET', {}, useToken)
    if (result.isError){
        yield put({type: a.ERROR, payload: result.data})    
    } else {
        yield put({type: a.SUCCESS, payload: result.data})
    }
}

export function* watchApiGetRequest(){
  while(true){
    const { name, params, url } = yield take(actions.API_GET_REQUEST.FETCH)
    yield fork(apiGet, name, params, url)
  }
}


