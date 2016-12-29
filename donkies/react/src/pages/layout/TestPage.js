import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import { InputAutocomplete } from 'components'


export default class TestPageComponent extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }

    render(){
        return (
            <InputAutocomplete />
        )
    }
}

TestPageComponent.propTypes = {
}

