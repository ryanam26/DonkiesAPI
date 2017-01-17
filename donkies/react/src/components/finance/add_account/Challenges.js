import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import {
    apiCall2,
    apiCall3,
    MEMBERS_URL,
    MEMBERS_RESUME_URL } from 'services/api'
import { formToObject } from 'services/helpers'
import { Button2, Input2, LoadingInline } from 'components'


/**
 * Third step of add bank form.
 * If member has status challenge - we need to submit answers.
 * "member" object that has status CHALLENGED and passed to
 * this component, has "challenges" array.
 *
 * Flow:
 * 1) Render form with challenges (on init component).
 * 1) Submit user answers (challenges) to server.
 * 3) Request server for every 5 seconds until completed status.
 * 4) As soon as member is completed, call onCompleteMember(member)
 *    exactly the same scenario as Credentials component.
 */

class Challenges extends Component{
    constructor(props){
        super(props)
        autoBind(this)

        this.state = {
            errorSubmit: null,
            isFetchingMember: false
        }
    }

    /**
     * Process form.
     */
    onSubmit(e){
        e.preventDefault()
        this.setState({errorSubmit: null})

        const form = formToObject(e.target)
        const data = {challenges: []}
        
        for (let key in form){
            if (key.length === 0){
                continue
            }

            if (form[key].trim().length === 0){
                return
            }

            let obj = {guid: key, value: form[key].trim()}
            data.challenges.push(obj)
        }
        this.submitChallenges(data)
    }

    /**
     * Submit to server user's filled challenges.
     * (resume member)
     */
    async submitChallenges(data){
        const { member } = this.props
        const url = MEMBERS_RESUME_URL + '/' + member.identifier

        let response = await apiCall3(url, data, true) 
        if (response.status === 204){
            this.setState({'isFetchingMember': true})
            this.fetchMemberUntilCompleted(member)
        } else {
            this.setState({errorSubmit: 'Server responded with error.'})
        }
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
        const { isFetchingMember, errorSubmit } = this.state
        const { member } = this.props

        if (isFetchingMember){
            return <LoadingInline />
        }
        
        return (
            <div>
                <form onSubmit={this.onSubmit}>
                    {member.challenges.map((obj, index) => {
                        const type = obj.type.toLowerCase() === 'password' ? 'password' : 'text'
                        return (
                            <Input2
                                key={index}
                                type={type}
                                name={obj.guid}
                                label={obj.label}
                                placeholder={obj.label} />
                        )                                
                    })}
                
                    <Button2 />

                    {errorSubmit && <p className="custom-errors">{errorSubmit}</p>}
                </form>
            </div>
        )
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