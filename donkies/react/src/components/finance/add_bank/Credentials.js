import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'


/**
 * Second step of add bank form.
 * On init fetches credentials for institution.
 * Then user submit credentials.
 * Then fetches server until it get completed status of member
 * and send callback to parent with updated status.
 *
 * @param {object} institution: {id: ..., name: ...}
 * @param {func} onUpdateMemberStatus
 */ 
class Credentials extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }

    render(){
        return (
            <div>{'Credentials'}</div>
        )
    }
}


Credentials.propTypes = {
    institution: PropTypes.object,
    onUpdateMemberStatus: PropTypes.func

}

const mapStateToProps = (state) => ({
})

export default connect(mapStateToProps, {
})(Credentials)