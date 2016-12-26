import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import { Link } from 'react-router'
import autoBind from 'react-autobind'


export default class MainMenu extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }

    render(){
        return (
            <ul className="main-menu">
                <li className="active">
                    <Link to="/dashboard">
                        <i className="zmdi zmdi-home" />
                        {' Dashboard'}
                    </Link>
                </li>

                <li>
                    <Link to="/accounts">
                        <i className="zmdi zmdi-money" />
                        {' Accounts'}
                    </Link>
                </li>

                <li>
                    <Link to="/settings">
                        <i className="zmdi zmdi-settings" />
                        {' Settings'}
                    </Link>
                </li>
            </ul>
        )
    }
}


MainMenu.propTypes = {
}

