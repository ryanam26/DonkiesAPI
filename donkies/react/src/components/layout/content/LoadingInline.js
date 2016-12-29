import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'


export default class LoadingInline extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }

    render(){
        return (
            <svg className="pl-circular" viewBox="25 25 50 50">
                <circle className="plc-path" cx="50" cy="50" r="20" />
            </svg>
        )
    }
}


LoadingInline.propTypes = {
}

