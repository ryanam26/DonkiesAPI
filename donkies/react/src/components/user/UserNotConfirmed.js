import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import { Link } from 'react-router'
import { apiCall2, RESEND_REG_CONFIRMATION_URL } from 'services/api'
import { Alert } from 'components'


class UserNotConfirmed extends Component{
    constructor(props){
        super(props)
        autoBind(this)

        this.state = {
            isProcessing: false,
            message: null
        }
    }

    onClickResend(){
        this.sendRequest()
    }

    async sendRequest() {
        this.setState({isProcessing: true})
        let response = await apiCall2(RESEND_REG_CONFIRMATION_URL, true) 
        let data = await response.json()
        this.setState({message: data.message})
    }

    render(){
        const { isProcessing, message } = this.state

        const text = `
            We sent you email with verification link.
            Please click the link to confirm your account.
            If you didn't receive verification email, you can resend the link
            using the button below.
        `

        return (
            <div className="login-content">
                <div className="lc-block lc-block-alt toggled">
                    <Alert type="danger" value="Your account is not confirmed." />
                    
                    <div className="lcb-form">
                        <p>{text}</p>

                        {!isProcessing &&
                            <Link 
                                onClick={this.onClickResend}
                                className="btn">

                                {'Resend verification link'}
                            </Link>
                        }
                    </div>

                    {message && 
                            <Alert type="success" value={message} />}
                </div>
            </div>
        )
    }
}


UserNotConfirmed.propTypes = {
}

const mapStateToProps = (state) => ({
})

export default connect(mapStateToProps, {
})(UserNotConfirmed)