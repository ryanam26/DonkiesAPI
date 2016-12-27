import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import { MainMenu } from 'components'


class Sidebar extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }

    render(){
        const { user } = this.props

        return (
            <aside id="sidebar" className="sidebar c-overflow">
                <div className="s-profile">
                    <a>
                        <div className="sp-pic">
                            <img src="img/demo/profile-pics/1.jpg" alt="" />
                        </div>

                        <div className="sp-info">
                            {user.first_name}{' '}{user.last_name}
                        </div>
                    </a>
                </div>

                <MainMenu />

            </aside>
        )
    }
}


Sidebar.propTypes = {
    user: PropTypes.object
}


const mapStateToProps = (state) => ({
    user: state.user.item
})

export default connect(mapStateToProps, {
})(Sidebar)
