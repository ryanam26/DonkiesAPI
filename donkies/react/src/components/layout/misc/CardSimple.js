import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'


export default class CardSimple extends Component{
    static get defaultProps() {
        return {
            smallHeader: null
        }
    }

    constructor(props){
        super(props)
        autoBind(this)
    }

    render(){
        const { children, header, smallHeader } = this.props 

        return (
            <div className="card">
                <div className="card-header bgm-teal">
                    <h2>{header} {smallHeader && <small>{smallHeader}</small>}</h2>
                    
                </div>

                <div className="card-body m-t-0">
                    {children}
                </div>
            </div>
        )
    }
}


CardSimple.propTypes = {
    children: PropTypes.object,
    header: PropTypes.string.isRequired,
    smallHeader: PropTypes.string
}

