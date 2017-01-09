import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import { Link } from 'react-router'
import autoBind from 'react-autobind'
import { loginFacebook, navigate, setFormErrors } from 'actions'
import { ErrorBlock, Loading } from 'components'



class LoginFacebook extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }

    /**
     * In query params get "code" and send request to API.
     */
    componentWillMount(){
        if (this.props.auth.isAuthenticated){
            this.props.navigate('/')
            return
        }
        
        const params = this.props.location.query
        if (!params.hasOwnProperty('code')){
            this.props.navigate('/login')
            return
        }
        this.props.loginFacebook(params.code)
    }

    componentWillReceiveProps(props){
        if (props.auth.isAuthenticated){
            props.navigate('/')
        }
    }

    componentWillUnmount(){
        this.props.setFormErrors('clear', null)   
    }

    render(){
        const { errors } = this.props

        if (!this.props.auth.isAuthenticated && !errors){
            return <Loading />    
        }

        return (
            <div className="login-content">
                <div className="lc-block toggled">
                    
                    <div className="lcb-form">
                        {errors && <ErrorBlock errors={errors} />}

                        <div>
                            <Link to="/login">{'Back to login'}</Link> 
                        </div>
                    </div>
                   
                </div>
            </div>
        )
    }
}

LoginFacebook.propTypes = {
    auth: PropTypes.object,
    errors: PropTypes.object,
    location: PropTypes.object,
    loginFacebook: PropTypes.func,
    navigate: PropTypes.func,
    setFormErrors: PropTypes.func
}

const mapStateToProps = (state) => ({
    auth: state.auth,
    errors: state.formErrors.login
})

export default connect(mapStateToProps, {
    loginFacebook,
    navigate,
    setFormErrors
})(LoginFacebook)
