import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import {CREDENTIALS_URL, apiCall2} from 'services/api'
import Institution from './Institution'
import Credentials from './Credentials'


/**
 * Main component that controls adding bank account.
 * Flow: 
 * 1) Select institution and set it to state (it also is set in input element)
 * 2) Fetch credentials for institution.
 * 3) Submit credentials to server.
 * 4) Wait for member status.
 * 5) If member has completed status - show message.
 * 6) If status is challenged, fetch challenges and resume member.
 * 7) Wait for status again.
 * 8) If member has completed status - show message.
 */
class AddBank extends Component{
    constructor(props){
        super(props)
        autoBind(this)

        this.state = {
            institution: null,
            isInstitutionChosen: false,
            memberStatus: null
        }
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
    onChooseInstitution(){
        this.setState({isInstitutionChosen: true})
    }

    /**
     * Receives member status.
     */ 
    onUpdateMemberStatus(status){
        this.setState({memberStatus: status})
    }

    renderCredentials(){
        const { institution, memberStatus, isInstitutionChosen } = this.state
        if (!isInstitutionChosen){
            return null
        }

        return (
            <Credentials
                institution={institution}
                memberStatus={memberStatus}
                onUpdateMemberStatus={this.onUpdateMemberStatus} />
        )
    }

    render(){
        const { institution, isInstitutionChosen } = this.state

        return (
            <div className="card col-lg-6">

                <form ref="form" onSubmit={this.onSubmit} className="form-horizontal">
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
                </form>
            </div>
        )
    }
}


AddBank.propTypes = {
    
}

const mapStateToProps = (state) => ({
})

export default connect(mapStateToProps, {

})(AddBank)
