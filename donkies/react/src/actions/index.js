
// convention:
// GET - for sync calls, FETCH - for async calls

const GET = 'GET'
const FETCH = 'FETCH'
const HIDE = 'HIDE'
const SUBMIT = 'SUBMIT'
const REQUEST = 'REQUEST'
const RELOAD = 'RELOAD'
const SET = 'SET'
const SHOW = 'SHOW'
const SUCCESS = 'SUCCESS'
const ERROR = 'ERROR'
const SET_CLEAR_FORM = 'SET_CLEAR_FORM'
const UNSET_CLEAR_FORM = 'UNSET_CLEAR_FORM'

function createRequestTypes(base) {
  const res = {};
  [
    GET,
    FETCH,
    HIDE,
    SUBMIT,
    REQUEST,
    SET,
    SHOW,
    SUCCESS,
    RELOAD,
    SET_CLEAR_FORM,
    UNSET_CLEAR_FORM,
    ERROR].forEach(type => res[type] = `${base}_${type}`)
  
  return res;
}

export const API_GET_REQUEST = createRequestTypes('API_GET_REQUEST')
export const API_EDIT_REQUEST = createRequestTypes('API_EDIT_REQUEST')
export const LOGIN = createRequestTypes('LOGIN')
export const REGISTRATION = createRequestTypes('REGISTRATION')
export const TOKEN = createRequestTypes('TOKEN')

export const ALERT_ADD = 'ALERT_ADD'
export const ALERT_REMOVE = 'ALERT_REMOVE'
export const FORM_ERRORS =  'FORM_ERRORS'
export const LOGOUT =  'LOGOUT'
export const NAVIGATE =  'NAVIGATE'
export const RESET_ERROR_MESSAGE = 'RESET_ERROR_MESSAGE'
export const TOKEN_EXPIRED =  'TOKEN_EXPIRED'
export const UPDATE_ROUTER_STATE = 'UPDATE_ROUTER_STATE'


function action(type, payload = {}) {
  return {type, ...payload}
}

// Generic GET request
// Example: name="some"
// actions should have "SOME.FETCH", "SOME.SUCCESS", "SOME.ERROR"
// url should be equal "SOME_URL"  
export const apiGetRequest = (name, params, url=null) => action(API_GET_REQUEST.FETCH, {name, params, url})


// Generic EDIT (PATCH) request
// Example: name="some"
// actions should have "SOME_EDIT.SUCCESS", "SOME_EDIT.ERROR"
// url in api should be equal "SOME_URL"  
// form should conatain id (edit by id)
export const apiEditRequest = (name, id, form, url=null) => action(API_EDIT_REQUEST.SUBMIT, {name, id, form, url})


// layout
export const alertAdd = (alertType, message) => action(ALERT_ADD, {alertType, message})
export const alertRemove = (message) => action(ALERT_REMOVE, {message})
export const navigate = pathname => action(NAVIGATE, {pathname})
export const resetErrorMessage = () => action(RESET_ERROR_MESSAGE)
export const setFormErrors = (formType, errors) => action(FORM_ERRORS, {formType, errors})
export const updateRouterState = state => action(UPDATE_ROUTER_STATE, {state})


// auth
export const getToken = () => action(TOKEN.GET)
export const login = (email, password) => action(LOGIN.SUBMIT, {email, password})
export const logout = () => action(LOGOUT)
export const registration = (form) => action(REGISTRATION.SUBMIT, {form})
