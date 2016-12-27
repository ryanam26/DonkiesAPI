import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import { formToObject } from 'services/helpers'
import { apiGetRequest, editProfile, setFormErrors } from 'actions'
import { Input2 } from 'components'


class EditProfile extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }

    componentWillReceiveProps(nextProps){
        // Update user in Redux state.
        if (this.props.triggerEditProfile !== nextProps.triggerEditProfile){
            this.props.apiGetRequest('user')
        }
    }   

    onSubmit(e){
        e.preventDefault()
        this.props.setFormErrors('clear', null)

        const form = formToObject(e.target)
        this.props.editProfile(form)
    }

    render(){
        const { errors, inProgress, user } = this.props

        return (
            <div className="card">

                <form onSubmit={this.onSubmit} className="form-horizontal">
                    <div className="card-header">
                        <h2>{'Edit user profile'}
                            <small>{'some description'}</small></h2>
                    </div>

                    <div className="card-body card-padding">
                        <Input2
                            name="first_name"
                            placeholder="First Name"
                            label="First Name"
                            value={user.first_name}
                            errors={errors} />

                        <Input2
                            name="last_name"
                            placeholder="Last Name"
                            label="Last Name"
                            value={user.last_name}
                            errors={errors} />

                        <Input2
                            name="phone"
                            placeholder="Phone"
                            label="Phone"
                            value={user.phone}
                            errors={errors} />

                        <Input2
                            name="address1"
                            placeholder="Address line1 (max. length 50)"
                            label="Address1"
                            value={user.address1}
                            errors={errors} />

                        <Input2
                            name="address2"
                            placeholder="Address line2 (max. length 50)"
                            label="Address2"
                            value={user.address2}
                            errors={errors} />

                        <Input2
                            name="city"
                            placeholder="City"
                            label="City"
                            value={user.city}
                            errors={errors} />

                        <Input2
                            name="state"
                            placeholder="State"
                            label="State"
                            value={user.state}
                            errors={errors} />

                        <Input2
                            name="postal_code"
                            placeholder="Postal Code"
                            label="Postal Code"
                            value={user.postal_code}
                            errors={errors} />

                        <Input2
                            name="date_of_birth"
                            placeholder="Date Of Birth"
                            label="Date Of Birth"
                            value={user.date_of_birth}
                            errors={errors} />

                        <Input2
                            name="ssn"
                            placeholder="SSN"
                            label="SSN"
                            value={user.ssn}
                            errors={errors} />
                        
                        <div className="form-group">
                            <div className="col-sm-offset-2 col-sm-10">
                                <button
                                    disabled={inProgress}
                                    type="submit"
                                    className="btn btn-primary btn-sm waves-effect">
                                
                                    {'Submit'}
                                </button>
                            </div>
                        </div>
                    </div>
                </form>
            </div>
        )
    }
}


EditProfile.propTypes = {
    apiGetRequest: PropTypes.func,
    editProfile: PropTypes.func,
    errors: PropTypes.object,
    inProgress: PropTypes.bool,
    setFormErrors: PropTypes.func,
    triggerEditProfile: PropTypes.number,
    user: PropTypes.object
}

const mapStateToProps = (state) => ({
    errors: state.formErrors.editProfile,
    inProgress: state.user.isSubmittingEditProfile,
    triggerEditProfile: state.user.triggerEditProfile,
    user: state.user.item
})

export default connect(mapStateToProps, {
    apiGetRequest,
    editProfile,
    setFormErrors
})(EditProfile)