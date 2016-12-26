import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'


export default class NotFoundPageComponent extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }

    render(){
        return (
            <div>{'NotFoundPageComponent'}</div>
        )
    }
}

NotFoundPageComponent.propTypes = {
}

