import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import Institution from './Institution'
import Credentials from './Credentials'


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

                        <Credentials
                            institution={institution}
                            onUpdateMemberStatus={this.onUpdateMemberStatus} />
                        
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

/*
<Input2
    name="test"
    placeholder=""
    label=""
    errors={errors} />
*/