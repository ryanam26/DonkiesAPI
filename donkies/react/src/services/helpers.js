
import moment from 'moment'
import React from 'react'


export function validateEmail(email){
    var regex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/
    if(!regex.test(email)) {
        return false;   
    } 
    return true;
}     


/**
 * Get all form values and return object.
 */
export function formToObject(form){
  let res = {}
  for (let el of form.elements){
    let value = el.value
    if (typeof value === 'string'){
        value = value.trim()
    }
    res[el.name] = value
  }
  return res
}


/**
 * Object to query string foo=bar&lorem=ipsum
 */
export function objToParams(obj){
    return Object.keys(obj).map(
        k => k + '=' + encodeURIComponent(obj[k])
    ).join('&')    
}


/**
 * Undescore to camelCase
 */
export function toCamelCase(str){
  return str.toLowerCase().replace(
    /(_|-)([a-z])/g,
    (str) => str[1].toUpperCase()
  )
}


/**
 * Returns filtered data.
 * @param {string} value
 * @param {Array}  data - array of objects
 * @param {Array}  fields - array of strings
 */ 
export function filterData(value, data, fields){
    return data.filter((obj) => {
        for (let field of fields){
            if (obj.hasOwnProperty(field) && obj[field].toLowerCase().includes(value.toLowerCase())){
                return true    
            }    
        }
        return false 
    })
}

/**
 * Function for formatMoney besides prototype function formatMoney,
 * (positions API not always returns numbers)
 */
export function formatMoney(n, c, d, t){
    if (typeof n !== 'number')
        return 0

    c = isNaN(c = Math.abs(c)) ? 2 : c
    d = d === undefined ? '.' : d
    t = t === undefined ? ',' : t 
    let s = n < 0 ? '-' : ''
    let i = parseInt(n = Math.abs(+n || 0).toFixed(c)) + ''
    let j = (j = i.length) > 3 ? j % 3 : 0
    return s + (j ? i.substr(0, j) + t : '') + i.substr(j).replace(/(\d{3})(?=\d)/g, '$1' + t) + (c ? d + Math.abs(n - i).toFixed(c).slice(2) : '')
}


Array.prototype.flatResult = function (inputArray, ischild) {
    ischild = ischild || false;
    
    let i = 0, len = inputArray.length;

    for (i = 0; i < len; i++) {
        this.push(inputArray[i]);

        if (inputArray[i].children && typeof inputArray[i].children === typeof []) {
            this.flatResult(inputArray[i].children, true);
        }
    }
    
    if(ischild === false)
    {
        return this;
    }
}


Number.prototype.formatMoney = function(c, d, t){
    let n = this
    c = isNaN(c = Math.abs(c)) ? 2 : c
    d = d === undefined ? '.' : d
    t = t === undefined ? ',' : t 
    let s = n < 0 ? '-' : ''
    let i = parseInt(n = Math.abs(+n || 0).toFixed(c)) + ''
    let j = (j = i.length) > 3 ? j % 3 : 0
    return s + (j ? i.substr(0, j) + t : '') + i.substr(j).replace(/(\d{3})(?=\d)/g, '$1' + t) + (c ? d + Math.abs(n - i).toFixed(c).slice(2) : '')
}


export function zeroFill(num, size) {
    var s = num.toString()
    while (s.length < size){
        s = '0' + s
    }
    return s
}


export function createUUID() {
    let s = []
    let hexDigits = '0123456789abcdef'
    for (let i = 0; i < 36; i++) {
        s[i] = hexDigits.substr(Math.floor(Math.random() * 0x10), 1)
    }
    s[14] = '4'
    s[19] = hexDigits.substr((s[19] & 0x3) | 0x8, 1)
    s[8] = s[13] = s[18] = s[23] = '-'
    let uuid = s.join('')
    return uuid
}


export function isFloat(value){
    var re = /^[0-9]+$/;
    if (re.test(value)){
        return true;
    }
    re = /^[0-9]+\.[0-9]+$/;
    return ( re.test(value) ) ? true : false;
}


export function isInteger(value){
    var er = /^[0-9]+$/
    return ( er.test(value) ) ? true : false
}


/**
 * Empty row for table.
 */
export function getEmptyRow(numColumns){
    let row = {className: 'blank_row'}
    row.cols = [{value: '', colspan: numColumns}]
    return row
}


Array.prototype.move = function(fromIndex, toIndex) {
    this.splice(toIndex, 0, this.splice(fromIndex, 1)[0])
}


export function rHTML(html){
    return <wrap dangerouslySetInnerHTML={{__html: html}} />
}

/**
 * Converts date received by API to datetime string
 */
export function getDateTimeString(dt){
    return moment(dt).format('DD MMM HH:mm:ss')
}


Array.prototype.offset = function(os){
   return this.filter((e,i) => i > os - 1)
}


Array.prototype.limit = function(index) {
   return this.filter((e, i) =>  i < index)
}

/**
 * @param {number} currentPage
 * @param {number} numPages
 * @returns {array} - array of numbers
 *
 * Pagination consist of 3 ranges.
 * Example: 1 2 3 ... 7 8 9 ... 17 18 19
 *
 * Function returns combined 3 ranges.
 * Example: [1, 2, 3, 7, 8, 9, 17, 18, 19] 
 *
 * First range  [1, 2, 3]
 * Second range [currentPage - 1, currentPage, currentPage + 1]
 * Third range  [numPages - 2, numPages - 1, numPages]
 */
export function getPaginationArr(currentPage, numPages){
    let arr = [1]
    
    numPages > 1 && arr.push(2)
    numPages > 2 && arr.push(3)

    currentPage > 1 && arr.push(currentPage - 1)
    arr.push(currentPage)
    currentPage < numPages && arr.push(currentPage + 1)

    numPages > 2 && arr.push(numPages - 2)
    numPages > 1 && arr.push(numPages - 1)
    arr.push(numPages)

    arr = [... new Set(arr)]
    return arr.sort((a, b) => a > b)
}

/**
 * @param {number} amount
 * @returns {string} 
 * Examples: $10.00 -$10.00
 */
export function getDollarAmount(amount){
    if (amount >= 0){
        return `$${Math.abs(amount)}`
    }
    return `-$${Math.abs(amount)}`
}

/**
 * Returns sum of the array of numbers.
 */
export function getArraySum(arr){
    let sum = 0
    for (let num of arr){
        sum += num
    }
    return sum
}
    

