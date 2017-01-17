import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import { CREDENTIALS_URL, apiCall2 } from 'services/api'
import { createUUID } from 'services/helpers'
import { growlAddRequest } from 'actions'
import { MEMBER_STATUS } from 'constants'
import { Alert } from 'components'
import Credentials from './Credentials'
import Challenges from './Challenges'
import Institution from './Institution'


/**
 * Main component that controls adding bank account.
 * Flow: 
 * 1) Select institution and set it to state. (Institution)
 * 2) Fetch credentials for institution. (Credentials)
 * 3) Submit credentials to server.
 * 4) Wait for member status.
 * 5) If member has completed status and success - show success message.
 *    and hide Credentials component.
 * 6) If member has completed status and error - show error message.
 * 7) If status is challenged, fetch challenges and resume member.
 *    (Challenges)
 * 8) Wait for status again, back to 4th step.
 *
 */
class AddAccount extends Component{
    constructor(props){
        super(props)
        autoBind(this)

        this.state = {
            institution: null,
            isInstitutionChosen: false,
            isShowCredentials: false,
            isShowChallenge: false,
            member: null,
            successMessage: null
        }
    }

    /**
     * Debug challenges to render challenges form.
     * Set state without all steps required to reach challenges.
     * When debug is required, call this method from ComponentWillMount.
     */
    debugChallenges(){
        const i = {
            id: 2,
            code: 'mxbank',
            name: 'MX Bank',
            url: 'https://www.mx.com'
        }

        const m = {
            id: 4,
            aggregated_at: '2017-01-17T19:09:49',
            challenges: [{
                guid: 'some_guid',
                label: 'What city were you born in?',
                type: 'TEXT'
            }],
            identifier: 'c97362c5f77a477abee05330bdc5e7a5',
            institution: 'mxbank',
            name: 'MX Bank',
            status: 'CHALLENGED',
            status_info: {
                is_completed: true,
                message: 'Please provide additional info.',
                name: 'CHALLENGED',
                status: 'CHALLENGED'
            },
            successfully_aggregated_at: null,

        }

        this.setState({
            institution: i,
            isInstitutionChosen: true,
            isShowCredentials: false,
            isShowChallenge: true,
            member: m
        })
    }


    /**
     * User not yet selected institution in Autocomplete.
     */
    onFailInstitution(){
        this.setState({institution: null})
    }

    /**
     * User selects institution on Autocomplete.
     */
    onSelectInstitution(id, value){
        this.setState({institution: {id, name: value}})
    }

    /**
     * User clicked button and chosen institution.
     */
    onChooseInstitution(institution){
        this.setState({
            isInstitutionChosen: true,
            institution: institution,
            isShowCredentials: true
        })
    }

    /**
     * Receives member after first submit.
     */ 
    onUpdateMember(member){
        this.setState({member: member})
    }

    /**
     * Receives member after status is completed
     */
    onCompleteMember(member){
        this.setState({
            member: member,
            isShowCredentials: false,
            isShowChallenge: false
        })

        const s = member.status_info

        if (s.name === MEMBER_STATUS.SUCCESS){
            this.setState({successMessage: s.message})
        } else if (s.name === MEMBER_STATUS.CHALLENGED){
            this.setState({isShowChallenge: true})

        } else if (s.name === MEMBER_STATUS.ERROR){
            const id = createUUID()
            this.props.growlAddRequest({
                id: id,
                message: s.message,
                'type': 'danger'
            })
        }
    }

    renderCredentials(){
        const { institution, member, isInstitutionChosen, isShowCredentials } = this.state
        if (!isInstitutionChosen || !isShowCredentials){
            return null
        }

        return (
            <Credentials
                institution={institution}
                member={member}
                onUpdateMember={this.onUpdateMember}
                onCompleteMember={this.onCompleteMember} />
        )
    }

    renderChallenges(){
        const { member, isShowChallenge } = this.state
        if (!isShowChallenge){
            return null
        }

        return (
            <Challenges
                member={member}
                onCompleteMember={this.onCompleteMember} />
        )
    }

    renderSuccess(){
        const { successMessage } = this.state
        return successMessage ? <Alert type="success" value={successMessage} /> : null
    }

    render(){
        const { institution, isInstitutionChosen } = this.state
        const { user } = this.props

        if (!user.guid){
            // Means that user has not been created yet in Atrium.
            return (
                <Alert
                    type="info"
                    showClose={false}
                    value="Your user account has not been activated to add financial account." />
            )       
        }

        return (
            <div className="card col-lg-6">

                <div className="form-horizontal">
                    <div className="card-header">
                        <h2>{'Add bank account'}</h2>
                    </div>

                    <div className="card-body card-padding">
                        <Institution
                            institution={institution}
                            onChooseInstitution={this.onChooseInstitution}
                            onFailInstitution={this.onFailInstitution}
                            onSelectInstitution={this.onSelectInstitution}
                            isInstitutionChosen={isInstitutionChosen} />

                        {this.renderCredentials()}

                        {this.renderChallenges()}

                        {this.renderSuccess()}

                    </div>
                </div>
            </div>
        )
    }
}


AddAccount.propTypes = {
    growlAddRequest: PropTypes.func,
    user: PropTypes.object
}

const mapStateToProps = (state) => ({
    user: state.user.item
})

export default connect(mapStateToProps, {
    growlAddRequest
})(AddAccount)
