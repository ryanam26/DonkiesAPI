import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import { CreateFundingSource } from 'components'



export default class CreateFundingSourcePage extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }

    render(){
        const { location } = this.props

        return (
            <CreateFundingSource location={location} />
        )
    }
}


CreateFundingSourcePage.propTypes = {
    location: PropTypes.object
}
