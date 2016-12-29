import React, {Component, PropTypes} from 'react'
import autoBind from 'react-autobind'
import Autosuggest from 'react-autosuggest'
import { apiCall2 } from 'services/api'
import { FieldWrapper } from 'components'

/**
 * Generic autosuggest for all charfields.
 *
 * It gets API url for getting suggestions.
 * Format of data provided by server should be (value, text):
 * example: [ {'value': '...', 'text': '...'}, ]
 * "text" - showing to user, "value" - sets to input value. 
 *
 * props: name, errors, label, isVisible, isLoading passed to FieldWrapper
  * FieldWrapper knows how to render errors.
 */
export default class InputAutoSuggest extends Component {
    static get defaultProps() {
        return {
            disabled: false,
            type: 'text'
        }
    }

    constructor(props){
        super(props)
        autoBind(this)
        
        this.state = {
            value: '',
            isLoading: false,
            suggestions: []
        }
    }

    onKeyDown(e){
        const { onUpdate } = this.props

        if (e.keyCode === 13){
            e.preventDefault()
            if (onUpdate){
                onUpdate(e.target.value) 
            }
        }
    }

    onChange(e, {newValue, method}) {
        this.setState({value: newValue})
    }

    getSuggestionValue(suggestion) {
        return suggestion.value
    }

    async onSuggestionsUpdateRequested({ value, reason }) {
        this.setState({isLoading: true})
        const url = this.props.url + '?value=' + value
        let response = await apiCall2(url, true)
        let data = await response.json()
        this.setState({suggestions: data, isLoading: false})    
    }
 
    renderSuggestion(suggestion) {
        return (
            <span>{suggestion.text}</span>
        )
    }

    render() {
        const { disabled, name, type, placeholder, ...other } = this.props
        const { value, suggestions } = this.state

        // Props that goes to <input />
        const inputProps = {
            //defaultValue: value,
            value: value,
            disabled: disabled,
            name: name,
            type: type,
            placeholder: placeholder,
            onKeyDown: this.onKeyDown,
            onChange: this.onChange,
            className: 'form-control'
        }

        return (
            <FieldWrapper name={name} isLoading={this.state.isLoading} {...other}>
                <Autosuggest 
                    suggestions={suggestions}
                    getSuggestionValue={this.getSuggestionValue}
                    onSuggestionsUpdateRequested={this.onSuggestionsUpdateRequested}
                    renderSuggestion={this.renderSuggestion}
                    inputProps={inputProps} />
            </FieldWrapper>
        )
    }
}


InputAutoSuggest.propTypes = {
    disabled: PropTypes.bool,
    errors: PropTypes.object,
    label: PropTypes.string,
    name: PropTypes.string.isRequired,
    // pass value to parent
    onUpdate: PropTypes.func,
    placeholder: PropTypes.string,
    type: PropTypes.string,
    url: PropTypes.string.isRequired,
    value: PropTypes.any
}
