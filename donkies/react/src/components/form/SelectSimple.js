import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'


/**
 * Options passes to Select is array of objects.
 * Each object has properties: text and value.
 */
export default class SelectSimple extends Component{
    static get defaultProps() {
        return {
            onChange: null,
            value: ''
        }
    }

    constructor(props){
        super(props)
        autoBind(this)

        this.state = {
            wrapperClassName: 'fg-line'
        }
    }

    onFocus(e){
        this.setState({wrapperClassName: 'fg-line fg-toggled'})
    }

    onBlur(e){
        this.setState({wrapperClassName: 'fg-line'})
    }

    onChange(e){
        if (this.props.onChange !== null){
            this.props.onChange(e.target.value)    
        }
    }

    render(){
        const { wrapperClassName } = this.state
        const { name, options, value } = this.props

        return (
            <div className={wrapperClassName}>
                <div className="select">
                    <select
                        defaultValue={value}
                        onChange={this.onChange}
                        onFocus={this.onFocus}
                        onBlur={this.onBlur}
                        name={name}
                        className="form-control">
                    
                    {options.map((obj, index) => {
                        return <option key={index} value={obj.value}>{obj.text}</option>
                    })}

                </select>
                </div>
            </div>
        )
    }
}


SelectSimple.propTypes = {
    name: PropTypes.string.isRequired,
    onChange: PropTypes.func,
    options: PropTypes.arrayOf(
        PropTypes.shape({
            value: PropTypes.any,
            text: PropTypes.any
        })
    ).isRequired,
    value: PropTypes.any
}