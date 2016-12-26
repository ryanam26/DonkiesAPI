import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'


export default class Checkbox extends Component{
    static get defaultProps() {
        return {
            disabled: false
        }
    }

    constructor(props){
        super(props)
        autoBind(this)
    }

    onClick(){
        this.props.onClick()
    }
    
    render(){
        const { title } = this.props

        return (
            <div className="checkbox" onClick={this.onClick}>
                <label>
                    <input
                        type="checkbox"
                        onChange={this.onClick}
                        checked={this.props.checked}
                        disabled={this.props.disabled} />
                    <i className="input-helper" />
                    {title}
                </label>
            </div>
        )
    }
}


Checkbox.propTypes = {
    checked: PropTypes.bool,
    disabled: PropTypes.bool,
    onClick: PropTypes.func,
    title: PropTypes.string
}


