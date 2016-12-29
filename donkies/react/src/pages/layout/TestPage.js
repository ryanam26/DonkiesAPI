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
            {text: 'text1', value: 'text1'},
            {text: 'text2', value: 'text2'}
        ]

        return (
            <InputAutocomplete
                name="name"
                placeholder="test"
                suggestions={suggestions} />
        )
    }
}

TestPageComponent.propTypes = {
}

