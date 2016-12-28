import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import { formToObject } from 'services/helpers'
import { changePassword, setFormErrors } from 'actions' 
import { Input2 } from 'components'



class ChangePassword extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }

    componentWillReceiveProps(nextProps){
        if (this.props.triggerChangePassword !== nextProps.triggerChangePassword){
            this.refs.form.reset()
        }
    }

    onSubmit(e){
        e.preventDefault()
        this.props.setFormErrors('clear', null)

        const form = formToObject(e.target)
        this.props.changePassword(form)
    }


    render(){
        const { errors, inProgress, user } = this.props

        return (
            <div className="card">

                <form ref="form" onSubmit={this.onSubmit} className="form-horizontal">
                    <div className="card-header">
                        <h2>{'Change password'}</h2>
                    </div>

                    <div className="card-body card-padding">
                        <Input2
                            name="current_password"
                            placeholder="Current password"
                            label="Current password"
                            type="password"
                            errors={errors} />

                        <Input2
                            name="new_password1"
                            placeholder="New password"
                            label="New password"
                            type="password"
                            errors={errors} />

                        <Input2
                            name="new_password2"
                            placeholder="Confirm new password"
                            label="Confirm"
                            type="password"
                            errors={errors} />

                        <div className="form-group">
                            <div className="col-sm-offset-4 col-sm-8">
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


ChangePassword.propTypes = {
    changePassword: PropTypes.func,
    errors: PropTypes.object,
    inProgress: PropTypes.bool,
    setFormErrors: PropTypes.func,
    triggerChangePassword: PropTypes.number,
    user: PropTypes.object
}

const mapStateToProps = (state) => ({
    errors: state.formErrors.changePassword,
    inProgress: state.user.isSubmittingChangePassword,
    triggerChangePassword: state.user.triggerChangePassword,
    user: state.user.item
})

export default connect(mapStateToProps, {
    changePassword,
    setFormErrors
})(ChangePassword)