import React, {Component, PropTypes} from 'react'
import autoBind from 'react-autobind'
import classNames from 'classnames'
import Autosuggest from 'react-autosuggest'


/**
 * Presentational component.
 * dependencies: css/react-autosuggest.css
 *
 * @param {array} suggestions.
 *                Array of objects {id:..., value:...}
                  "value" goes to input element value.
                  "id" used in parent component. 
 *
 * @param {function} onUpdate
 *                   Send updated value to parent and parent
 *                   should send back new suggestions accordingly
 *                   to new value. 
 *
 * Other params passed to input props. 
 *
 * onBlur checks if current value is not in suggestions, 
 * and set isError.
 *
 */
export default class InputAutocompleteUI extends Component {
    static get defaultProps() {
        return {
            disabled: false,
            type: 'text',
            isError: false
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
        if (!this.checkValue(value)){
            this.setState({isError: true})
            this.props.onUpdate('')    
        } else {
            this.setState({isError: false})
        }
    }

    onKeyDown(e){
        if (e.keyCode === 13){
            e.preventDefault()
        }
    }

    /**
     * Called on each input change.
     */
    onChange(e, {newValue, method}) {
    }

    /**
     * Called every time we need update suggestions.
     */
    onUpdate({ value }) {
        if (this.state.value === value){
            return
        }
        this.setState({value: value, isError: false})
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
            <span>{suggestion.value}</span>
        )
    }

    render() {
        const { disabled, name, type, placeholder, suggestions, ...other } = this.props
        const { value, isError } = this.state

        const cn = classNames('form-control', {'error': isError})

        // Props that goes to <input />
        const inputProps = {
            value: value,
            disabled: disabled,
            name: name,
            type: type,
            placeholder: placeholder,
            onChange: this.onChange,
            onBlur: this.onBlur,
            onKeyDown: this.onKeyDown,
            className: cn
        }

        return (
            <Autosuggest 
                suggestions={this.props.suggestions}
                getSuggestionValue={this.getSuggestionValue}
                onSuggestionsUpdateRequested={this.onUpdate}
                renderSuggestion={this.renderSuggestion}
                inputProps={inputProps} />
        )
    }
}


InputAutocompleteUI.propTypes = {
    disabled: PropTypes.bool,
    name: PropTypes.string.isRequired,
    // pass value to parent
    onUpdate: PropTypes.func.isRequired,
    placeholder: PropTypes.string,
    suggestions: PropTypes.arrayOf(
        PropTypes.shape({
            id: PropTypes.oneOfType([
                PropTypes.string,
                PropTypes.number
            ]),
            value: PropTypes.string
        })
    ).isRequired,
    type: PropTypes.string,
}
