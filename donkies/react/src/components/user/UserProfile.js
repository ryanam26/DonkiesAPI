import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'


class UserProfile extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }

    render(){
        return (
            <div>{'UserProfile'}</div>
        )
    }
}


UserProfile.propTypes = {

}

const mapStateToProps = (state) => ({

})

export default connect(mapStateToProps, {

})(UserProfile)