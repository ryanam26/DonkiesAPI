import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import { CREDENTIALS_URL, apiCall2 } from 'services/api'
import { createUUID } from 'services/helpers'
import { growlAdd } from 'actions'
import { MEMBER_STATUS } from 'constants'
import { Alert } from 'components'
import Institution from './Institution'
import Credentials from './Credentials'


/**
 * Main component that controls adding bank account.
 * Flow: 
 * 1) Select institution and set it to state
 * 2) Fetch credentials for institution.
 * 3) Submit credentials to server.
 * 4) Wait for member status.
 * 5) If member has completed status and success - show success message.
 *    and hide Credentials component.
 * 6) If member has completed status and error - show error message.
 * 7) If status is challenged, fetch challenges and resume member.
 * 8) Wait for status again, back to 4th step.
  */
class AddBank extends Component{
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

    componentDidMount(){
        
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
    onCompletedMember(member){
        const s = member.status_info

        if (s.name === MEMBER_STATUS.SUCCESS){
            this.setState({
                isShowCredentials: false,
                successMessage: s.message
            })
        
        } else if (s.name === MEMBER_STATUS.CHALLENGED){
            this.setState({isShowCredentials: false, isShowChallenge: true})
            console.log('TODO')
        
        } else if (s.name === MEMBER_STATUS.ERROR){
            this.props.growlAdd({
                id: createUUID(),
                message: status.message,
                'type': 'danger'
            })
        }
    }

    renderCredentials(){
        const { institution, member, isInstitutionChosen } = this.state
        if (!isInstitutionChosen || !isShowCredentials){
            return null
        }

        return (
            <Credentials
                institution={institution}
                member={member}
                onUpdateMember={this.onUpdateMember}
                onCompletedMember={this.onCompletedMember} />
        )
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
                    value="Your account has not been activated to add bank." />
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
                        
                    </div>
                </div>
            </div>
        )
    }
}


AddBank.propTypes = {
    growlAdd: PropTypes.func,
    user: PropTypes.object
}

const mapStateToProps = (state) => ({
    user: state.user.item
})

export default connect(mapStateToProps, {
    growlAdd
})(AddBank)
