import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import { Input2 } from 'components'


class ChangePassword extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }

    render(){
        const { errors, user } = this.props

        return (
            <div className="card">

                <form className="form-horizontal">
                    <div className="card-header">
                        <h2>{'Change password'}</h2>
                    </div>

                    <div className="card-body card-padding">
                        <Input2
                            col1="col-sm-4"
                            col2="col-sm-8"
                            name="old_password"
                            placeholder="Old password"
                            label="Old password"
                            type="password"
                            errors={errors} />

                        <Input2
                            col1="col-sm-4"
                            col2="col-sm-8"
                            name="password1"
                            placeholder="New password"
                            label="New password"
                            type="password"
                            errors={errors} />

                        <Input2
                            col1="col-sm-4"
                            col2="col-sm-8"
                            name="password2"
                            placeholder="Confirm new password"
                            label="Confirm"
                            type="password"
                            errors={errors} />

                        <div className="form-group">
                            <div className="col-sm-offset-4 col-sm-8">
                                <button
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


ChangePassword.propTypes = {
    errors: PropTypes.object,
    user: PropTypes.object
}

const mapStateToProps = (state) => ({
    errors: state.formErrors.editProfile,
    user: state.user.item
})

export default connect(mapStateToProps, {

})(ChangePassword)