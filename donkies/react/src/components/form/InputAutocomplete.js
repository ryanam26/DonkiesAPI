import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import InputAutocompleteUI from './ui/InputAutocompleteUI'


export default class InputAutocomplete extends Component{
    constructor(props){
        super(props)
        autoBind(this)

        this.state = {
            suggestions: []
        }

    }

    onUpdate(value){
        const suggestions = [
            {text: 'text1', value: 'text1'},
            {text: 'text2', value: 'text2'}
        ]
        this.setState({suggestions: suggestions})

        console.log('my value:', value)
    }

    render(){

        

        return (
                <InputAutocompleteUI
                    name="name"
                    suggestions={this.state.suggestions}
                    onUpdate={this.onUpdate} />
            
        )
    }
}


InputAutocomplete.propTypes = {
    
}
