import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import classNames from 'classnames'
import { alertRemove } from 'actions'


class Alert extends Component{
    static get defaultProps() {
        return {
            index: 0,
            showClose: false
        }
    }

    constructor(props){
        super(props)
        this.onClick = this.onClick.bind(this)
    }

    onClick(e){
        this.props.alertRemove(this.props.value)
    }

    render(){
        const {type, value, index, showClose} = this.props

        if (!value)
            return null
        
        const classType = 'alert-' + type

        return (
            <div className={classNames('alert', classType, 'alert-close', 'alert-dismissible')} role="alert">
                {showClose &&
                    <button onClick={this.onClick} type="button" className="close" aria-label="Close">
                        <span aria-hidden="true">{'\u00d7'}</span>
                    </button>}
                {value}
            </div>
        )
    }
}

Alert.propTypes = {
    alertRemove: PropTypes.func,
    index: PropTypes.number,
    showClose: PropTypes.bool,
    type: PropTypes.oneOf(['info', 'success', 'warning', 'danger']),
    value: PropTypes.string
}


export default connect(null, {
  alertRemove
})(Alert)
