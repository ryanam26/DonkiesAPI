import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'


/**
 * Button that used with Input2
 */
export default class Button2 extends Component{
    static get defaultProps() {
        return {
            className: 'btn btn-primary btn-sm waves-effect',
            disabled: false,
            onClick: null,
            type: 'submit',
            text: 'submit',
            wrapperClass: 'col-sm-offset-4 col-sm-8'
        }
    }

    constructor(props){
        super(props)
        autoBind(this)
    }

    render(){
        const {wrapperClass, text, ...btnProps } = this.props

        return (
            <div className="form-group">
                <div className={wrapperClass}>
                    <button {...btnProps}>{text}</button>
                </div>
            </div>
        )
    }
}


Button2.propTypes = {
    className: PropTypes.string,
    disabled: PropTypes.bool,
    onClick: PropTypes.func,
    text: PropTypes.string,
    type: PropTypes.string,
    wrapperClass: PropTypes.string
}
