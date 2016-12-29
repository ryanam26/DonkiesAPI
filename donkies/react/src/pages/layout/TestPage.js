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

        const suggestions = [
            {id: 1, value: 'text1'},
            {id: 2, value: 'text2'}
        ]

        return (
            <InputAutocomplete
                name="name"
                placeholder="my placeholder"
                suggestions={suggestions} />
        )
    }
}

TestPageComponent.propTypes = {
}

