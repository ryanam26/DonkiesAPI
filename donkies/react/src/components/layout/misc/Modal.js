import React, {Component, PropTypes} from 'react'
import classNames from 'classnames'


/**
 * onClickClose - passed from parent (show/hide controls from parent).
 * footer - additional node to footer.
 */
class Modal extends Component{
    static get defaultProps() {
        return {
            footer: null
        }
    }

    constructor(props){
        super(props)
        this.onClickClose = this.onClickClose.bind(this)
    }

    onClickClose(){
        this.props.onClickClose()
    }

    render(){
        const { children, footer, title, visible } = this.props

        let style = visible ? {'display': 'block', 'paddingRight': '15px'} : {'display': 'none'}
        
        let cn = classNames('modal fade', {'in': visible})

        return (
            <div className={cn} style={style}>
                <div className="modal-dialog">
                    <div className="modal-content">
                        <div className="modal-header">
                            <h4 className="modal-title">{title}</h4>
                        </div>
                        <div className="modal-body">
                            {children}
                        </div>
                        <div className="modal-footer">
                            {footer}

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
    footer: PropTypes.node,
    onClickClose: PropTypes.func,
    title: PropTypes.string,
    visible: PropTypes.bool
}

export default Modal


