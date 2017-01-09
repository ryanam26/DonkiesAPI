import React, {Component, PropTypes} from 'react'
import { LoginFacebook } from 'components'


/**
 * Not auth page
 */
export default class LoginFacebookPage extends Component{
    constructor(props){
        super(props)
    }

    render(){
        return <LoginFacebook location={this.props.location} />
    }
}

LoginFacebookPage.propTypes = {
    location: PropTypes.object
}
