import { take, put, call, fork, select } from 'redux-saga/effects'
import * as actions from 'actions'
import {
    CHANGE_EMAIL_URL,
    CHANGE_EMAIL_CONFIRM_URL,
    CHANGE_PASSWORD_URL,
    USER_URL,
     apiCall } from 'services/api'



// ------- Edit profile

function* editProfile(form){
    yield put({type: actions.EDIT_PROFILE.REQUEST}) 

    const result = yield call(apiCall, USER_URL, 'PUT', form, true)
    
    if (result.isError){
        yield put({type: actions.EDIT_PROFILE.ERROR, payload: result.data})    
        return
    } 
    
    yield put({type: actions.EDIT_PROFILE.SUCCESS, payload: result.data})
    
}

export function* watchEditProfile(){
  while(true){
    const { form } = yield take(actions.EDIT_PROFILE.SUBMIT)
    yield fork(editProfile, form)
  }
}


// ------- Change email

function* changeEmail(form){
    yield put({type: actions.CHANGE_EMAIL.REQUEST}) 

    const result = yield call(apiCall, CHANGE_EMAIL_URL, 'POST', form, true)
    
    if (result.isError){
        yield put({type: actions.CHANGE_EMAIL.ERROR, payload: result.data})  
        return  
    } 
    
    yield put({type: actions.CHANGE_EMAIL.SUCCESS, payload: result.data})
    yield put({
        type: actions.ALERT_ADD,
        alertType: 'success',
        message: result.data.message
    })
}

export function* watchChangeEmail(){
  while(true){
    const { form } = yield take(actions.CHANGE_EMAIL.SUBMIT)
    yield fork(changeEmail, form)
  }
}


// ------- Change password

function* changePassword(form){
    yield put({type: actions.CHANGE_PASSWORD.REQUEST}) 

    const result = yield call(apiCall, CHANGE_PASSWORD_URL, 'POST', form, true)
    
    if (result.isError){
        yield put({type: actions.CHANGE_PASSWORD.ERROR, payload: result.data})  
        return  
    } 

    yield put({type: actions.CHANGE_PASSWORD.SUCCESS, payload: result.data})
    
    yield put({
        type: actions.ALERT_ADD,
        alertType: 'success',
        message: result.data.message
    })
    
}

export function* watchChangePassword(){
  while(true){
    const { form } = yield take(actions.CHANGE_PASSWORD.SUBMIT)
    yield fork(changePassword, form)
  }
}