import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import { Link } from 'react-router'
import classNames from 'classnames'
import autoBind from 'react-autobind'
import { apiCall3, CHANGE_EMAIL_CONFIRM_URL } from 'services/api'
import { Loading } from 'components'


export default class ChangeEmailConfirm extends Component{
    constructor(props){
        super(props)
        autoBind(this)

        this.state = {
            isError: false,
            message: null
        }
    }

    componentWillMount(){
        const q = this.props.location.query  
        if (!q.hasOwnProperty('id') || !q.hasOwnProperty('token')){
            this.setState({
                isError: true,
                message: 'Incorrect url'
            })
            return
        }
        const form = {id: q.id, token: q.token}
        this.sendForm(form)
    }

    async sendForm(form){
        const url = `${CHANGE_EMAIL_CONFIRM_URL}/${form.id}/${form.token}`  
        const data = {}
        let response = await apiCall3(url, data, false)
        const result = await response.json()
        if (response.status === 400){
            this.setState({
                isError: true,
                message: result.non_field_errors
            })
        } else if (response.status === 200){
            this.setState({
                message: result.message
            })
        }
    }

    renderResult(){
        let { isError, message } = this.state
        const cn = classNames(
            'error-title',
            {red: isError, green: !isError}
        )

        return (
            <wrap>
                <div className={cn}>{message}</div>
                <Link to="/" className="btn btn-rounded">{'Home page'}</Link>
            </wrap>
        )
        
    }

    render(){
        const { error, message } = this.state
        return (
            <div className="page-center">
                <div className="page-center-in">
                    <div className="container-fluid">

                        <div className="page-error-box">
                            {!message ? <Loading /> : this.renderResult() }
                        </div>
                    </div>
                </div>
            </div>
        )
    }
}


ChangeEmailConfirm.propTypes = {
    location: PropTypes.object
}
