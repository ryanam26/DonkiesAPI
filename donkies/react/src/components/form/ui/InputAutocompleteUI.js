import React, {Component, PropTypes} from 'react'
import autoBind from 'react-autobind'
import Autosuggest from 'react-autosuggest'


/**
 * Presentational component.
 * dependencies: css/react-autosuggest.css
 *
 * @param {array} - suggestions.
 *                  Array of objects {text:..., value:...}
 *                  In most cases text == value.
 *                  In special cases value can be different.
 *                  "value" comes to input after selection.  
 *
 * @param {function} - onUpdate
 *                     Send updated value to parent and parent
 *                     should send back new suggestions accordingly
 *                     to new value. 
 *
 * Other params passed to input props. 
 *
 * onBlur checks if current value is not in suggestions, 
 * set value to empty and send updated value to parent.
 *
 */
export default class InputAutocompleteUI extends Component {
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
            isLoading: false
        }
    }

    onBlur(e){
        const { value } = this.state
        console.log(':::', value)
        if (!this.checkValue(value)){
            this.setState({value: ''})
            this.props.onUpdate('')    
        }
    }

    onChange(e, {newValue, method}) {
        this.setState({value: newValue})
    }

    onUpdate({ value, reason }) {
        this.props.onUpdate(value)
    }

    /**
     * @param {string} value
     * @returns {bool}
     * Check if value exist in suggestions
     */
    checkValue(value){
        const { suggestions } = this.props
        for (let obj of suggestions){
            if (obj.value === value){
                return true
            }
        }
        return false
    }

    getSuggestionValue(suggestion) {
        return suggestion.value
    }
 
    renderSuggestion(suggestion) {
        return (
            <span>{suggestion.text}</span>
        )
    }

    render() {
        const { disabled, name, type, placeholder, suggestions, ...other } = this.props
        const { value } = this.state

        // Props that goes to <input />
        const inputProps = {
            value: value,
            disabled: disabled,
            name: name,
            type: type,
            placeholder: placeholder,
            onChange: this.onChange,
            onBlur: this.onBlur,
            className: 'form-control'
        }

        return (
            <wrap>
            <Autosuggest 
                suggestions={this.props.suggestions}
                getSuggestionValue={this.getSuggestionValue}
                onSuggestionsUpdateRequested={this.onUpdate}
                renderSuggestion={this.renderSuggestion}
                inputProps={inputProps} />

            

            </wrap>
            
        )
    }
}


InputAutocompleteUI.propTypes = {
    disabled: PropTypes.bool,
    name: PropTypes.string.isRequired,
    // pass value to parent
    onUpdate: PropTypes.func.isRequired,
    placeholder: PropTypes.string,
    suggestions: PropTypes.array,
    type: PropTypes.string,
}
