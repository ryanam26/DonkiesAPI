import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import { apiCall2, CREDENTIALS_BY_ID_URL } from 'services/api'
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
            credentials: null
        }
    }

    componentWillMount(){
        this.fetchCredentials()
    }

    /**
     * Renders input components using data received by API.
     */
    renderCredentials(){

    }

    async fetchCredentials(){
        let { institution } = this.props
        const url = CREDENTIALS_BY_ID_URL + '/' + institution.id

        let response = await apiCall2(url, true) 
        let arr = await response.json()

        this.setState({credentials: arr})
       
    }

    onSubmit(e){

    }

    render(){
        const { credentials } = this.state

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