import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'


export default class RegistrationPageComponent extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }

    render(){
        return (
            <div>{'RegistrationPageComponent'}</div>
        )
    }
}

RegistrationPageComponent.propTypes = {
}

