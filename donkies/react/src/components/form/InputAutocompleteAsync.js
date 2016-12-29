import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import { apiCall2, INSTITUTIONS_SUGGEST_URL } from 'services/api'
import InputAutocompleteUI from './ui/InputAutocompleteUI'


/**
 * Component with static suggestions.
 * Pass suggestions to InputAutocompleteUI and
 * after getting value filter suggestions and send them back
 * to UI component.
 *
 * @param {string} url - API endpoint url that receives 
 *                       "value" in GET param for filtering suggestions and
 *                       returns array of objects: {id: ..., value: ...}.
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

export default class InputAutocompleteAsync extends Component{
    static get defaultProps() {
        return {
            isAuth: true,
            onFail: null,
            onSuccess: null
        }
    }

    constructor(props){
        super(props)
        autoBind(this)
    }

    componentWillMount(){
        this.setState({
            suggestions: [],
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

    async sendRequest(value) {
        let {isAuth, url} = this.props
        url = url + '?value=' + encodeURI(value)

        let response = await apiCall2(url, isAuth) 
        let arr = await response.json()

        let map = this.getMap(arr)
         let id = map.get(value)
         id = id || ''

        if (id === undefined || id === null || id === ''){
            this.props.onFail && this.props.onFail()
        } else {
            this.props.onSuccess && this.props.onSuccess(id, value)
        }

        this.setState({suggestions: arr, hiddenInputValue: id})
    }

    onUpdate(value){
        this.sendRequest(value)
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


InputAutocompleteAsync.propTypes = {
    disabled: PropTypes.bool,
    isAuth: PropTypes.bool,
    name: PropTypes.string.isRequired,
    onFail: PropTypes.func,
    onSuccess: PropTypes.func,
    placeholder: PropTypes.string,
    type: PropTypes.string,
    url: PropTypes.string
}





