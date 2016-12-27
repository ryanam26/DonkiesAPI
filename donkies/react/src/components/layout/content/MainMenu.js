import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import { Link } from 'react-router'
import autoBind from 'react-autobind'
import classNames from 'classnames'
import { setActiveMenu } from 'actions'


class MainMenu extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }

    getMenu(){
        return [
            {url: '/', name: 'Dashboard', className: 'zmdi-home'},
            {url: '/accounts', name: 'Accounts', className: 'zmdi-money'},
            {url: '/settings', name: 'Settings', className: 'zmdi-settings'},
            {url: '/user_profile', name: 'Profile', className: 'zmdi-male'}
        ]
    }

    onClick(url){
        this.props.setActiveMenu(url)
    }

    render(){
        const { activeUrl } = this.props

        return (
            <ul className="main-menu">
                {this.getMenu().map((obj, index) => {
                    const cnActive = classNames({'active': activeUrl === obj.url})
                    const cnZmdi = classNames('zmdi', obj.className)

                    return (
                        <li key={index} className={cnActive}>
                            <Link onClick={this.onClick.bind(null, obj.url)} to={obj.url}>
                                <i className={cnZmdi} />
                                {' '}{obj.name}
                            </Link>
                        </li>                        
                    )     
                })}
            </ul>
        )
    }
}


MainMenu.propTypes = {
    activeUrl: PropTypes.string,
    setActiveMenu: PropTypes.func
}

const mapStateToProps = (state) => ({
    activeUrl: state.menu.activeUrl
})

export default connect(mapStateToProps, {
    setActiveMenu
})(MainMenu)
