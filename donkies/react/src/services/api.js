import 'whatwg-fetch'
import { put } from 'redux-saga/effects'
import { TOKEN_EXPIRED } from 'actions'
import { API_ROOT_URL } from 'store/configureStore'
   
export const LOGIN_URL = `${API_ROOT_URL}v1/auth/login`
export const REGISTRATION_URL = `${API_ROOT_URL}v1/auth/signup`


/**
 * Generic api call to all endpoints.
 * Under any circumstance function should 
 * return result object {isError, data}. 
 *
 * @param {string}  url
 * @param {string}  method - GET, POST, PUT, PATCH, DELETE
 * @param {Object}  data   
 * @param {boolean} isAuth - Does request need token.
 * 
 * @returns {Object}  obj
 * @returns {boolean} obj.isError
 * @returns {Object}  obj.data - requested data from server
 *                               or errors object
 *
 * data errors example: possible keys {
 *   field1: ['error1'],
 *   field2: ['error2', 'error3'],
 *   non_field_errors: ['error4']}
 */
export function* apiCall(url, method, data, isAuth){
    isAuth = isAuth || false

    let promise
    let result = {isError: false}
    
    let token = ''
    if (isAuth){
        token = window.localStorage.getItem('token')    
        if (token === null){
            result.isError = true
            result.data = {non_field_errors: ['The token is not provided.']}
            return result
        }    
    }
    
    try {
        let fetchObj = {method: method}
        
        if (method === 'POST' || method === 'PUT' || method === 'PATCH'){
            fetchObj.body = JSON.stringify(data)
        }

        fetchObj.headers =  {'Accept': 'application/json', 'Content-Type': 'application/json'}
        
        if (isAuth){
            fetchObj.headers.Authorization = 'Token ' + token
        }

        yield promise = fetch(url, fetchObj)    
    } catch(e){
        result.isError = true
        result.data = {non_field_errors: ['Connection error.']}
        return result
    }

    const status = yield promise.then(resp => resp.status).then(data)
    const text = yield promise.then(resp => resp.text()).then(data)

    if (status === 404){
        result.isError = true
        result.data = {non_field_errors: ['Page not found.']}
        return result
    }

    if (status === 500){
        result.isError = true
        result.data = {non_field_errors: ['Internal server error.']}
        return result
    }

    // Process success case, where no content
    if (status >= 200 && status <= 300 && text.length === 0){
        result.data = {}
        return result
    }
    
    // All other success cases should get valid json object
    // otherwise it is error.
    let obj
    try{
        obj = JSON.parse(text)
    } catch(e){
        result.isError = true
        result.data = {non_field_errors: [text]}
        return result
    }

    if (status >= 200 && status <= 300){
        result.data = obj
        return result
    }

    // When token wrong - remove it from localstorage.
    if (obj.hasOwnProperty('error_code')){
        if (obj.error_code === 'Bad Token'){
            yield put({type: TOKEN_EXPIRED})
        }
    }

    // DRF in many error cases returns {detail: string}
    if (obj.hasOwnProperty('detail')){
        result.isError = true
        result.data = {non_field_errors: [obj.detail]}
        return result
    }

    // In all other cases it should be valid json object with errors.
    result.isError = true
    result.data = obj
    return result
}


/**
 * This function returns promise.
 * Used for simple GET requests inside component.
 * Doesn't process errors.
 */
export function apiCall2(url, isAuth){
    let fetchObj = {method: 'GET'}
    fetchObj.headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    if (isAuth){
        let token = window.localStorage.getItem('token')
        if (token !== null){
            fetchObj.headers.Authorization = 'Token ' + token    
        }
    }
    return fetch(url, fetchObj)
}


/**
 * This function returns promise.
 * Used for POST requests inside component.
 */
export function apiCall3(url, data, isAuth){
    let fetchObj = {method: 'POST'}
    fetchObj.body = JSON.stringify(data)
    fetchObj.headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    if (isAuth){
        let token = window.localStorage.getItem('token')
        if (token !== null){
            fetchObj.headers.Authorization = 'Token ' + token    
        }
    }
    return fetch(url, fetchObj)
}