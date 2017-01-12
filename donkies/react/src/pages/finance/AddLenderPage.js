import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import { AddAccount } from 'components' 


export default class AddLenderPage extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }

    render(){
        return (
            <AddAccount />
        )
    }
}


AddLenderPage.propTypes = {
}

