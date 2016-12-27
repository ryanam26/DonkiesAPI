import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'


export default class Loading extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }

    render(){
        return (
            <div className="page-loader">
                <div className="preloader pls-blue">
                    <svg className="pl-circular" viewBox="25 25 50 50">
                        <circle className="plc-path" cx="50" cy="50" r="20" />
                    </svg>

                    <p>{'Please wait...'}</p>
                </div>
            </div>
        )
    }
}


Loading.propTypes = {
}
