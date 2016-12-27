import React, {Component, PropTypes} from 'react'
import { RegistrationConfirm } from 'components'


/**
 * Not auth page
 */
export default class RegistrationConfirmPage extends Component{
    constructor(props){
        super(props)
    }

    render(){
        const { location } = this.props
        return <RegistrationConfirm query={location.query} />
    }
}


RegistrationConfirmPage.propTypes = {
    location: PropTypes.object
}
