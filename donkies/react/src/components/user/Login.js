import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import { Link } from 'react-router'
import autoBind from 'react-autobind'
import { Checkbox, Input } from 'components'


export default class LoginComponent extends Component{
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
                            name="password"
                            type="password"
                            wrapperClass="input-group m-b-20"
                            zmdi="zmdi-male"
                            placeholder="Password" />

                        <Checkbox
                            title="Keep me signed in" />

                        <a href="#" className="btn btn-login btn-success btn-float">
                            <i className="zmdi zmdi-arrow-forward" />
                        </a>
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

LoginComponent.propTypes = {
}



