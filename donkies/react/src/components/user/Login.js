import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import { Link } from 'react-router'
import autoBind from 'react-autobind'
import { HOME_PAGE_URL } from 'store/configureStore'
import { login, navigate, setFormErrors } from 'actions'
import { Checkbox, ErrorBlock, Input } from 'components'



class Login extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }

    componentWillMount(){
        if (this.props.auth.isAuthenticated){
            this.props.navigate('/')
            return
        }
    }

    componentWillReceiveProps(props){
        if (props.auth.isAuthenticated){
            props.navigate('/')
        }
    }

    componentWillUnmount(){
        this.props.setFormErrors('clear', null)   
    }

    onSubmit(e){
        e.preventDefault()
        this.props.setFormErrors('clear', null)
        
        let username = document.querySelector('[name="email"]').value.trim()
        let password = document.querySelector('[name="password"]').value.trim()

        if (username.length === 0){
            this.props.setFormErrors('login', {email: ['Please input username']})
            return
        }

        if (password.length === 0){
            this.props.setFormErrors('login', {password: ['Please input password']})
            return
        }

        this.props.login(username, password)
    }

    render(){
        const { errors } = this.props

        return (
            <div className="login-content">
                <div className="lc-block toggled">
                    <div className="lcb-form">
                        <Input
                            name="email"
                            wrapperClass="input-group m-b-20"
                            zmdi="zmdi-account"
                            placeholder="Username"
                            errors={errors} />

                        <Input
                            name="password"
                            type="password"
                            wrapperClass="input-group m-b-20"
                            zmdi="zmdi-male"
                            placeholder="Password"
                            errors={errors} />

                        <Checkbox
                            title="Keep me signed in" />

                        <a
                            href="#"
                            className="btn btn-login btn-success btn-float"
                            onClick={this.onSubmit}>
                            
                            <i className="zmdi zmdi-arrow-forward" />
                        </a>

                        {errors && <ErrorBlock errors={errors} />}

                    </div>

                    <div className="lcb-navigation">
                        <Link
                            to="/registration"
                            data-ma-action="login-switch"
                            data-ma-block="#l-register">
                            
                            <i className="zmdi zmdi-plus" />
                            <span>{'Register'}</span>
                        </Link>
                        
                        <Link
                            to="/forgot_password"
                            data-ma-action="login-switch"
                            data-ma-block="#l-forget-password">
                            <i>{'?'}</i> <span>{'Forgot Password'}</span>
                        </Link>
                    </div>
                </div>
            </div>
        )
    }
}

Login.propTypes = {
}



Login.propTypes = {
    auth: PropTypes.object,
    errors: PropTypes.object,
    location: PropTypes.object,
    login: PropTypes.func,
    navigate: PropTypes.func,
    setFormErrors: PropTypes.func
}

const mapStateToProps = (state) => ({
    auth: state.auth,
    errors: state.formErrors.login
})

export default connect(mapStateToProps, {
    login,
    navigate,
    setFormErrors
})(Login)
