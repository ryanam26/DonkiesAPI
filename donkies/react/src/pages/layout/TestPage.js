import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import { InputAutocompleteAsync } from 'components'
import { INSTITUTIONS_SUGGEST_URL } from 'services/api'


export default class TestPageComponent extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }

    render(){
        return (
            <div />
        )
    }
}

TestPageComponent.propTypes = {
}

// <InputAutocompleteAsync
//     name="name"
//     placeholder="my placeholder"
//     url={INSTITUTIONS_SUGGEST_URL} />