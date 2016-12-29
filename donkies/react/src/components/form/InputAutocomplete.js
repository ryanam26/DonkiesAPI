import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import InputAutocompleteUI from './ui/InputAutocompleteUI'


/**
 * Component with static suggestions.
 * Pass suggestions to InputAutocompleteUI and
 * after getting value filter suggestions and send them back
 * to UI component.
 *
 * @param {array} suggestions - array of objects: {id: ..., value: ...}.
                  Suggestions that come from props go to state.
 *
 * @param {func} onSuccess - callback, when suggestion selected.
 * @param {func} onFail - callback, when incorrect value in input. 
 *
 * We use 2 inputs.
 * First input: that uses text ("value") as value and works with suggestions.
 * Second hidden input: that uses "id" as value.
 * Hidden input name called: <name>_id
 * If we don't need id, we can pass id=value.
 * This is implemented, because we often need id instead of text.
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
            suggestionsAll: arr,
            map: this.getMap(arr),
            hiddenInputValue: ''
        })   
    }

    get hiddenInputName(){
        const { name } = this.props
        return name + '_id'
    }

    /**
     * Map value to id.
     * @param {array} - array of objects {id:..., value:...}
     * @return {map}
     */
    getMap(arr){
        let m = new Map()
        for (let obj of arr){
            m.set(obj.value, obj.id)
        }
        return m
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
        const { map } = this.state
        let id = map.get(value)
        id = id || ''

        if (id === undefined || id === null || id === ''){
            this.props.onFail && this.props.onFail()
        } else {
            this.props.onSuccess && this.props.onSuccess(id, value)
        }

        this.setState({hiddenInputValue: id})
    }

    render(){
        const { hiddenInputValue } = this.state
        const { name, disabled, placeholder, type } = this.props
        const inputProps = {name, disabled, placeholder, type}


        return (
            <wrap>
                <input
                    type="hidden"
                    name={this.hiddenInputName}
                    value={hiddenInputValue} />
                
                <InputAutocompleteUI
                    suggestions={this.state.suggestions}
                    onUpdate={this.onUpdate}
                    {...inputProps} />
            </wrap>
        )
    }
}


InputAutocomplete.propTypes = {
    disabled: PropTypes.bool,
    name: PropTypes.string.isRequired,
    onFail: PropTypes.func,
    onSuccess: PropTypes.func,
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
