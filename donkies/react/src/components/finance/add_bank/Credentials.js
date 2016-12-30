import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import { apiCall2, apiCall3, CREDENTIALS_BY_ID_URL, MEMBERS_URL } from 'services/api'
import { formToObject } from 'services/helpers'
import { Button2, Input2, LoadingInline } from 'components'


/**
 * Second step of add bank form.
 * On init fetches credentials for institution.
 * Then user submit credentials.
 * Then fetches server until it get completed status of member
 * and send callback to parent with updated status.
 *
 * @param {object} institution: {id: ..., name: ...}
 * @param {func} onUpdateMemberStatus
 *
 * Flow:
 * 1) Fetch credentials (on mount)
 * 2) Submit credentials to server
 * 3) Request server for every 5 seconds until completed status
 * 4) If error, allow to submit again.
 * 5) If challenged, load challenges.
 * 6) If success - show success message.
 *
 */ 
class Credentials extends Component{
    constructor(props){
        super(props)
        autoBind(this)

        this.state = {
            credentials: null,
            errorSubmit: null
        }
    }

    componentWillMount(){
        this.fetchCredentials()
    }

    /**
     * Fetch from server data to render credentials.
     */
    async fetchCredentials(){
        let { institution } = this.props
        const url = CREDENTIALS_BY_ID_URL + '/' + institution.id

        let response = await apiCall2(url, true) 
        let arr = await response.json()

        this.setState({credentials: arr})
    }

    onSubmit(e){
        e.preventDefault()
        const { institution } = this.props

        this.setState({errorSubmit: null})
        const form = formToObject(e.target)
        const data = {institution_code: institution.code}

        data.credentials = []
        for (let key in form){
            if (key.length === 0){
                continue
            }

            if (form[key].trim().length === 0){
                this.setState({errorSubmit: `Please fill ${key}`})
                return
            }

            let obj = {field_name: key, value: form[key].trim()}
            data.credentials.push(obj)
        }

        this.submitCredentials(data)
    }

    /**
     * Submit to server user's filled credentials.
     * (create member)
     */
    async submitCredentials(data){
        let response = await apiCall3(MEMBERS_URL, data, true) 
        let member = await response.json()
        console.log(member)
    }


    render(){
        const { credentials, errorSubmit } = this.state

        if (!credentials){
            return <LoadingInline />
        }

        return (
            <form onSubmit={this.onSubmit}>
                {credentials.map((obj, index) => {
                    const type = obj.type.toLowerCase() === 'password' ? 'password' : 'text'
                    return (
                        <Input2
                            key={index}
                            type={type}
                            name={obj.field_name}
                            label={obj.label}
                            placeholder={obj.label} />
                    )                                
                })}
            
                <Button2 />

                {errorSubmit && <p className="custom-errors">{errorSubmit}</p>}

            </form>
        )
    }
}


Credentials.propTypes = {
    institution: PropTypes.object,
    memberStatus: PropTypes.string,
    onUpdateMemberStatus: PropTypes.func

}

const mapStateToProps = (state) => ({
})

export default connect(mapStateToProps, {
})(Credentials)