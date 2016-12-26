
import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import { Link } from 'react-router'
import autoBind from 'react-autobind'
import { Checkbox, Input } from 'components'


export default class ForgotPassword extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }



    render(){
        return (
            <div className="login-content">
                <div className="lc-block toggled">
                    <div className="lcb-form">
                        <p className="text-left">
                            {'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla eu risus. Curabitur commodo lorem fringilla enim feugiat commodo sed ac lacus.'}
                        </p>

                        <Input
                            name="email"
                            wrapperClass="input-group m-b-20"
                            zmdi="zmdi-email"
                            placeholder="Email Address" />

                        <a href="#" className="btn btn-login btn-success btn-float">
                            <i className="zmdi zmdi-check" />
                        </a>
                    </div>

                    <div className="lcb-navigation">
                        <Link
                            to="/login"
                            data-ma-block="#l-login">

                            <i className="zmdi zmdi-long-arrow-right" />
                             <span>{'Sign in'}</span>
                        </Link>

                        <Link
                            to="/registration"
                            data-ma-block="#l-register">
                            
                            <i className="zmdi zmdi-plus" />
                            <span>{'Register'}</span>
                        </Link>
                    </div>
                </div>
            </div>
        )
    }
}

ForgotPassword.propTypes = {
}
