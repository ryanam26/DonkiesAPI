import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import classNames from 'classnames'


/**
 * isContentToBody = true - children placed to body
 * isContentToBody = false - children placed to header
 */
export default class CardSimple extends Component{
    static get defaultProps() {
        return {
            isContentToBody: true,
            cardClass: 'bgm-teal',
            headerClass: '',
            smallHeader: null
        }
    }

    constructor(props){
        super(props)
        autoBind(this)
    }

    render(){
        const {
            cardClass,
            children,
            header,
            headerClass,
            isContentToBody,
            smallHeader } = this.props 
        const cn = classNames('card-header', cardClass)

        return (
            <div className="card">
                <div className={cn}>
                    <h2 className={headerClass}>
                        {header}
                        {' '}{smallHeader && <small>{smallHeader}</small>}
                    </h2>
                    {!isContentToBody && children}
                </div>

                <div className="card-body m-t-0">
                    {isContentToBody && children}
                </div>
            </div>
        )
    }
}


CardSimple.propTypes = {
    cardClass: PropTypes.string,
    children: PropTypes.oneOfType([
        PropTypes.array,
        PropTypes.object
    ]),
    header: PropTypes.string.isRequired,
    headerClass: PropTypes.string,
    isContentToBody: PropTypes.bool,
    smallHeader: PropTypes.string
}
