import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import InputAutocompleteUI from './ui/InputAutocompleteUI'


/**
 * Component with suggestions received by API.
 * Pass suggestions to dump InputAutocompleteUI and
 * after getting value fetch data from server and send them back
 * to UI component.
 *
 * @param {string} url. API url, that should return
 *                      array of suggestions.
 *
 */

export default class InputAutocompleteAsync extends Component{
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


InputAutocompleteAsync.propTypes = {
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


/*
import { apiCall2, ___URL } from 'services/api'

async sendRequest() {
        this.setState({isProcessing: true})
        let response = await apiCall2(___URL, true) 
        let data = await response.json()
        this.setState({message: data.message})
    }

*/