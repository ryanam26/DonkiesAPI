import React, {Component, PropTypes} from 'react'
import { Login } from 'components'


/**
 * Not auth page
 */
export default class LoginPage extends Component{
    constructor(props){
        super(props)
    }

    render(){
        return <Login />
    }
}
