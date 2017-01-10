import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'


/**
 * Select without wrappers.
 */
export default class SelectClean extends Component{
    static get defaultProps() {
        return {
            className: '',
            onChange: null
        }
    }

    constructor(props){
        super(props)
        autoBind(this)
    }

    onChange(e){
        if (this.props.onChange !== null){
            this.props.onChange(e.target.value)    
        }
    }

    render(){
        const { className, name, options } = this.props

        return (
            <select
                onChange={this.onChange}
                onFocus={this.onFocus}
                onBlur={this.onBlur}
                name={name}
                className={className}>
            
                {options.map((obj, index) => {
                    return <option key={index} value={obj.value}>{obj.text}</option>
                })}

            </select>
                
        )
    }
}


SelectClean.propTypes = {
    className: PropTypes.string,
    name: PropTypes.string.isRequired,
    onChange: PropTypes.func,
    options: PropTypes.arrayOf(
        PropTypes.shape({
            value: PropTypes.any,
            text: PropTypes.any
        })
    ).isRequired
}