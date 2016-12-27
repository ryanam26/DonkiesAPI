import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import { Input } from 'components'


class UserProfile extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }

    render(){
        return (
            <div>
                {'UserProfile'}
                <Input
                    name="email" />
            </div>
        )
    }
}


UserProfile.propTypes = {

}

const mapStateToProps = (state) => ({

})

export default connect(mapStateToProps, {

})(UserProfile)