import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import { apiCall2, apiCall3, CREDENTIALS_BY_ID_URL, MEMBERS_URL } from 'services/api'
import { formToObject } from 'services/helpers'
import { Button2, Input2, LoadingInline } from 'components'


/**
 * Third step of add bank form.
 * If member has status challenge - we need to submit answers.
 * Database will have will have challenges row(s) for member. 
 *
 * Flow:
 * 1) Request challenges list from API.
 * 2) Submit answers to server
 * 3) Request server for every 5 seconds until completed status
 * 4) As soon as member is completed, call onCompleteMember(member)
 *    exactly the same scenario as Credentials component.
 */


class Challenges extends Component{
    constructor(props){
        super(props)
        autoBind(this)

        this.state = {
            isFetchingMember: false
        }
    }

    onSubmit(e){
        e.preventDefault()
    }

    /**
     * Submit to server user's filled challenges.
     */
    async submitChallenges(data){
        
    }

    /**
     * Request MemberDetail endpoint every 5 seconds until 
     * get completed status.
     */
    async fetchMemberUntilCompleted(member){
        const url = MEMBERS_URL + '/' + member.identifier

        let response = await apiCall2(url, true) 
        member = await response.json()

        if (member.status_info.is_completed){
            this.setState({isFetchingMember: false})
            this.props.onCompleteMember(member)
        } else {
            setTimeout(() => this.fetchMemberUntilCompleted(member), 5000)
        }
    }

    render(){
        return null
    }
}


Challenges.propTypes = {
    member: PropTypes.object,
    onCompleteMember: PropTypes.func
}

const mapStateToProps = (state) => ({
})

export default connect(mapStateToProps, {
})(Challenges)