import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import { AddBank } from 'components' 


export default class AddBankPage extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }

    render(){
        return (
            <AddBank />
        )
    }
}


AddBankPage.propTypes = {
}

