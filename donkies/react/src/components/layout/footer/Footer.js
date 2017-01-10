import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import { Link } from 'react-router'
import autoBind from 'react-autobind'


export default class Footer extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }

    render(){
        return (
            <footer id="footer">
                {'Copyright \u00A9 2016 Donkies.co'}

                <ul className="f-menu">
                    <li><Link to="/">{'Home'}</Link></li>
                    <li><Link to="/dashboard">{'Dashboard'}</Link></li>
                    <li><Link to="/reports">{'Reports'}</Link></li>
                    <li><Link to="/support">{'Support'}</Link></li>
                    <li><Link to="/contact">{'Contact'}</Link></li>
                </ul>
            </footer>
        )
    }
}


Footer.propTypes = {
}
