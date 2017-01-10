import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import { Link } from 'react-router'
import { Transactions } from 'components'



export default class TransactionsPage extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }

    render(){
        const { location } = this.props

        return (
            <Transactions location={location} />
        )
    }
}


TransactionsPage.propTypes = {
    location: PropTypes.object
}
