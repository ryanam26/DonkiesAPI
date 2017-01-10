import React, {Component, PropTypes} from 'react'
import classNames from 'classnames'


class Modal extends Component{
    constructor(props){
        super(props)
        this.onClickClose = this.onClickClose.bind(this)
    }

    onClickClose(){
        this.props.onClickClose()
    }

    render(){
        const {title, visible, children} = this.props

        let style = visible ? {'display': 'block', 'paddingRight': '15px'} : {'display': 'none'}
        
        let cn = classNames('modal fade', {'in': visible})

        return (
            <div className={cn} role="dialog" aria-hidden="true" style={style}>
                <div className="modal-dialog">
                    <div className="modal-content">
                        <div className="modal-header">
                            <h4 className="modal-title">{title}</h4>
                        </div>
                        <div className="modal-body">
                            {children}
                        </div>
                        <div className="modal-footer">
                            <button
                                onClick={this.onClickClose}
                                type="button"
                                className="btn btn-link waves-effect"
                                data-dismiss="modal">
                                {'Close'}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        )
    }
}

Modal.propTypes = {
    children: PropTypes.node,
    onClickClose: PropTypes.func,
    size: PropTypes.string,
    title: PropTypes.string,
    visible: PropTypes.bool
}

export default Modal


