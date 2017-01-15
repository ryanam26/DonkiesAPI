import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'


export default class LoadingInline extends Component{
    static get defaultProps() {
        return {
            message: null,
            radius: 20
        }
    }

    constructor(props){
        super(props)
        autoBind(this)
    }

    render(){
        const { message, radius } = this.props

        return (
            <wrap>
                <div className="preloader pls-blue">
                    <svg className="pl-circular" viewBox="25 25 50 50">
                        <circle className="plc-path" cx="50" cy="50" r={radius} />
                    </svg>
                </div>

                {message && <p>{message}</p>}
            </wrap>
        )
    }
}


LoadingInline.propTypes = {
    message: PropTypes.string,
    radius: PropTypes.number
}

