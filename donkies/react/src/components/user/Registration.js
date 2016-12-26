
import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import { Link } from 'react-router'
import autoBind from 'react-autobind'
import { Checkbox, Input } from 'components'


export default class Registration extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }

    render(){
        return (
            <div className="login-content">
                <div className="lc-block toggled">
                    <div className="lcb-form">
                        
                        <Input
                            name="username"
                            wrapperClass="input-group m-b-20"
                            zmdi="zmdi-account"
                            placeholder="Username" />

                        <Input
                            name="email"
                            wrapperClass="input-group m-b-20"
                            zmdi="zmdi-email"
                            placeholder="Email Address" />

                        <Input
                            name="password"
                            type="password"
                            wrapperClass="input-group m-b-20"
                            zmdi="zmdi-male"
                            placeholder="Password" />

                        <a href="#" className="btn btn-login btn-success btn-float">
                            <i className="zmdi zmdi-check" />
                        </a>
                    </div>

                    <div className="lcb-navigation">
                        <Link
                            to="/login"
                            data-ma-action="login-switch"
                            data-ma-block="#l-login">

                            <i className="zmdi zmdi-long-arrow-right" />
                             <span>{'Sign in'}</span>
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

Registration.propTypes = {
}
