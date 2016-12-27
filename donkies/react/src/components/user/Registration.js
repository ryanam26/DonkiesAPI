import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import { Link } from 'react-router'
import autoBind from 'react-autobind'
import { navigate, registration, setFormErrors } from 'actions'
import { Alert, Checkbox, ErrorBlock, Input } from 'components'
import { formToObject } from 'services/helpers'


/**
 * js/app.js had method that automatically removes "toggled" class
 * from lc-block and div started to be invisible.
 * Removed this method from app.js
 */
class Registration extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }

    componentWillMount(){
        if (this.props.isAuthenticated){
            this.props.navigate('/')
        }
    }

    componentWillReceiveProps(nextProps){
        if (nextProps.isAuthenticated)
            nextProps.navigate('/')
        
        if (nextProps.successMessage !== null){
            this.refs.form.reset()
        }
    }

    componentWillUnmount(){
        this.props.setFormErrors('clear', null)   
    }

    onSubmit(e){
        e.preventDefault()
        this.props.setFormErrors('clear', null)
        
        let form = formToObject(e.target)
        this.props.registration(form)
    }


    render(){
        const { errors, successMessage } = this.props
        
        return (
            <div className="login-content">
                <div ref="block" className="lc-block toggled">
                    <div className="lcb-form">
                        
                        <form ref="form" onSubmit={this.onSubmit} target="">
                        <Input
                            name="first_name"
                            wrapperClass="input-group m-b-20"
                            zmdi="zmdi-account"
                            placeholder="First name"
                            errors={errors} />

                        <Input
                            name="last_name"
                            wrapperClass="input-group m-b-20"
                            zmdi="zmdi-account"
                            placeholder="Last name"
                            errors={errors} />

                        <Input
                            name="email"
                            wrapperClass="input-group m-b-20"
                            zmdi="zmdi-email"
                            placeholder="Email Address"
                            errors={errors} />

                        <Input
                            name="password"
                            type="password"
                            wrapperClass="input-group m-b-20"
                            zmdi="zmdi-male"
                            placeholder="Password"
                            errors={errors} />

                        <button
                            type="submit"
                            href="#"
                            className="btn btn-login btn-success btn-float">
                            
                            <i className="zmdi zmdi-check" />
                        </button>

                        {errors && <ErrorBlock errors={errors} />}
                        
                        </form>

                        {successMessage && 
                            <Alert
                                type="success"
                                showClose={false}
                                value={successMessage} />}

                    </div>

                    <div className="lcb-navigation">
                        <Link
                            to="/login"
                            data-ma-block="#l-login">

                            <i className="zmdi zmdi-long-arrow-right" />
                             <span>{'Sign in'}</span>
                        </Link>

                        <Link
                            to="/forgot_password"
                            data-ma-block="#l-forget-password">
                            <i>{'?'}</i> <span>{'Forgot Password'}</span>
                        </Link>
                    </div>
                </div>
            </div>
        )
    }
}

Registration.propTypes = {
    errors: PropTypes.object,
    isAuthenticated: PropTypes.bool,
    navigate: PropTypes.func,
    registration: PropTypes.func,
    setFormErrors: PropTypes.func,
    successMessage: PropTypes.string
}

const mapStateToProps = (state) => ({
    isAuthenticated: state.auth.isAuthenticated,
    errors: state.formErrors.registration,
    successMessage: state.auth.registrationSuccessMessage
})

export default connect(mapStateToProps, {
    navigate,
    registration,
    setFormErrors
})(Registration)