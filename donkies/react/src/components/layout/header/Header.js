import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import { HOME_PAGE_URL } from 'store/configureStore'
import { logout } from 'actions'


class Header extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }

    onClickLogout(e){
        e.preventDefault()
        this.props.logout()
        location.reload()
    }

    render(){
        return (
            <header id="header" className="clearfix" data-ma-theme="blue">
                <ul className="h-inner">
                    <li className="hi-trigger ma-trigger" data-ma-action="sidebar-open" data-ma-target="#sidebar">
                        <div className="line-wrap">
                            <div className="line top" />
                            <div className="line center" />
                            <div className="line bottom" />
                        </div>
                    </li>

                    <li className="hi-logo hidden-xs">
                        <a href={HOME_PAGE_URL}>{'Donkies'}</a>
                    </li>

                    <li className="pull-right">
                        <ul className="hi-menu">
                            <li>
                                <a onClick={this.onClickLogout} href="#" title="Logout">
                                    <i className="him-icon zmdi zmdi-power" />
                                </a>
                            </li>
                        </ul>
                    </li>
                </ul>
            </header>
        )
    }
}


Header.propTypes = {
    logout: PropTypes.func
}

const mapStateToProps = (state) => ({
})

export default connect(mapStateToProps, {
    logout
})(Header)
