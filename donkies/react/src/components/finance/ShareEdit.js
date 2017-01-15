import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import { apiGetRequest } from 'actions'
import { apiCall4, ACCOUNTS_EDIT_SHARE_URL } from 'services/api'
import { formToObject, getArraySum, isInteger } from 'services/helpers'


/**
 * Edit transfer_share of debt accounts.
 */ 
class ShareEdit extends Component{
    constructor(props){
        super(props)
        autoBind(this)

        this.state = {
            error: null,
            success: null,
            isProcessing: false
        }
    }

    /**
     * 1) All values in form should be integer.
     * 2) The sum of all values should be equal to 100.
     * Returns error or null if no error.
     */
    checkValues(form){
        for (let value of Object.values(form)){
            if (!isInteger(value)){
                return 'Please input only integer numbers.'
            }
        }
        
        let values = Object.values(form).map((num) => parseInt(num))

        if (getArraySum(values) !== 100){
            return 'The total sum of all share should be equal 100.'
        }
        return null
    }

    /**
     * Disable space.
     */
    onKeyDown(e){
        if (e.keyCode === 32){
            e.preventDefault()
        }
    }
    
    onChange(){
        this.setState({error: null, success: null})

        let form = this.refs.form
        form = formToObject(form)
        let error = this.checkValues(form)
        if (error !== null){
            this.setState({error: error})
            return
        } 
        this.submitRequest(form)
    }

    async submitRequest(data){
        this.setState({isProcessing: true})
        const url = ACCOUNTS_EDIT_SHARE_URL

        let response = await apiCall4(url, data, true) 
        if (response.status === 200){
            // Update accounts in Redux state
            this.setState({success: 'Saved!'})
            this.props.apiGetRequest('accounts')
        } else {
            this.setState({error: 'Server error.'})
        }

        this.setState({isProcessing: false})
    }

    render(){
        const { accounts } = this.props
        const { error, success, isProcessing } = this.state

        return (
            <form ref="form">
            <div className="table-responsive">
                <table className="table table-condensed table-vmiddle">
                    <tbody>
                        {accounts.map((account, index) => {
                            return (
                                <tr key={index}>
                                    <td>{account.name}</td>
                                    <td>
                                        <input
                                            disabled={isProcessing}
                                            autoComplete="off"
                                            onKeyDown={this.onKeyDown}
                                            onChange={this.onChange}
                                            className="form-control input-sm"
                                            type="text"
                                            name={`id${account.id}`}
                                            defaultValue={account.transfer_share} />
                                    </td>
                                </tr>
                            )           
                        })}

                        <tr>
                            <td colSpan="2" className="text-right">
                                {error && 
                                    <div className="custom-error">{error}</div>}
                                
                                {success &&
                                    <div className="custom-success">{success}</div>}
                            </td>
                        </tr>


                    </tbody>
                </table>
            </div>
            </form>
        )
    }
}


ShareEdit.propTypes = {
    accounts: PropTypes.array,
    apiGetRequest: PropTypes.func
}

const mapStateToProps = (state) => ({
})

export default connect(mapStateToProps, {
    apiGetRequest
})(ShareEdit)