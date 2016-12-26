import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import { MainMenu } from 'components'


export default class Sidebar extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }

    render(){
        return (
            <aside id="sidebar" className="sidebar c-overflow">
                <div className="s-profile">
                    <a>
                        <div className="sp-pic">
                            <img src="img/demo/profile-pics/1.jpg" alt="" />
                        </div>

                        <div className="sp-info">
                            {'Maldina'}
                        </div>
                    </a>
                </div>

                <MainMenu />

            </aside>
        )
    }
}


Sidebar.propTypes = {
}

