/**
 * Generic API PATCH request. The name of request is equal the uppercase of action.
 * Example: name="some"
 * Actions: SOME_EDIT.SUCCESS, SOME_EDIT.ERROR
 * Url: SOME_URL 
 * SOME URL should have pk(id)
 * /v1/some/:id
 */

import { take, put, call, fork, select } from 'redux-saga/effects'
import * as actions from 'actions'
import * as api from 'services/api'
import { apiCall } from 'services/api'



function* apiEdit(name, id, form, url){
    const actionKey = `${name.toUpperCase()}_EDIT`
    const a = actions[actionKey]
    const urlKey = `${name.toUpperCase()}_URL`
    
    if (!url){
        url = `${api[urlKey]}/${id}`      
    }
    
    const result = yield call(apiCall, url, 'PATCH', form, true)
    if (result.isError){
        yield put({type: a.ERROR, payload: result.data})    
    } else {
        yield put({type: a.SUCCESS, payload: result.data})
    }
}

export function* watchApiEditRequest(){
  while(true){
    const { name, id, form, url } = yield take(actions.API_EDIT_REQUEST.SUBMIT)
    yield fork(apiEdit, name, id, form, url)
  }
}


