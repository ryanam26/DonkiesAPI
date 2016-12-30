import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import { formToObject } from 'services/helpers'
import { changeEmail, setFormErrors } from 'actions' 
import { Input2, Button2 } from 'components'


class ChangeEmail extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }

    componentWillReceiveProps(nextProps){
        if (this.props.triggerChangeEmail !== nextProps.triggerChangeEmail){
            this.refs.form.reset()
        }
    }

    onSubmit(e){
        e.preventDefault()
        this.props.setFormErrors('clear', null)

        const form = formToObject(e.target)
        this.props.changeEmail(form)
    }

    render(){
        const { errors, inProgress, user } = this.props

        return (
            <div className="card">

                <form ref="form" onSubmit={this.onSubmit} className="form-horizontal">
                    <div className="card-header">
                        <h2>{'Change email'}</h2>
                    </div>

                    <div className="card-body card-padding">
                        <Input2
                            name="new_email"
                            placeholder="Input new email"
                            label="New email"
                            errors={errors} />
                        
                        <Button2 disabled={inProgress} />
                    </div>
                </form>
            </div>
        )
    }
}


ChangeEmail.propTypes = {
    changeEmail: PropTypes.func,
    errors: PropTypes.object,
    inProgress: PropTypes.bool,
    setFormErrors: PropTypes.func,
    triggerChangeEmail: PropTypes.number,
    user: PropTypes.object
}

const mapStateToProps = (state) => ({
    errors: state.formErrors.changeEmail,
    inProgress: state.user.isSubmittingChangeEmail,
    triggerChangeEmail: state.user.triggerChangeEmail,
    user: state.user.item
})

export default connect(mapStateToProps, {
    changeEmail,
    setFormErrors
})(ChangeEmail)