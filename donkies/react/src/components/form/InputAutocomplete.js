import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import InputAutocompleteUI from './ui/InputAutocompleteUI'


/**
 * Component with static suggestions.
 * Pass suggestion to dump InputAutocompleteUI and
 * after getting value filter suggestions and send them back
 * to UI component.
 *
 * @param {array} suggestions.
                  Suggestions that come from props go to state.
 *
 */

export default class InputAutocomplete extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }

    componentWillMount(){
        const arr = this.props.suggestions
        this.setState({
            suggestions: arr,
            suggestionsAll: arr
        })   
    }

    filterSuggestions(value){
        const { suggestionsAll } = this.state

        if (value.trim().length === 0){
            this.setState({suggestions: suggestionsAll})            
        }

        const arr = suggestionsAll.filter(
            (obj) => obj.value.includes(value))

        this.setState({suggestions: arr})
    }

    onUpdate(value){
        this.filterSuggestions(value)
    }

    render(){
        const {suggestions, ...other} = this.props

        return (
            <InputAutocompleteUI
                suggestions={this.state.suggestions}
                onUpdate={this.onUpdate}
                {...other} />
        )
    }
}


InputAutocomplete.propTypes = {
    disabled: PropTypes.bool,
    name: PropTypes.string.isRequired,
    placeholder: PropTypes.string,
    suggestions: PropTypes.arrayOf(
        PropTypes.shape({
            text: PropTypes.string,
            value: PropTypes.string
        })
    ).isRequired,
    type: PropTypes.string
}
