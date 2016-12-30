import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import { INSTITUTIONS_SUGGEST_URL } from 'services/api'
import { InputAutocompleteAsync, Button2 } from 'components'


/**
 * First step of add bank form: select institution.
 */
export default class Institution extends Component{
    constructor(props){
        super(props)
        autoBind(this)
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
                                onClick={this.props.onChooseInstitution} />
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

