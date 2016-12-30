import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import { INSTITUTIONS_URL, INSTITUTIONS_SUGGEST_URL, apiCall2 } from 'services/api'
import { InputAutocompleteAsync, Button2 } from 'components'


/**
 * First step of add bank form: select institution.
 */
export default class Institution extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }

    /**
     * From autocomplete we have only id and name of institution.
     * As soon as user have chosen institution,
     * request server for full object.
     */
    async onChooseInstitution(){
        const { institution } = this.props
        const url = INSTITUTIONS_URL + '/' + institution.id

        let response = await apiCall2(url, true) 
        let newInstitution = await response.json()

        this.props.onChooseInstitution(newInstitution)
    }

    render(){
        const {
            institution,
            isInstitutionChosen,
            onChooseInstitution,
            onFailInstitution,
            onSelectInstitution } = this.props

        return (
            <wrap>
                {!isInstitutionChosen ?
                    <wrap>
                        <div className="form-group">
                        
                            <label className="control-label col-sm-4">{'Bank'}</label>
                            <div className="col-sm-8">
                                <div className="fg-line">

                                    <InputAutocompleteAsync
                                        onSuccess={this.props.onSelectInstitution}
                                        onFail={this.props.onFailInstitution}
                                        name="institution"
                                        placeholder="Bank name"
                                        url={INSTITUTIONS_SUGGEST_URL} />
                                </div>
                            </div>
                        </div>
                        
                        {institution && 
                            <Button2
                                type="button"
                                text="next"
                                onClick={this.onChooseInstitution} />
                        }
                        
                    </wrap>
                :
                    <p>{'Bank: '}{institution.name}</p>
                }
            </wrap>
        )
    }
}


Institution.propTypes = {
    institution: PropTypes.object,
    isInstitutionChosen: PropTypes.bool,
    onChooseInstitution: PropTypes.func,
    onFailInstitution: PropTypes.func,
    onSelectInstitution: PropTypes.func,
}

